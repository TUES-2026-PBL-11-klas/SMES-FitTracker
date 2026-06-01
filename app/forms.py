from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    FloatField, SelectField, DateField,
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, NumberRange, ValidationError,
)
from app.models import User


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )

    date_of_birth = DateField("Date of Birth", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        choices=[("", "Select..."), ("male", "Male"), ("female", "Female")],
        validators=[DataRequired()],
    )
    height_cm = FloatField(
        "Height (cm)", validators=[DataRequired(), NumberRange(min=100, max=250)]
    )
    weight_kg = FloatField(
        "Weight (kg)", validators=[DataRequired(), NumberRange(min=30, max=300)]
    )
    activity_level = SelectField(
        "Activity Level",
        choices=[
            ("", "Select..."),
            ("sedentary", "Sedentary — little or no exercise"),
            ("light", "Light — 1-3 days/week"),
            ("moderate", "Moderate — 3-5 days/week"),
            ("active", "Active — 6-7 days/week"),
            ("very_active", "Very Active — intense daily training"),
        ],
        validators=[DataRequired()],
    )
    fitness_goal = SelectField(
        "Fitness Goal",
        choices=[
            ("", "Select..."),
            ("lose_weight", "Lose Weight"),
            ("maintain", "Maintain Weight"),
            ("gain_muscle", "Build Muscle"),
        ],
        validators=[DataRequired()],
    )

    submit = SubmitField("Create Account")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email already registered.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")
