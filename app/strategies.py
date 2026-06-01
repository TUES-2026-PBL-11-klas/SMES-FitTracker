"""
Workout generation strategies using the Strategy design pattern.

Design Pattern: Strategy
- Problem: Different fitness goals require fundamentally different workout
  configurations (rep ranges, rest times, cardio amounts, exercise selection).
- Solution: Encapsulate each goal's logic in its own strategy class that
  implements a common interface. New goals can be added without modifying
  existing code.

OOP Principles demonstrated:
- Abstraction: WorkoutStrategy ABC defines the interface
- Polymorphism: Each strategy implements get_config() differently
- Inheritance: Concrete strategies inherit from WorkoutStrategy
- Encapsulation: Each strategy encapsulates its own configuration logic

SOLID Principles demonstrated:
- Single Responsibility (SRP): Each strategy handles one goal's config
- Open/Closed (OCP): New goals = new strategy class, no existing code changes
- Liskov Substitution (LSP): Any strategy can replace another transparently
- Dependency Inversion (DIP): Service depends on abstraction, not concrete classes
"""

from abc import ABC, abstractmethod
from typing import Any


# --- SOLID: SRP - UserProfile has one responsibility: hold validated profile data ---
class UserProfile:
    """Value object holding validated user profile data (OOP: Encapsulation)."""

    __slots__ = ("age", "gender", "bmi", "bmi_category", "weight_kg",
                 "activity_level", "fitness_goal")

    def __init__(self, age: int, gender: str, bmi: float, bmi_category: str,
                 weight_kg: float, activity_level: str, fitness_goal: str):
        self.age = age
        self.gender = gender
        self.bmi = bmi
        self.bmi_category = bmi_category
        self.weight_kg = weight_kg
        self.activity_level = activity_level
        self.fitness_goal = fitness_goal

    @classmethod
    def from_user(cls, user) -> "UserProfile":
        """Factory method to create profile from User model (Design Pattern: Factory Method)."""
        from datetime import date
        from app.exceptions import InvalidProfileError

        if not user.date_of_birth:
            raise InvalidProfileError("date_of_birth")
        if not user.height_cm or not user.weight_kg:
            raise InvalidProfileError("height_cm/weight_kg", "must be positive numbers")

        age = (date.today() - user.date_of_birth).days // 365
        bmi = user.weight_kg / ((user.height_cm / 100) ** 2)

        # Categorize BMI (Python equivalent of ternary/Stream)
        def categorize(b):
            if b < 18.5:
                return "underweight"
            elif b < 25:
                return "normal"
            elif b < 30:
                return "overweight"
            return "obese"

        return cls(
            age=age,
            gender=user.gender,
            bmi=round(bmi, 1),
            bmi_category=categorize(bmi),
            weight_kg=user.weight_kg,
            activity_level=user.activity_level,
            fitness_goal=user.fitness_goal,
        )


# --- Design Pattern: Strategy (Abstract) ---
# --- SOLID: OCP - open for extension, closed for modification ---
class WorkoutStrategy(ABC):
    """
    Abstract base class for workout strategies (OOP: Abstraction).

    Each concrete strategy encapsulates the workout configuration logic
    for a specific fitness goal. This allows adding new goals without
    modifying existing code (SOLID: Open/Closed Principle).
    """

    @abstractmethod
    def get_config(self, profile: UserProfile) -> dict[str, Any]:
        """Return workout configuration for the given user profile."""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """Return human-readable description of this strategy."""
        ...

    def _apply_bmi_adjustments(self, config: dict, profile: UserProfile) -> dict:
        """Template method for BMI-based adjustments (Design Pattern: Template Method)."""
        return config

    def _apply_age_adjustments(self, config: dict, profile: UserProfile) -> dict:
        """Adjust config based on user age."""
        if profile.age >= 50:
            config["rest_sec"] = max(config["rest_sec"], 90)
            config["reps"] = (max(config["reps"][0], 10), max(config["reps"][1], 12))
        elif profile.age < 18:
            config["reps"] = (max(config["reps"][0], 10), max(config["reps"][1], 15))
            config["rest_sec"] = max(config["rest_sec"], 60)
        return config


