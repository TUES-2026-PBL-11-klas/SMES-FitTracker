"""
Service layer for FitTracker business logic.

Demonstrates:
- Dependency Injection: WorkoutService receives its strategy via constructor
- SOLID: SRP - service handles orchestration, strategy handles config
- SOLID: DIP - depends on WorkoutStrategy abstraction, not concrete classes
- Threading: Parallel exercise selection using concurrent.futures
- Python collections: set, dict, defaultdict, list comprehensions
- Python equivalents of Stream API: map(), filter(), sorted(), comprehensions
"""

import random
import logging
from typing import Any
from collections import defaultdict  # noqa: F401 – used in exercise grouping
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.strategies import WorkoutStrategy, UserProfile, StrategyFactory
from app.exceptions import WorkoutGenerationError  # noqa: F401
from app.exceptions import ExerciseNotFoundError, InvalidProfileError
from app.exercises import EXERCISES, SPLIT_TEMPLATES, DAY_NAMES

logger = logging.getLogger(__name__)


class ExerciseSelector:
    """
    Selects exercises based on user profile and constraints.

    Demonstrates:
    - SOLID: SRP - only responsible for exercise selection
    - Python collections: set for tracking used exercises, defaultdict for grouping
    - Lambda/comprehensions: filtering and mapping exercise data
    """

    def __init__(self, max_level: int, prefer_joint_friendly: bool):
        self._max_level = max_level
        self._prefer_joint_friendly = prefer_joint_friendly
        # Using set to track selected exercises and avoid duplicates
        self._used_exercises: set[str] = set()

    def select(self, group: str, count: int) -> list[dict[str, Any]]:
        """Select exercises for a muscle group, avoiding duplicates."""
        pool = EXERCISES.get(group, [])

        if not pool:
            raise ExerciseNotFoundError(group, self._max_level)

        # Python equivalent of Stream API: filter() with lambda
        filtered = list(filter(
            lambda e: e["level"] <= self._max_level and e["name"] not in self._used_exercises,
            pool
        ))

        if not filtered:
            # Reset used exercises for this group if all are exhausted
            filtered = [e for e in pool if e["level"] <= self._max_level]

        if self._prefer_joint_friendly and group != "cardio":
            # Using sorted() with key function (Python equivalent of Comparator)
            filtered = sorted(
                filtered,
                key=lambda e: (0 if e.get("joint_friendly", False) else 1, random.random())
            )
        else:
            random.shuffle(filtered)

        selected = filtered[:count]

        # Track used exercises using set.update()
        self._used_exercises.update(map(lambda e: e["name"], selected))

        return selected

    def select_cardio(self, profile: UserProfile) -> dict[str, Any]:
        """Select appropriate cardio exercise based on profile."""
        pool = EXERCISES.get("cardio", [])

        # Using list comprehension with multiple conditions
        suitable = [
            e for e in pool
            if e["level"] <= self._max_level
            and e["name"] not in self._used_exercises
        ]

        if profile.bmi_category in ("overweight", "obese") or profile.age >= 50:
            # Filter for low-impact using list comprehension
            low_impact = [e for e in suitable if e.get("low_impact", False)]
            if low_impact:
                suitable = low_impact

        if not suitable:
            suitable = [e for e in pool if e["level"] <= self._max_level]

        choice = random.choice(suitable) if suitable else pool[0]
        self._used_exercises.add(choice["name"])
        return choice


