"""Integration tests for routes."""
import pytest
from app.models import WorkoutPlan


class TestPublicRoutes:
    """Integration tests for public-facing routes."""

    def test_index_page(self, client):
        """Home page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"FitTracker" in response.data

    def test_login_page(self, client):
        """Login page loads."""
        response = client.get("/login")
        assert response.status_code == 200

    def test_register_page(self, client):
        """Register page loads."""
        response = client.get("/register")
        assert response.status_code == 200


class TestProtectedRoutes:
    """Integration tests for authenticated routes."""

    def test_dashboard_requires_login(self, client):
        """Dashboard redirects to login when not authenticated."""
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_workout_requires_login(self, client):
        """Workout page redirects to login when not authenticated."""
        response = client.get("/workout", follow_redirects=False)
        assert response.status_code == 302

    def test_login_and_access_dashboard(self, client, sample_user, app):
        """User can login and access dashboard."""
        with app.app_context():
            response = client.post("/login", data={
                "email": "test@example.com",
                "password": "testpass123",
            }, follow_redirects=True)
            assert response.status_code == 200

            response = client.get("/dashboard")
            assert response.status_code == 200

    def test_workout_regenerate_creates_plan(self, client, sample_user, app, db):
        """Regenerate creates a new workout plan in the database."""
        with app.app_context():
            # Login
            client.post("/login", data={
                "email": "test@example.com",
                "password": "testpass123",
            })

            # Regenerate
            response = client.get("/workout/regenerate", follow_redirects=True)
            assert response.status_code == 200

            # Check plan was created
            plan = WorkoutPlan.query.filter_by(
                user_id=sample_user.id, is_active=True
            ).first()
            assert plan is not None
            assert plan.days_per_week > 0
            assert len(plan.days) == 7
