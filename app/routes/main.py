from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from app.workout_generator import generate_workout

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/workout")
@login_required
def workout():
    plan = generate_workout(current_user)
    return render_template("workout.html", plan=plan)


@main_bp.route("/workout/regenerate")
@login_required
def workout_regenerate():
    plan = generate_workout(current_user)
    return render_template("workout.html", plan=plan)
