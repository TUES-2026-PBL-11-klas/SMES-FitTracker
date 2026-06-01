import random

EXERCISES = {
    "chest": [
        {"name": "Bench Press", "type": "strength", "level": 1},
        {"name": "Incline Dumbbell Press", "type": "strength", "level": 2},
        {"name": "Push-Ups", "type": "strength", "level": 0},
        {"name": "Cable Flyes", "type": "strength", "level": 2},
        {"name": "Dips (Chest)", "type": "strength", "level": 1},
    ],
    "back": [
        {"name": "Pull-Ups", "type": "strength", "level": 1},
        {"name": "Barbell Rows", "type": "strength", "level": 1},
        {"name": "Lat Pulldown", "type": "strength", "level": 0},
        {"name": "Seated Cable Row", "type": "strength", "level": 1},
        {"name": "Deadlift", "type": "strength", "level": 2},
    ],
    "shoulders": [
        {"name": "Overhead Press", "type": "strength", "level": 1},
        {"name": "Lateral Raises", "type": "strength", "level": 0},
        {"name": "Face Pulls", "type": "strength", "level": 0},
        {"name": "Arnold Press", "type": "strength", "level": 2},
        {"name": "Front Raises", "type": "strength", "level": 0},
    ],
    "legs": [
        {"name": "Squats", "type": "strength", "level": 1},
        {"name": "Leg Press", "type": "strength", "level": 0},
        {"name": "Romanian Deadlift", "type": "strength", "level": 2},
        {"name": "Lunges", "type": "strength", "level": 0},
        {"name": "Leg Curls", "type": "strength", "level": 0},
        {"name": "Calf Raises", "type": "strength", "level": 0},
    ],
    "arms": [
        {"name": "Bicep Curls", "type": "strength", "level": 0},
        {"name": "Tricep Pushdowns", "type": "strength", "level": 0},
        {"name": "Hammer Curls", "type": "strength", "level": 0},
        {"name": "Skull Crushers", "type": "strength", "level": 1},
        {"name": "Concentration Curls", "type": "strength", "level": 1},
    ],
    "core": [
        {"name": "Plank", "type": "strength", "level": 0},
        {"name": "Crunches", "type": "strength", "level": 0},
        {"name": "Russian Twists", "type": "strength", "level": 0},
        {"name": "Leg Raises", "type": "strength", "level": 1},
        {"name": "Ab Wheel Rollout", "type": "strength", "level": 2},
    ],
    "cardio": [
        {"name": "Running (Treadmill)", "type": "cardio", "level": 0},
        {"name": "Jump Rope", "type": "cardio", "level": 0},
        {"name": "Cycling", "type": "cardio", "level": 0},
        {"name": "Burpees", "type": "cardio", "level": 1},
        {"name": "Mountain Climbers", "type": "cardio", "level": 0},
        {"name": "Rowing Machine", "type": "cardio", "level": 1},
    ],
}

SPLIT_TEMPLATES = {
    3: {
        "name": "Full Body (3 days)",
        "days": [
            {"name": "Full Body A", "groups": ["chest", "back", "legs", "core"]},
            {"name": "Full Body B", "groups": ["shoulders", "legs", "arms", "cardio"]},
            {"name": "Full Body C", "groups": ["chest", "back", "shoulders", "core"]},
        ],
    },
    4: {
        "name": "Upper / Lower (4 days)",
        "days": [
            {"name": "Upper Body A", "groups": ["chest", "back", "shoulders"]},
            {"name": "Lower Body A", "groups": ["legs", "core", "cardio"]},
            {"name": "Upper Body B", "groups": ["chest", "back", "arms"]},
            {"name": "Lower Body B", "groups": ["legs", "shoulders", "core"]},
        ],
    },
    5: {
        "name": "Push / Pull / Legs (5 days)",
        "days": [
            {"name": "Push", "groups": ["chest", "shoulders", "arms"]},
            {"name": "Pull", "groups": ["back", "arms", "core"]},
            {"name": "Legs", "groups": ["legs", "core", "cardio"]},
            {"name": "Upper Body", "groups": ["chest", "back", "shoulders"]},
            {"name": "Lower + Core", "groups": ["legs", "core", "cardio"]},
        ],
    },
    6: {
        "name": "Push / Pull / Legs x2 (6 days)",
        "days": [
            {"name": "Push A", "groups": ["chest", "shoulders", "arms"]},
            {"name": "Pull A", "groups": ["back", "arms", "core"]},
            {"name": "Legs A", "groups": ["legs", "cardio"]},
            {"name": "Push B", "groups": ["chest", "shoulders", "arms"]},
            {"name": "Pull B", "groups": ["back", "arms", "core"]},
            {"name": "Legs B", "groups": ["legs", "core"]},
        ],
    },
}

