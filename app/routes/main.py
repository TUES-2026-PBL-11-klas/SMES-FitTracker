"""
Main routes for FitTracker application.

Demonstrates:
- Context managers (Python equivalent of try-with-resources)
- Custom exception handling
- Dependency Injection via WorkoutService
"""

import logging
import re
import urllib.request
import urllib.parse
import json
from datetime import date, timedelta
from flask import Blueprint, render_template, redirect, url_for, jsonify, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import WorkoutPlan, WorkoutDay, WorkoutExercise, FoodEntry
from app.services import WorkoutService
from app.strategies import StrategyFactory
from app.exceptions import (
    FitTrackerError,
    InvalidProfileError,
    WorkoutGenerationError,
    UnauthorizedAccessError,
)

logger = logging.getLogger(__name__)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    return render_template("dashboard.html", plan=plan)


@main_bp.route("/workout")
@login_required
def workout():
    plan = WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).first()
    if not plan:
        return redirect(url_for("main.workout_regenerate"))
    return render_template("workout.html", plan=plan)


@main_bp.route("/workout/regenerate")
@login_required
def workout_regenerate():
    try:
        # Dependency Injection: create strategy via factory, inject into service
        strategy = StrategyFactory.create(current_user.fitness_goal)
        service = WorkoutService(strategy=strategy)
        plan_data = service.generate_plan(current_user)
    except InvalidProfileError as e:
        logger.error("Profile error for user %s: %s", current_user.username, e)
        flash(f"Please complete your profile: {e.message}", "warning")
        return redirect(url_for("main.dashboard"))
    except WorkoutGenerationError as e:
        logger.error("Generation error: %s", e)
        flash("Could not generate workout plan. Please try again.", "danger")
        return redirect(url_for("main.dashboard"))
    except FitTrackerError as e:
        logger.error("Unexpected error: %s", e)
        flash("An unexpected error occurred.", "danger")
        return redirect(url_for("main.dashboard"))

    # Deactivate old plans using context manager pattern for DB transaction
    try:
        WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).update(
            {"is_active": False}
        )

        plan = WorkoutPlan(
            user_id=current_user.id,
            split_name=plan_data["split_name"],
            goal=plan_data["goal"],
            days_per_week=plan_data["days_per_week"],
            rest_between_sets=plan_data["rest_between_sets"],
        )
        db.session.add(plan)
        db.session.flush()

        for i, day_data in enumerate(plan_data["days"]):
            day = WorkoutDay(
                plan_id=plan.id,
                day_index=i,
                day_name=day_data["day_name"],
                is_rest=day_data["is_rest"],
                workout_name=day_data["workout_name"],
            )
            db.session.add(day)
            db.session.flush()

            for j, ex_data in enumerate(day_data["exercises"]):
                exercise = WorkoutExercise(
                    day_id=day.id,
                    order=j,
                    name=ex_data["name"],
                    is_cardio=ex_data.get("is_cardio", False),
                    muscle_group=ex_data.get("muscle_group"),
                    sets=ex_data.get("sets"),
                    reps=ex_data.get("reps"),
                    duration_min=ex_data.get("duration_min"),
                )
                db.session.add(exercise)

        db.session.commit()
        logger.info("Generated new plan for user %s", current_user.username)
    except Exception as e:
        db.session.rollback()
        logger.error("Database error saving plan: %s", e)
        flash("Error saving workout plan.", "danger")
        return redirect(url_for("main.dashboard"))

    return redirect(url_for("main.workout"))


@main_bp.route("/workout/toggle/<int:exercise_id>", methods=["POST"])
@login_required
def toggle_exercise(exercise_id):
    try:
        exercise = WorkoutExercise.query.get_or_404(exercise_id)

        # Custom exception for authorization check
        if exercise.day.plan.user_id != current_user.id:
            raise UnauthorizedAccessError("exercise")

        exercise.is_completed = not exercise.is_completed
        db.session.commit()

        day = exercise.day
        # Using sum() with generator expression (Python Stream.count equivalent)
        total = len(day.exercises)
        done = sum(1 for e in day.exercises if e.is_completed)

        return jsonify({
            "completed": exercise.is_completed,
            "day_total": total,
            "day_done": done,
        })

    except UnauthorizedAccessError:
        return jsonify({"error": "Unauthorized"}), 403


@main_bp.route("/workout/reset-day/<int:day_id>", methods=["POST"])
@login_required
def reset_day(day_id):
    day = WorkoutDay.query.get_or_404(day_id)

    if day.plan.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    # Using list comprehension for batch update
    for ex in day.exercises:
        ex.is_completed = False
    db.session.commit()

    return jsonify({"success": True})