class WorkoutService:
    """
    Main service for workout plan generation.

    Design Pattern: Strategy (context)
    - Receives a WorkoutStrategy via constructor injection (DI)
    - Delegates configuration decisions to the strategy
    - Can switch strategies at runtime

    SOLID: DIP - depends on WorkoutStrategy abstraction
    SOLID: SRP - orchestrates generation, doesn't decide configs
    """

    def __init__(self, strategy: WorkoutStrategy | None = None):
        """
        Dependency Injection: strategy is injected, not created internally.

        This allows:
        1. Easy testing with mock strategies
        2. Runtime strategy switching
        3. New goals without modifying this class
        """
        self._strategy = strategy

    @property
    def strategy(self) -> WorkoutStrategy | None:
        """Encapsulated access to the current strategy (OOP: Encapsulation)."""
        return self._strategy

    @strategy.setter
    def strategy(self, new_strategy: WorkoutStrategy) -> None:
        """Allow runtime strategy switching."""
        self._strategy = new_strategy

    def generate_plan(self, user) -> dict[str, Any]:
        """
        Generate a complete workout plan for the user.

        Uses threading for parallel exercise selection per day,
        demonstrating Python's concurrent.futures module.
        """
        try:
            profile = UserProfile.from_user(user)
        except InvalidProfileError:
            raise

        # Auto-select strategy if not injected (fallback)
        if self._strategy is None:
            self._strategy = StrategyFactory.create(profile.fitness_goal)

        config = self._strategy.get_config(profile)
        logger.info(
            "Generating plan for user=%s goal=%s bmi=%.1f",
            getattr(user, "username", "unknown"),
            profile.fitness_goal,
            profile.bmi,
        )

        num_days = self._get_training_days(profile)
        template = SPLIT_TEMPLATES[num_days]
        rest_days = self._distribute_rest_days(num_days)
        max_level = self._get_max_level(profile)
        joint_friendly = self._prefer_joint_friendly(profile)

        # --- Multithreading: parallel exercise selection per training day ---
        training_day_data = []
        day_idx = 0
        for i in range(7):
            if i not in rest_days:
                day_template = template["days"][day_idx % len(template["days"])]
                training_day_data.append((i, day_template))
                day_idx += 1

        # Use ThreadPoolExecutor for parallel day generation
        day_results: dict[int, dict] = {}

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(
                    self._generate_day_exercises,
                    day_template, config, max_level, joint_friendly, profile
                ): day_index
                for day_index, day_template in training_day_data
            }

            for future in as_completed(futures):
                day_index = futures[future]
                try:
                    day_results[day_index] = future.result()
                except ExerciseNotFoundError as e:
                    logger.warning("Exercise selection issue: %s", e)
                    day_results[day_index] = {"exercises": []}

        # Build the final plan
        plan_days = []
        day_idx = 0
        for i in range(7):
            if i in rest_days:
                plan_days.append({
                    "day_name": DAY_NAMES[i],
                    "is_rest": True,
                    "workout_name": "Rest Day",
                    "exercises": [],
                })
            else:
                day_template = template["days"][day_idx % len(template["days"])]
                exercises = day_results.get(i, {}).get("exercises", [])
                plan_days.append({
                    "day_name": DAY_NAMES[i],
                    "is_rest": False,
                    "workout_name": day_template["name"],
                    "exercises": exercises,
                })
                day_idx += 1

        return {
            "split_name": template["name"],
            "goal": profile.fitness_goal.replace("_", " ").title(),
            "days_per_week": num_days,
            "rest_between_sets": config["rest_sec"],
            "days": plan_days,
        }

    def _generate_day_exercises(
        self,
        day_template: dict,
        config: dict,
        max_level: int,
        joint_friendly: bool,
        profile: UserProfile,
    ) -> dict[str, Any]:
        """Generate exercises for a single day (runs in separate thread)."""
        selector = ExerciseSelector(max_level, joint_friendly)
        exercises: list[dict[str, Any]] = []

        for group in day_template["groups"]:
            if group == "cardio":
                cardio = selector.select_cardio(profile)
                exercises.append({
                    "name": cardio["name"],
                    "is_cardio": True,
                    "duration_min": config["cardio_minutes"],
                })
            else:
                picked = selector.select(group, config["exercises_per_group"])
                # Using list comprehension to transform exercises (Stream.map equivalent)
                exercises.extend([
                    {
                        "name": ex["name"],
                        "is_cardio": False,
                        "sets": random.randint(*config["sets"]),
                        "reps": random.randint(*config["reps"]),
                        "muscle_group": group.title(),
                    }
                    for ex in picked
                ])

        # Add extra cardio if configured
        if config["extra_cardio"] and not any(
            e.get("is_cardio") for e in exercises
        ):
            cardio = selector.select_cardio(profile)
            exercises.append({
                "name": cardio["name"],
                "is_cardio": True,
                "duration_min": config["cardio_minutes"],
            })

        return {"exercises": exercises}

    @staticmethod
    def _get_training_days(profile: UserProfile) -> int:
        """Determine training days from profile."""
        # Using dict.get() with default (Python collections)
        base = {"sedentary": 3, "light": 3, "moderate": 4, "active": 5, "very_active": 6}
        days = base.get(profile.activity_level, 4)

        if profile.bmi_category == "obese" and profile.activity_level in ("sedentary", "light"):
            days = min(days, 3)
        if profile.age >= 55:
            days = min(days, 4)

        return days

    @staticmethod
    def _get_max_level(profile: UserProfile) -> int:
        level = {"sedentary": 0, "light": 0, "moderate": 1, "active": 2, "very_active": 2}.get(
            profile.activity_level, 1
        )
        if profile.age >= 50 or profile.bmi_category == "obese":
            level = min(level, 1)
        if profile.age >= 60:
            level = min(level, 0)
        return level

    @staticmethod
    def _prefer_joint_friendly(profile: UserProfile) -> bool:
        # Using set membership check (Python collections: set)
        high_bmi = {
            "overweight",
            "obese",
        }
        low_activity = {"sedentary", "light"}

        return (
            profile.bmi_category in high_bmi
            or profile.age >= 45
            or profile.activity_level in low_activity
        )

    @staticmethod
    def _distribute_rest_days(num_training: int) -> set[int]:
        """Return set of rest day indices (Python collections: set)."""
        rest_map: dict[int, set[int]] = {
            1: {6},
            2: {3, 6},
            3: {2, 4, 6},
            4: {1, 3, 5, 6},
        }
        return rest_map.get(7 - num_training, {1, 3, 5, 6})


# --- Convenience function (backward compatible) ---
def generate_workout(user) -> dict[str, Any]:
    """Generate a workout plan using the Strategy pattern with auto-selected strategy."""
    # SOLID: DIP - strategy is created via factory, not hardcoded
    strategy = StrategyFactory.create(user.fitness_goal)
    service = WorkoutService(strategy=strategy)
    return service.generate_plan(user)
