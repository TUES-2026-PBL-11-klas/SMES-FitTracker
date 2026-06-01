"""
Exercise database and split templates.

SOLID: SRP - This module is only responsible for exercise data.
Separated from generation logic for clean architecture.
"""

EXERCISES: dict[str, list[dict]] = {
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

SPLIT_TEMPLATES: dict[int, dict] = {
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

DAY_NAMES: list[str] = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
