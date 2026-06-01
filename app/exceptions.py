"""
Custom exception classes for FitTracker.

Demonstrates:
- Custom exception hierarchy (OOP: Inheritance)
- Specific error types for different failure modes
- Clean error handling throughout the application
"""


class FitTrackerError(Exception):
    """Base exception for all FitTracker errors (OOP: Abstraction)."""

    def __init__(self, message: str = "An error occurred in FitTracker"):
        self.message = message
        super().__init__(self.message)


class InvalidProfileError(FitTrackerError):
    """Raised when user profile data is invalid or incomplete (OOP: Inheritance)."""

    def __init__(self, field: str, reason: str = "is missing or invalid"):
        self.field = field
        super().__init__(f"Invalid profile: '{field}' {reason}")


class WorkoutGenerationError(FitTrackerError):
    """Raised when workout plan generation fails."""

    def __init__(self, reason: str = "Could not generate workout plan"):
        super().__init__(f"Workout generation failed: {reason}")


class ExerciseNotFoundError(FitTrackerError):
    """Raised when no suitable exercises are found for a muscle group."""

    def __init__(self, muscle_group: str, level: int):
        self.muscle_group = muscle_group
        self.level = level
        super().__init__(
            f"No exercises found for '{muscle_group}' at difficulty level {level}"
        )


class UnauthorizedAccessError(FitTrackerError):
    """Raised when a user tries to access another user's resources."""

    def __init__(self, resource: str = "resource"):
        super().__init__(f"Unauthorized access to {resource}")
