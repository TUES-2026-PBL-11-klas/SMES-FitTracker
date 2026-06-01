"""Shared test fixtures."""
import pytest
from datetime import date
from app import create_app, db as _db
from app.models import User


@pytest.fixture(scope="session")
def app():
    """Create application for testing with in-memory SQLite."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost",
    })
    yield app


@pytest.fixture(autouse=True)
def db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_user(db):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        date_of_birth=date(2000, 1, 1),
        gender="male",
        height_cm=180.0,
        weight_kg=75.0,
        activity_level="moderate",
        fitness_goal="gain_muscle",
    )
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def obese_user(db):
    """Create an obese user for testing BMI-based logic."""
    user = User(
        username="obeseuser",
        email="obese@example.com",
        date_of_birth=date(1990, 6, 15),
        gender="female",
        height_cm=165.0,
        weight_kg=110.0,
        activity_level="sedentary",
        fitness_goal="lose_weight",
    )
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def underweight_user(db):
    """Create an underweight user for testing."""
    user = User(
        username="thinuser",
        email="thin@example.com",
        date_of_birth=date(2005, 3, 20),
        gender="male",
        height_cm=175.0,
        weight_kg=50.0,
        activity_level="light",
        fitness_goal="gain_muscle",
    )
    user.set_password("testpass123")
    db.session.add(user)
    db.session.commit()
    return user