@main_bp.route("/workout/history")
@login_required
def workout_history():
    # Using SQLAlchemy query with chaining (similar to Stream pipeline)
    plans = (WorkoutPlan.query
             .filter_by(user_id=current_user.id)
             .order_by(WorkoutPlan.created_at.desc())
             .all())
    return render_template("workout_history.html", plans=plans)


# ─── BMI Calculator ─────────────────────────────────────────────────


@main_bp.route("/bmi", methods=["GET", "POST"])
@login_required
def bmi():
    """BMI calculator — uses profile data or manual input."""
    result = None

    if request.method == "POST":
        height = request.form.get("height", type=float)
        weight = request.form.get("weight", type=float)

        if not height or not weight or height <= 0 or weight <= 0:
            flash("Enter valid height and weight.", "warning")
            return redirect(url_for("main.bmi"))

        height_m = height / 100
        bmi_value = round(weight / (height_m ** 2), 1)

        if bmi_value < 18.5:
            category = "Underweight"
        elif bmi_value < 25:
            category = "Normal"
        elif bmi_value < 30:
            category = "Overweight"
        else:
            category = "Obese"

        result = {
            "bmi": bmi_value,
            "category": category,
            "height": height,
            "weight": weight,
        }

    return render_template(
        "bmi.html",
        result=result,
        user_height=current_user.height_cm,
        user_weight=current_user.weight_kg,
    )


# ─── Calories Tracker ────────────────────────────────────────────────


@main_bp.route("/calories")
@login_required
def calories():
    """Show today's calorie tracker with food log."""
    selected = request.args.get("date")
    if selected:
        try:
            view_date = date.fromisoformat(selected)
        except ValueError:
            view_date = date.today()
    else:
        view_date = date.today()

    entries = (FoodEntry.query
               .filter_by(user_id=current_user.id, date=view_date)
               .order_by(FoodEntry.created_at.asc())
               .all())

    # Group entries by meal type
    meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for entry in entries:
        meals.setdefault(entry.meal_type, []).append(entry)

    # Daily totals using generator expressions
    total_cal = sum(e.calories for e in entries)
    total_protein = sum(e.protein_g or 0 for e in entries)
    total_carbs = sum(e.carbs_g or 0 for e in entries)
    total_fat = sum(e.fat_g or 0 for e in entries)

    target = current_user.daily_calories or 2000

    # Weekly data for chart (last 7 days)
    week_data = []
    for i in range(6, -1, -1):
        d = view_date - timedelta(days=i)
        day_entries = (FoodEntry.query
                       .filter_by(user_id=current_user.id, date=d)
                       .all())
        day_cal = sum(e.calories for e in day_entries)
        week_data.append({"date": d, "calories": day_cal})

    return render_template(
        "calories.html",
        view_date=view_date,
        today=date.today(),
        prev_date=(view_date - timedelta(days=1)).isoformat(),
        next_date=(view_date + timedelta(days=1)).isoformat(),
        meals=meals,
        entries=entries,
        total_cal=total_cal,
        total_protein=round(total_protein, 1),
        total_carbs=round(total_carbs, 1),
        total_fat=round(total_fat, 1),
        target=target,
        week_data=week_data,
    )


@main_bp.route("/calories/add", methods=["POST"])
@login_required
def calories_add():
    """Add a food entry."""
    selected = request.form.get("date", date.today().isoformat())
    try:
        entry_date = date.fromisoformat(selected)
    except ValueError:
        entry_date = date.today()

    name = request.form.get("name", "").strip()
    calories_val = request.form.get("calories", 0, type=int)
    meal_type = request.form.get("meal_type", "snack")

    if not name or calories_val <= 0:
        flash("Enter a valid food name and calorie amount.", "warning")
        return redirect(url_for("main.calories", date=selected))

    entry = FoodEntry(
        user_id=current_user.id,
        date=entry_date,
        meal_type=meal_type,
        name=name,
        calories=calories_val,
        protein_g=request.form.get("protein", 0, type=float),
        carbs_g=request.form.get("carbs", 0, type=float),
        fat_g=request.form.get("fat", 0, type=float),
    )
    db.session.add(entry)
    db.session.commit()
    logger.info("User %s logged food: %s (%d kcal)", current_user.username, name, calories_val)

    return redirect(url_for("main.calories", date=selected))


@main_bp.route("/calories/delete/<int:entry_id>", methods=["POST"])
@login_required
def calories_delete(entry_id):
    """Delete a food entry."""
    entry = FoodEntry.query.get_or_404(entry_id)

    if entry.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    entry_date = entry.date.isoformat()
    db.session.delete(entry)
    db.session.commit()

    return redirect(url_for("main.calories", date=entry_date))


