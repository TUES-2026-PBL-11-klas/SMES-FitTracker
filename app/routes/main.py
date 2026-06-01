"""
Main routes for FitTracker application.

Demonstrates:
- Context managers (Python equivalent of try-with-resources)
- Custom exception handling
- Dependency Injection via WorkoutService
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app import db
from app.models import WorkoutPlan, WorkoutDay, WorkoutExercise
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
