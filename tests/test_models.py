"""Unit tests for User model."""
from datetime import date


class TestUserModel:
    """Tests for User model properties and methods."""

    def test_password_hashing(self, sample_user):
        """Password is hashed and can be verified."""
        assert sample_user.password_hash is not None
        assert sample_user.password_hash != "testpass123"
        assert sample_user.check_password("testpass123")
        assert not sample_user.check_password("wrongpassword")

    def test_bmi_calculation(self, sample_user):
        """BMI is calculated correctly from height and weight."""
        # 75 / (1.80^2) = 23.1
        assert sample_user.bmi is not None
        assert 23.0 <= sample_user.bmi <= 23.2

    def test_bmi_category_normal(self, sample_user):
        """Normal BMI user gets correct category."""
        assert sample_user.bmi_category == "Normal"

    def test_bmi_category_obese(self, obese_user):
        """Obese user gets correct category."""
        # 110 / (1.65^2) = 40.4
        assert obese_user.bmi > 30
        assert obese_user.bmi_category == "Obese"

    def test_bmi_category_underweight(self, underweight_user):
        """Underweight user gets correct category."""
        # 50 / (1.75^2) = 16.3
        assert underweight_user.bmi < 18.5
        assert underweight_user.bmi_category == "Underweight"

    def test_daily_calories_male(self, sample_user):
        """Daily calories calculation for male user."""
        cals = sample_user.daily_calories
        assert cals is not None
        assert 2000 <= cals <= 4000

    def test_daily_calories_female(self, obese_user):
        """Daily calories calculation for female user."""
        cals = obese_user.daily_calories
        assert cals is not None
        assert 1500 <= cals <= 4000

    def test_user_repr(self, sample_user):
        """User has correct username."""
        assert sample_user.username == "testuser"
        assert sample_user.email == "test@example.com"
