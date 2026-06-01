from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height_cm = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    fitness_goal = db.Column(db.String(20), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None

    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi is None:
            return "Unknown"
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"

    @property
    def daily_calories(self):
        """BMR via Mifflin-St Jeor, adjusted by activity level."""
        if not all([self.height_cm, self.weight_kg, self.date_of_birth]):
            return None
        from datetime import date
        age = (date.today() - self.date_of_birth).days // 365
        if self.gender == "male":
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * age + 5
        else:
            bmr = 10 * self.weight_kg + 6.25 * self.height_cm - 5 * age - 161
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9,
        }
        return round(bmr * multipliers.get(self.activity_level, 1.2))


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