GOAL_CONFIG = {
    "lose_weight": {
        "sets": (3, 4),
        "reps": (12, 15),
        "rest_sec": 45,
        "cardio_minutes": 25,
        "exercises_per_group": 2,
        "extra_cardio": True,
    },
    "maintain": {
        "sets": (3, 4),
        "reps": (8, 12),
        "rest_sec": 60,
        "cardio_minutes": 15,
        "exercises_per_group": 2,
        "extra_cardio": False,
    },
    "gain_muscle": {
        "sets": (4, 5),
        "reps": (6, 10),
        "rest_sec": 90,
        "cardio_minutes": 10,
        "exercises_per_group": 3,
        "extra_cardio": False,
    },
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _pick_exercises(group, count, max_level):
    pool = [e for e in EXERCISES.get(group, []) if e["level"] <= max_level]
    return random.sample(pool, min(count, len(pool)))


def _get_max_level(activity_level):
    mapping = {"sedentary": 0, "light": 0, "moderate": 1, "active": 2, "very_active": 2}
    return mapping.get(activity_level, 1)


def generate_workout(user):
    days = {"sedentary": 3, "light": 3, "moderate": 4, "active": 5, "very_active": 6}
    num_days = days.get(user.activity_level, 4)

    template = SPLIT_TEMPLATES[num_days]
    config = GOAL_CONFIG.get(user.fitness_goal, GOAL_CONFIG["maintain"])
    max_level = _get_max_level(user.activity_level)

    workout_plan = {
        "split_name": template["name"],
        "goal": user.fitness_goal.replace("_", " ").title(),
        "days_per_week": num_days,
        "rest_between_sets": config["rest_sec"],
        "days": [],
    }

    rest_days = _distribute_rest_days(num_days)

    day_idx = 0
    for i in range(7):
        if i in rest_days:
            workout_plan["days"].append({
                "day_name": DAY_NAMES[i],
                "is_rest": True,
                "workout_name": "Rest Day",
                "exercises": [],
            })
        else:
            day_template = template["days"][day_idx % len(template["days"])]
            exercises = []

            for group in day_template["groups"]:
                if group == "cardio":
                    exercises.append({
                        "name": random.choice(EXERCISES["cardio"])["name"],
                        "is_cardio": True,
                        "duration_min": config["cardio_minutes"],
                    })
                else:
                    picked = _pick_exercises(group, config["exercises_per_group"], max_level)
                    for ex in picked:
                        exercises.append({
                            "name": ex["name"],
                            "is_cardio": False,
                            "sets": random.randint(*config["sets"]),
                            "reps": random.randint(*config["reps"]),
                            "muscle_group": group.title(),
                        })

            if config["extra_cardio"] and not any(e.get("is_cardio") for e in exercises):
                exercises.append({
                    "name": random.choice(EXERCISES["cardio"])["name"],
                    "is_cardio": True,
                    "duration_min": config["cardio_minutes"],
                })

            workout_plan["days"].append({
                "day_name": DAY_NAMES[i],
                "is_rest": False,
                "workout_name": day_template["name"],
                "exercises": exercises,
            })
            day_idx += 1

    return workout_plan


def _distribute_rest_days(num_training_days):
    num_rest = 7 - num_training_days
    if num_rest == 1:
        return {6}
    if num_rest == 2:
        return {3, 6}
    if num_rest == 3:
        return {2, 4, 6}
    return {1, 3, 5, 6}