# Built-in nutrition database (per 100g) — fallback when API is unavailable
NUTRITION_DB = {
    "chicken breast": {"cal": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6},
    "chicken": {"cal": 239, "protein": 27.3, "carbs": 0.0, "fat": 13.6},
    "chicken thigh": {"cal": 209, "protein": 26.0, "carbs": 0.0, "fat": 10.9},
    "beef": {"cal": 250, "protein": 26.0, "carbs": 0.0, "fat": 15.0},
    "ground beef": {"cal": 332, "protein": 14.0, "carbs": 0.0, "fat": 30.0},
    "steak": {"cal": 271, "protein": 26.0, "carbs": 0.0, "fat": 18.0},
    "pork": {"cal": 242, "protein": 27.3, "carbs": 0.0, "fat": 14.0},
    "salmon": {"cal": 208, "protein": 20.0, "carbs": 0.0, "fat": 13.0},
    "tuna": {"cal": 130, "protein": 29.0, "carbs": 0.0, "fat": 1.0},
    "shrimp": {"cal": 85, "protein": 20.0, "carbs": 0.0, "fat": 0.5},
    "egg": {"cal": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0},
    "eggs": {"cal": 155, "protein": 13.0, "carbs": 1.1, "fat": 11.0},
    "rice": {"cal": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3},
    "white rice": {"cal": 130, "protein": 2.7, "carbs": 28.0, "fat": 0.3},
    "brown rice": {"cal": 112, "protein": 2.3, "carbs": 24.0, "fat": 0.8},
    "pasta": {"cal": 131, "protein": 5.0, "carbs": 25.0, "fat": 1.1},
    "spaghetti": {"cal": 131, "protein": 5.0, "carbs": 25.0, "fat": 1.1},
    "bread": {"cal": 265, "protein": 9.0, "carbs": 49.0, "fat": 3.2},
    "oatmeal": {"cal": 68, "protein": 2.5, "carbs": 12.0, "fat": 1.4},
    "oats": {"cal": 389, "protein": 16.9, "carbs": 66.0, "fat": 6.9},
    "potato": {"cal": 77, "protein": 2.0, "carbs": 17.0, "fat": 0.1},
    "sweet potato": {"cal": 86, "protein": 1.6, "carbs": 20.0, "fat": 0.1},
    "banana": {"cal": 89, "protein": 1.1, "carbs": 23.0, "fat": 0.3},
    "apple": {"cal": 52, "protein": 0.3, "carbs": 14.0, "fat": 0.2},
    "orange": {"cal": 47, "protein": 0.9, "carbs": 12.0, "fat": 0.1},
    "strawberry": {"cal": 32, "protein": 0.7, "carbs": 7.7, "fat": 0.3},
    "blueberry": {"cal": 57, "protein": 0.7, "carbs": 14.0, "fat": 0.3},
    "berries": {"cal": 57, "protein": 0.7, "carbs": 14.0, "fat": 0.3},
    "avocado": {"cal": 160, "protein": 2.0, "carbs": 9.0, "fat": 15.0},
    "milk": {"cal": 42, "protein": 3.4, "carbs": 5.0, "fat": 1.0},
    "yogurt": {"cal": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4},
    "greek yogurt": {"cal": 59, "protein": 10.0, "carbs": 3.6, "fat": 0.4},
    "cheese": {"cal": 402, "protein": 25.0, "carbs": 1.3, "fat": 33.0},
    "butter": {"cal": 717, "protein": 0.9, "carbs": 0.1, "fat": 81.0},
    "olive oil": {"cal": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0},
    "peanut butter": {"cal": 588, "protein": 25.0, "carbs": 20.0, "fat": 50.0},
    "almonds": {"cal": 579, "protein": 21.0, "carbs": 22.0, "fat": 49.0},
    "walnuts": {"cal": 654, "protein": 15.0, "carbs": 14.0, "fat": 65.0},
    "broccoli": {"cal": 34, "protein": 2.8, "carbs": 7.0, "fat": 0.4},
    "spinach": {"cal": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4},
    "carrot": {"cal": 41, "protein": 0.9, "carbs": 10.0, "fat": 0.2},
    "tomato": {"cal": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2},
    "cucumber": {"cal": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1},
    "salad": {"cal": 20, "protein": 1.5, "carbs": 3.0, "fat": 0.3},
    "pizza": {"cal": 266, "protein": 11.0, "carbs": 33.0, "fat": 10.0},
    "hamburger": {"cal": 295, "protein": 17.0, "carbs": 24.0, "fat": 14.0},
    "french fries": {"cal": 312, "protein": 3.4, "carbs": 41.0, "fat": 15.0},
    "ice cream": {"cal": 207, "protein": 3.5, "carbs": 24.0, "fat": 11.0},
    "chocolate": {"cal": 546, "protein": 5.0, "carbs": 60.0, "fat": 31.0},
    "protein shake": {"cal": 113, "protein": 24.0, "carbs": 4.0, "fat": 1.0},
    "whey protein": {"cal": 400, "protein": 80.0, "carbs": 10.0, "fat": 5.0},
    "tofu": {"cal": 76, "protein": 8.0, "carbs": 1.9, "fat": 4.8},
    "lentils": {"cal": 116, "protein": 9.0, "carbs": 20.0, "fat": 0.4},
    "chickpeas": {"cal": 164, "protein": 8.9, "carbs": 27.0, "fat": 2.6},
    "beans": {"cal": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5},
    "corn": {"cal": 86, "protein": 3.3, "carbs": 19.0, "fat": 1.2},
    "turkey": {"cal": 189, "protein": 29.0, "carbs": 0.0, "fat": 7.0},
    "bacon": {"cal": 541, "protein": 37.0, "carbs": 1.4, "fat": 42.0},
    "sausage": {"cal": 301, "protein": 12.0, "carbs": 2.0, "fat": 27.0},
    "hot dog": {"cal": 290, "protein": 10.0, "carbs": 18.0, "fat": 20.0},
}


