"""Unit tests for Strategy pattern and services."""
import pytest
from app.strategies import (
    UserProfile,
    StrategyFactory,
    LoseWeightStrategy,
    MaintainStrategy,
    GainMuscleStrategy,
    WorkoutStrategy,
)
from app.services import WorkoutService, ExerciseSelector
from app.exceptions import InvalidProfileError, ExerciseNotFoundError


class TestUserProfile:
    """Tests for UserProfile value object."""

    def test_from_user(self, app, sample_user):
        """UserProfile is created correctly from User model."""
        with app.app_context():
            profile = UserProfile.from_user(sample_user)
            assert profile.gender == "male"
            assert profile.bmi_category == "normal"
            assert profile.fitness_goal == "gain_muscle"
            assert profile.age > 0

    def test_obese_profile(self, app, obese_user):
        """Obese user profile has correct BMI category."""
        with app.app_context():
            profile = UserProfile.from_user(obese_user)
            assert profile.bmi_category == "obese"
            assert profile.bmi > 30

    def test_underweight_profile(self, app, underweight_user):
        """Underweight user profile has correct BMI category."""
        with app.app_context():
            profile = UserProfile.from_user(underweight_user)
            assert profile.bmi_category == "underweight"


class TestStrategyFactory:
    """Tests for StrategyFactory (Design Pattern: Factory)."""

    def test_create_lose_weight(self):
        """Factory creates LoseWeightStrategy for lose_weight goal."""
        strategy = StrategyFactory.create("lose_weight")
        assert isinstance(strategy, LoseWeightStrategy)

    def test_create_maintain(self):
        """Factory creates MaintainStrategy for maintain goal."""
        strategy = StrategyFactory.create("maintain")
        assert isinstance(strategy, MaintainStrategy)

    def test_create_gain_muscle(self):
        """Factory creates GainMuscleStrategy for gain_muscle goal."""
        strategy = StrategyFactory.create("gain_muscle")
        assert isinstance(strategy, GainMuscleStrategy)

    def test_create_unknown_defaults_to_maintain(self):
        """Unknown goal falls back to MaintainStrategy."""
        strategy = StrategyFactory.create("unknown_goal")
        assert isinstance(strategy, MaintainStrategy)

    def test_available_goals(self):
        """All expected goals are available."""
        goals = StrategyFactory.available_goals()
        assert "lose_weight" in goals
        assert "maintain" in goals
        assert "gain_muscle" in goals

    def test_all_strategies_are_workout_strategy(self):
        """All created strategies implement WorkoutStrategy (LSP)."""
        for goal in StrategyFactory.available_goals():
            strategy = StrategyFactory.create(goal)
            assert isinstance(strategy, WorkoutStrategy)


class TestStrategies:
    """Tests for concrete strategy configurations."""

    def _make_profile(self, **kwargs):
        defaults = {
            "age": 25, "gender": "male", "bmi": 22.0,
            "bmi_category": "normal", "weight_kg": 75.0,
            "activity_level": "moderate", "fitness_goal": "maintain",
        }
        defaults.update(kwargs)
        return UserProfile(**defaults)

    def test_lose_weight_has_more_cardio(self):
        """Lose weight strategy has more cardio than gain muscle."""
        profile = self._make_profile(fitness_goal="lose_weight")
        lw = LoseWeightStrategy().get_config(profile)
        gm = GainMuscleStrategy().get_config(profile)
        assert lw["cardio_minutes"] > gm["cardio_minutes"]
        assert lw["extra_cardio"] is True

    def test_gain_muscle_has_higher_sets(self):
        """Gain muscle strategy has more sets."""
        profile = self._make_profile(fitness_goal="gain_muscle")
        gm = GainMuscleStrategy().get_config(profile)
        assert gm["sets"][0] >= 4
        assert gm["exercises_per_group"] == 3

    def test_lose_weight_has_higher_reps(self):
        """Lose weight uses higher rep ranges."""
        profile = self._make_profile(fitness_goal="lose_weight")
        lw = LoseWeightStrategy().get_config(profile)
        assert lw["reps"][0] >= 12

    def test_obese_adjustments(self):
        """Obese user gets adjusted config regardless of strategy."""
        profile = self._make_profile(bmi=35.0, bmi_category="obese")
        lw = LoseWeightStrategy().get_config(profile)
        assert lw["cardio_minutes"] >= 25
        assert lw["rest_sec"] >= 60

    def test_age_adjustments(self):
        """Older users get longer rest times."""
        profile = self._make_profile(age=55)
        config = MaintainStrategy().get_config(profile)
        assert config["rest_sec"] >= 90

    def test_strategy_description(self):
        """Each strategy has a description."""
        for goal in StrategyFactory.available_goals():
            strategy = StrategyFactory.create(goal)
            desc = strategy.get_description()
            assert isinstance(desc, str)
            assert len(desc) > 10


