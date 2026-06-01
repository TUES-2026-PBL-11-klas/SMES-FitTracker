"""Unit tests for custom exceptions."""
import pytest
from app.exceptions import (
    FitTrackerError,
    InvalidProfileError,
    WorkoutGenerationError,
    ExerciseNotFoundError,
    UnauthorizedAccessError,
)


class TestExceptionHierarchy:
    """Test custom exception inheritance chain."""

    def test_all_inherit_from_base(self):
        """All custom exceptions inherit from FitTrackerError."""
        exceptions = [
            InvalidProfileError("field"),
            WorkoutGenerationError(),
            ExerciseNotFoundError("chest", 1),
            UnauthorizedAccessError(),
        ]
        for exc in exceptions:
            assert isinstance(exc, FitTrackerError)
            assert isinstance(exc, Exception)

    def test_invalid_profile_message(self):
        """InvalidProfileError stores field name and message."""
        exc = InvalidProfileError("height_cm", "must be positive")
        assert "height_cm" in str(exc)
        assert "must be positive" in str(exc)
        assert exc.field == "height_cm"

    def test_exercise_not_found_details(self):
        """ExerciseNotFoundError stores group and level."""
        exc = ExerciseNotFoundError("chest", 2)
        assert exc.muscle_group == "chest"
        assert exc.level == 2
        assert "chest" in str(exc)

    def test_raising_and_catching(self):
        """Custom exceptions can be raised and caught specifically."""
        with pytest.raises(InvalidProfileError):
            raise InvalidProfileError("weight_kg")

        # Can also catch via base class
        with pytest.raises(FitTrackerError):
            raise WorkoutGenerationError("test reason")