def _lookup_local(search_query, scale):
    """Try to match query against built-in nutrition database."""
    query_lower = search_query.lower().strip()
    # Try exact match first
    if query_lower in NUTRITION_DB:
        info = NUTRITION_DB[query_lower]
        return {
            "name": query_lower.title(),
            "calories": round(info["cal"] * scale),
            "protein": round(info["protein"] * scale, 1),
            "carbs": round(info["carbs"] * scale, 1),
            "fat": round(info["fat"] * scale, 1),
            "serving": f"{round(100 * scale)}g",
        }
    # Try partial match — find longest matching key
    best = None
    for key in NUTRITION_DB:
        if key in query_lower or query_lower in key:
            if best is None or len(key) > len(best):
                best = key
    if best:
        info = NUTRITION_DB[best]
        return {
            "name": best.title(),
            "calories": round(info["cal"] * scale),
            "protein": round(info["protein"] * scale, 1),
            "carbs": round(info["carbs"] * scale, 1),
            "fat": round(info["fat"] * scale, 1),
            "serving": f"{round(100 * scale)}g",
        }
    return None


@main_bp.route("/calories/lookup", methods=["POST"])
@login_required
def calories_lookup():
    """Look up nutrition info via USDA API with local DB fallback."""
    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"error": "Empty query"}), 400

    # Extract gram amount (e.g. "200g chicken breast" → scale=2.0)
    grams_match = re.search(r"(\d+)\s*g\b", query.lower())
    scale = 1.0
    if grams_match:
        scale = int(grams_match.group(1)) / 100.0

    # Strip quantity/units from query so search finds the right food
    search_query = re.sub(r"\d+\s*g\b", "", query).strip()
    if not search_query:
        search_query = query

    # Try USDA FoodData Central API first
    try:
        api_url = (
            "https://api.nal.usda.gov/fdc/v1/foods/search?query="
            + urllib.parse.quote(search_query)
            + "&pageSize=3&api_key=DEMO_KEY"
        )
        req = urllib.request.Request(api_url)

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        foods = data.get("foods", [])
        if foods:
            # Pick the first result that has Energy data
            food = None
            nutrients = {}
            for candidate in foods:
                candidate_nutrients = {
                    n["nutrientName"]: n.get("value", 0)
                    for n in candidate.get("foodNutrients", [])
                }
                if candidate_nutrients.get("Energy", 0) > 0:
                    food = candidate
                    nutrients = candidate_nutrients
                    break

            if food is None:
                food = foods[0]
                nutrients = {
                    n["nutrientName"]: n.get("value", 0)
                    for n in food.get("foodNutrients", [])
                }

            calories = round(nutrients.get("Energy", 0))
            protein = round(nutrients.get("Protein", 0), 1)
            carbs = round(nutrients.get("Carbohydrate, by difference", 0), 1)
            fat = round(nutrients.get("Total lipid (fat)", 0), 1)

            return jsonify({
                "name": food.get("description", query).title(),
                "calories": round(calories * scale),
                "protein": round(protein * scale, 1),
                "carbs": round(carbs * scale, 1),
                "fat": round(fat * scale, 1),
                "serving": f"{round(100 * scale)}g",
            })

    except Exception as e:
        logger.warning("USDA API unavailable: %s — using local database", e)

    # Fallback: built-in nutrition database
    local_result = _lookup_local(search_query, scale)
    if local_result:
        return jsonify(local_result)

    return jsonify({"error": "Food not found"}), 404
