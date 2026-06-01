import random

EXERCISES = {
    "chest": [
        {"name": "Push-Ups", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Bench Press", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Incline Dumbbell Press", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Cable Flyes", "type": "strength", "level": 1, "joint_friendly": True},
        {"name": "Dips (Chest)", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Machine Chest Press", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Dumbbell Flyes", "type": "strength", "level": 1, "joint_friendly": True},
    ],
    "back": [
        {"name": "Lat Pulldown", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Seated Cable Row", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Pull-Ups", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Barbell Rows", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Deadlift", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Dumbbell Rows", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "T-Bar Row", "type": "strength", "level": 2, "joint_friendly": False},
    ],
    "shoulders": [
        {"name": "Lateral Raises", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Face Pulls", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Front Raises", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Overhead Press", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Arnold Press", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Machine Shoulder Press", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Reverse Flyes", "type": "strength", "level": 0, "joint_friendly": True},
    ],
    "legs": [
        {"name": "Leg Press", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Leg Curls", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Leg Extensions", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Calf Raises", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Lunges", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Squats", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Romanian Deadlift", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Bulgarian Split Squats", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Hip Thrusts", "type": "strength", "level": 1, "joint_friendly": True},
        {"name": "Goblet Squats", "type": "strength", "level": 0, "joint_friendly": True},
    ],
    "arms": [
        {"name": "Bicep Curls", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Tricep Pushdowns", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Hammer Curls", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Skull Crushers", "type": "strength", "level": 1, "joint_friendly": False},
        {"name": "Concentration Curls", "type": "strength", "level": 1, "joint_friendly": True},
        {"name": "Overhead Tricep Extension", "type": "strength", "level": 1, "joint_friendly": True},
        {"name": "Cable Curls", "type": "strength", "level": 0, "joint_friendly": True},
    ],
    "core": [
        {"name": "Plank", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Crunches", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Russian Twists", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Dead Bugs", "type": "strength", "level": 0, "joint_friendly": True},
        {"name": "Leg Raises", "type": "strength", "level": 1, "joint_friendly": True},
        {"name": "Ab Wheel Rollout", "type": "strength", "level": 2, "joint_friendly": False},
        {"name": "Cable Woodchops", "type": "strength", "level": 1, "joint_friendly": True},
        {"name": "Mountain Climbers", "type": "strength", "level": 1, "joint_friendly": True},
    ],
    "cardio": [
        {"name": "Walking (Treadmill)", "type": "cardio", "level": 0, "low_impact": True},
        {"name": "Cycling", "type": "cardio", "level": 0, "low_impact": True},
        {"name": "Elliptical", "type": "cardio", "level": 0, "low_impact": True},
        {"name": "Rowing Machine", "type": "cardio", "level": 1, "low_impact": True},
        {"name": "Running (Treadmill)", "type": "cardio", "level": 1, "low_impact": False},
        {"name": "Jump Rope", "type": "cardio", "level": 1, "low_impact": False},
        {"name": "Burpees", "type": "cardio", "level": 2, "low_impact": False},
        {"name": "Stair Climber", "type": "cardio", "level": 1, "low_impact": True},
        {"name": "Swimming", "type": "cardio", "level": 0, "low_impact": True},
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

# Goal configs adjust based on BMI category (see _get_goal_config)
BASE_GOAL_CONFIG = {
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


def _get_user_profile(user):
    """Extract user profile data for workout customization."""
    from datetime import date
    age = (date.today() - user.date_of_birth).days // 365

    bmi = None
    if user.height_cm and user.weight_kg:
        bmi = user.weight_kg / ((user.height_cm / 100) ** 2)

    bmi_cat = "normal"
    if bmi:
        if bmi < 18.5:
            bmi_cat = "underweight"
        elif bmi < 25:
            bmi_cat = "normal"
        elif bmi < 30:
            bmi_cat = "overweight"
        else:
            bmi_cat = "obese"

    return {
        "age": age,
        "gender": user.gender,
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "weight_kg": user.weight_kg,
        "activity_level": user.activity_level,
        "fitness_goal": user.fitness_goal,
    }


def _get_goal_config(profile):
    """Adjust workout config based on goal AND BMI/age."""
    goal = profile["fitness_goal"]
    config = {k: v for k, v in BASE_GOAL_CONFIG.get(goal, BASE_GOAL_CONFIG["maintain"]).items()}

    bmi_cat = profile["bmi_category"]
    age = profile["age"]

    # BMI-based adjustments
    if bmi_cat == "obese":
        # More cardio, higher reps, lower intensity
        config["cardio_minutes"] = max(config["cardio_minutes"], 30)
        config["extra_cardio"] = True
        config["reps"] = (max(config["reps"][0], 12), max(config["reps"][1], 15))
        config["rest_sec"] = max(config["rest_sec"], 60)
    elif bmi_cat == "overweight":
        # Moderate cardio boost
        config["cardio_minutes"] = max(config["cardio_minutes"], 20)
        if goal != "lose_weight":
            config["extra_cardio"] = True
    elif bmi_cat == "underweight":
        # Less cardio, focus on strength, more rest
        config["cardio_minutes"] = min(config["cardio_minutes"], 10)
        config["extra_cardio"] = False
        config["rest_sec"] = max(config["rest_sec"], 90)
        if goal == "gain_muscle":
            config["sets"] = (4, 5)
            config["reps"] = (6, 8)

    # Age-based adjustments
    if age >= 50:
        config["rest_sec"] = max(config["rest_sec"], 90)
        config["reps"] = (max(config["reps"][0], 10), max(config["reps"][1], 12))
    elif age < 18:
        config["reps"] = (max(config["reps"][0], 10), max(config["reps"][1], 15))
        config["rest_sec"] = max(config["rest_sec"], 60)

    return config


def _get_max_level(profile):
    """Determine max exercise difficulty from activity level and age."""
    base_mapping = {
        "sedentary": 0,
        "light": 0,
        "moderate": 1,
        "active": 2,
        "very_active": 2,
    }
    level = base_mapping.get(profile["activity_level"], 1)

    # Reduce difficulty for older users or high BMI
    if profile["age"] >= 50 or profile["bmi_category"] == "obese":
        level = min(level, 1)
    if profile["age"] >= 60:
        level = min(level, 0)

    return level


def _prefer_joint_friendly(profile):
    """Should we prefer joint-friendly exercises?"""
    return (
        profile["bmi_category"] in ("overweight", "obese")
        or profile["age"] >= 45
        or profile["activity_level"] in ("sedentary", "light")
    )


def _pick_exercises(group, count, max_level, joint_friendly_pref):
    """Pick exercises filtering by level and optionally preferring joint-friendly ones."""
    pool = [e for e in EXERCISES.get(group, []) if e["level"] <= max_level]

    if not pool:
        return []

    if joint_friendly_pref and group != "cardio":
        friendly = [e for e in pool if e.get("joint_friendly", False)]
        other = [e for e in pool if not e.get("joint_friendly", False)]

        # Pick mostly from friendly, maybe 1 from other
        n_friendly = min(len(friendly), max(count - 1, count))
        picked = random.sample(friendly, min(n_friendly, len(friendly)))

        remaining = count - len(picked)
        if remaining > 0 and other:
            picked += random.sample(other, min(remaining, len(other)))

        return picked[:count]

    return random.sample(pool, min(count, len(pool)))


def _pick_cardio(profile):
    """Pick appropriate cardio based on BMI and fitness level."""
    max_level = _get_max_level(profile)
    pool = [e for e in EXERCISES["cardio"] if e["level"] <= max_level]

    if profile["bmi_category"] in ("overweight", "obese") or profile["age"] >= 50:
        # Prefer low-impact cardio
        low_impact = [e for e in pool if e.get("low_impact", False)]
        if low_impact:
            return random.choice(low_impact)

    return random.choice(pool) if pool else EXERCISES["cardio"][0]


def _get_training_days(profile):
    """Determine number of training days based on activity, BMI, and age."""
    base_days = {
        "sedentary": 3,
        "light": 3,
        "moderate": 4,
        "active": 5,
        "very_active": 6,
    }
    days = base_days.get(profile["activity_level"], 4)

    # Reduce for obese beginners — recovery is important
    if profile["bmi_category"] == "obese" and profile["activity_level"] in ("sedentary", "light"):
        days = min(days, 3)

    # Older users may need more recovery
    if profile["age"] >= 55:
        days = min(days, 4)

    return days


def generate_workout(user):
    """Generate a personalized workout plan based on user profile."""
    profile = _get_user_profile(user)
    num_days = _get_training_days(profile)
    template = SPLIT_TEMPLATES[num_days]
    config = _get_goal_config(profile)
    max_level = _get_max_level(profile)
    joint_friendly = _prefer_joint_friendly(profile)

    workout_plan = {
        "split_name": template["name"],
        "goal": profile["fitness_goal"].replace("_", " ").title(),
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
                    cardio = _pick_cardio(profile)
                    exercises.append({
                        "name": cardio["name"],
                        "is_cardio": True,
                        "duration_min": config["cardio_minutes"],
                    })
                else:
                    picked = _pick_exercises(
                        group, config["exercises_per_group"],
                        max_level, joint_friendly
                    )
                    for ex in picked:
                        exercises.append({
                            "name": ex["name"],
                            "is_cardio": False,
                            "sets": random.randint(*config["sets"]),
                            "reps": random.randint(*config["reps"]),
                            "muscle_group": group.title(),
                        })

            if config["extra_cardio"] and not any(e.get("is_cardio") for e in exercises):
                cardio = _pick_cardio(profile)
                exercises.append({
                    "name": cardio["name"],
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