class TestExerciseSelector:
    """Tests for ExerciseSelector."""

    def test_select_returns_exercises(self):
        """Selector returns the requested number of exercises."""
        selector = ExerciseSelector(max_level=2, prefer_joint_friendly=False)
        exercises = selector.select("chest", 3)
        assert len(exercises) <= 3
        assert all("name" in e for e in exercises)

    def test_joint_friendly_preference(self):
        """Joint-friendly selector prefers safe exercises."""
        selector = ExerciseSelector(max_level=2, prefer_joint_friendly=True)
        exercises = selector.select("chest", 2)
        # At least some should be joint-friendly
        friendly_count = sum(1 for e in exercises if e.get("joint_friendly"))
        assert friendly_count >= 1

    def test_no_duplicate_exercises(self):
        """Selector avoids duplicates across multiple calls."""
        selector = ExerciseSelector(max_level=2, prefer_joint_friendly=False)
        first = selector.select("chest", 2)
        second = selector.select("chest", 2)
        first_names = {e["name"] for e in first}
        second_names = {e["name"] for e in second}
        # Should try to avoid overlap
        assert len(first_names | second_names) >= 3

    def test_level_filtering(self):
        """Only exercises at or below max level are selected."""
        selector = ExerciseSelector(max_level=0, prefer_joint_friendly=False)
        exercises = selector.select("chest", 5)
        assert all(e["level"] <= 0 for e in exercises)


class TestWorkoutService:
    """Tests for WorkoutService (DI and generation)."""

    def test_generate_plan_structure(self, app, sample_user):
        """Generated plan has correct structure."""
        with app.app_context():
            strategy = StrategyFactory.create("gain_muscle")
            service = WorkoutService(strategy=strategy)
            plan = service.generate_plan(sample_user)

            assert "split_name" in plan
            assert "goal" in plan
            assert "days_per_week" in plan
            assert "rest_between_sets" in plan
            assert "days" in plan
            assert len(plan["days"]) == 7

    def test_plan_has_rest_days(self, app, sample_user):
        """Plan includes rest days."""
        with app.app_context():
            service = WorkoutService(strategy=GainMuscleStrategy())
            plan = service.generate_plan(sample_user)
            rest_days = [d for d in plan["days"] if d["is_rest"]]
            assert len(rest_days) >= 1

    def test_plan_training_days_have_exercises(self, app, sample_user):
        """Training days have exercises."""
        with app.app_context():
            service = WorkoutService(strategy=GainMuscleStrategy())
            plan = service.generate_plan(sample_user)
            training_days = [d for d in plan["days"] if not d["is_rest"]]
            assert all(len(d["exercises"]) > 0 for d in training_days)

    def test_strategy_injection(self, app, sample_user):
        """Service uses injected strategy."""
        with app.app_context():
            service = WorkoutService(strategy=LoseWeightStrategy())
            plan = service.generate_plan(sample_user)
            assert plan["goal"] == "Gain Muscle"  # goal comes from user profile

    def test_auto_strategy_selection(self, app, sample_user):
        """Service auto-selects strategy if none injected."""
        with app.app_context():
            service = WorkoutService()  # No strategy injected
            plan = service.generate_plan(sample_user)
            assert plan is not None
            assert len(plan["days"]) == 7
