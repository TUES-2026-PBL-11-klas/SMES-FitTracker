from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import WorkoutPlan, WorkoutDay, WorkoutExercise
from app.workout_generator import generate_workout

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
    # Deactivate old plans
    WorkoutPlan.query.filter_by(user_id=current_user.id, is_active=True).update(
        {"is_active": False}
    )

    # Generate new plan data
    plan_data = generate_workout(current_user)

    # Save to database
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
    return redirect(url_for("main.workout"))


@main_bp.route("/workout/toggle/<int:exercise_id>", methods=["POST"])
@login_required
def toggle_exercise(exercise_id):
    exercise = WorkoutExercise.query.get_or_404(exercise_id)
    # Verify ownership
    if exercise.day.plan.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    exercise.is_completed = not exercise.is_completed
    db.session.commit()

    # Calculate day progress
    day = exercise.day
    total = len([e for e in day.exercises])
    done = len([e for e in day.exercises if e.is_completed])

    return jsonify({
        "completed": exercise.is_completed,
        "day_total": total,
        "day_done": done,
    })


@main_bp.route("/workout/reset-day/<int:day_id>", methods=["POST"])
@login_required
def reset_day(day_id):
    day = WorkoutDay.query.get_or_404(day_id)
    if day.plan.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    for ex in day.exercises:
        ex.is_completed = False
    db.session.commit()
    return jsonify({"success": True})


@main_bp.route("/workout/history")
@login_required
def workout_history():
    plans = (WorkoutPlan.query
             .filter_by(user_id=current_user.id)
             .order_by(WorkoutPlan.created_at.desc())
             .all())
    return render_template("workout_history.html", plans=plans)