# --- Design Pattern: Strategy (Concrete) ---
# --- SOLID: LSP - each strategy is substitutable for WorkoutStrategy ---
class LoseWeightStrategy(WorkoutStrategy):
    """Strategy for users with a weight loss goal (OOP: Polymorphism)."""

    def get_config(self, profile: UserProfile) -> dict[str, Any]:
        config = {
            "sets": (3, 4),
            "reps": (12, 15),
            "rest_sec": 45,
            "cardio_minutes": 25,
            "exercises_per_group": 2,
            "extra_cardio": True,
        }
        config = self._apply_bmi_adjustments(config, profile)
        config = self._apply_age_adjustments(config, profile)
        return config

    def get_description(self) -> str:
        return "High rep ranges with extra cardio for maximum calorie burn"

    def _apply_bmi_adjustments(self, config: dict, profile: UserProfile) -> dict:
        if profile.bmi_category == "obese":
            config["cardio_minutes"] = 30
            config["rest_sec"] = 60
        return config


class MaintainStrategy(WorkoutStrategy):
    """Strategy for users wanting to maintain their current physique."""

    def get_config(self, profile: UserProfile) -> dict[str, Any]:
        config = {
            "sets": (3, 4),
            "reps": (8, 12),
            "rest_sec": 60,
            "cardio_minutes": 15,
            "exercises_per_group": 2,
            "extra_cardio": False,
        }
        config = self._apply_bmi_adjustments(config, profile)
        config = self._apply_age_adjustments(config, profile)
        return config

    def get_description(self) -> str:
        return "Balanced approach with moderate intensity"

    def _apply_bmi_adjustments(self, config: dict, profile: UserProfile) -> dict:
        if profile.bmi_category in ("overweight", "obese"):
            config["extra_cardio"] = True
            config["cardio_minutes"] = 20
        return config


class GainMuscleStrategy(WorkoutStrategy):
    """Strategy for users focused on muscle gain."""

    def get_config(self, profile: UserProfile) -> dict[str, Any]:
        config = {
            "sets": (4, 5),
            "reps": (6, 10),
            "rest_sec": 90,
            "cardio_minutes": 10,
            "exercises_per_group": 3,
            "extra_cardio": False,
        }
        config = self._apply_bmi_adjustments(config, profile)
        config = self._apply_age_adjustments(config, profile)
        return config

    def get_description(self) -> str:
        return "Heavy compound movements with progressive overload"

    def _apply_bmi_adjustments(self, config: dict, profile: UserProfile) -> dict:
        if profile.bmi_category == "underweight":
            config["cardio_minutes"] = 5
            config["sets"] = (4, 5)
            config["reps"] = (6, 8)
        elif profile.bmi_category in ("overweight", "obese"):
            config["extra_cardio"] = True
            config["cardio_minutes"] = 20
        return config


# --- Design Pattern: Factory ---
# --- SOLID: DIP - returns abstraction, not concrete class ---
class StrategyFactory:
    """
    Factory for creating workout strategies (Design Pattern: Factory).

    Problem: Client code shouldn't know about concrete strategy classes.
    Solution: Factory encapsulates the creation logic and returns the
    appropriate strategy based on the fitness goal string.
    """

    # Using dict as a registry (Python equivalent of Map/HashMap)
    _strategies: dict[str, type[WorkoutStrategy]] = {
        "lose_weight": LoseWeightStrategy,
        "maintain": MaintainStrategy,
        "gain_muscle": GainMuscleStrategy,
    }

    @classmethod
    def create(cls, goal: str) -> WorkoutStrategy:
        """Create a strategy for the given goal (OOP: Polymorphism via factory)."""
        strategy_class = cls._strategies.get(goal)
        if strategy_class is None:
            # Fallback to maintain strategy
            strategy_class = MaintainStrategy
        return strategy_class()

    @classmethod
    def register(cls, goal: str, strategy_class: type[WorkoutStrategy]) -> None:
        """Register a new strategy (SOLID: OCP - extend without modifying)."""
        cls._strategies[goal] = strategy_class

    @classmethod
    def available_goals(cls) -> list[str]:
        """List all available goal strategies."""
        return list(cls._strategies.keys())
