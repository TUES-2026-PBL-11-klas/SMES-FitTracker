# FitTracker

A full-stack fitness tracking web application built with Flask and PostgreSQL. FitTracker helps users manage their workouts, track nutrition, monitor body composition, and stay on schedule with reminders.

## Features

- **Workout Planner** — AI-generated weekly workout plans based on fitness goals, with exercise tracking and completion status
- **Calorie Tracker** — Daily food logging with USDA API nutrition auto-lookup, macro tracking (protein/carbs/fat), weekly charts
- **BMI Calculator** — Interactive body mass index calculator with SVG gauge visualization
- **Progress Charts** — Chart.js graphs for weight trends, daily calories, and workout volume over time
- **Reminders** — Configurable fitness reminders with background scheduler thread
- **User Profiles** — Registration with body metrics, BMR/TDEE calculation, activity level tracking

## Architecture

FitTracker uses **MVC (Model-View-Controller)** architecture via Flask Blueprints:

```
app/
├── __init__.py          # Application factory (Flask app creation)
├── models.py            # Data layer — SQLAlchemy ORM models
├── routes/
│   ├── auth.py          # Controller — authentication (login, register, logout)
│   └── main.py          # Controller — main app routes (workout, calories, BMI, etc.)
├── templates/           # View layer — Jinja2 HTML templates
│   ├── base.html        # Base template with navbar
│   ├── dashboard.html   # Dashboard with BMI gauge, calorie ring, profile
│   ├── workout.html     # Weekly workout plan view
│   ├── calories.html    # Calorie tracker with AI lookup
│   ├── bmi.html         # BMI calculator with SVG gauge
│   ├── progress.html    # Chart.js progress graphs
│   └── reminders.html   # Reminder management
├── static/
│   └── style.css        # Dark theme CSS
├── services.py          # Business logic — workout generation service
├── strategies.py        # Strategy pattern — workout configurations per goal
├── exercises.py         # Exercise database and selector
├── exceptions.py        # Custom exception hierarchy
├── scheduler.py         # Background thread for reminder notifications
└── forms.py             # Flask-WTF form definitions
```

## Design Patterns

### 1. Strategy Pattern (`app/strategies.py`)
**Problem:** Different fitness goals (lose weight, gain muscle, maintain) require completely different workout configurations — rep ranges, rest times, cardio amounts, exercise selection.

**Solution:** Each goal is encapsulated in its own strategy class implementing a common `WorkoutStrategy` interface. Adding a new goal means creating a new class without modifying existing code.

### 2. Factory Pattern (`app/strategies.py` — `StrategyFactory`)
**Problem:** Client code needs to create the right strategy based on a string input (user's selected goal) without knowing all concrete classes.

**Solution:** `StrategyFactory.create(goal)` maps goal strings to strategy instances, centralizing object creation.

### 3. Dependency Injection (`app/routes/main.py` + `app/services.py`)
**Problem:** `WorkoutService` should not be tightly coupled to a specific strategy implementation.

**Solution:** Strategy is injected into `WorkoutService(strategy=strategy)` at runtime. The service depends on the abstraction, not the concrete class.

## SOLID Principles

| Principle | Where Applied | Example |
|-----------|--------------|---------|
| **SRP** — Single Responsibility | `strategies.py`, `services.py` | Each strategy handles only its goal's config; `WorkoutService` only generates plans |
| **OCP** — Open/Closed | `strategies.py` | New fitness goals = new strategy class, zero changes to existing code |
| **LSP** — Liskov Substitution | `WorkoutStrategy` subclasses | Any strategy can replace another — `LoseWeightStrategy` and `GainMuscleStrategy` are interchangeable |
| **ISP** — Interface Segregation | `WorkoutStrategy` ABC | Interface defines only `get_config()` — strategies aren't forced to implement unnecessary methods |
| **DIP** — Dependency Inversion | `services.py` | `WorkoutService` depends on abstract `WorkoutStrategy`, not concrete implementations |

## OOP Principles

- **Inheritance:** `FitTrackerError` → `InvalidProfileError`, `WorkoutGenerationError`; `WorkoutStrategy` → concrete strategies
- **Polymorphism:** Each strategy's `get_config()` returns different configurations; `bmi_category` property returns different strings
- **Encapsulation:** User model hides password hashing (`set_password`/`check_password`); strategy internals hidden behind `get_config()`
- **Abstraction:** `WorkoutStrategy` ABC defines interface; Flask blueprints abstract route grouping

## Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12+ | Backend language |
| Flask | 3.1.1 | Web framework |
| PostgreSQL | 17 | Relational database |
| SQLAlchemy | 2.x | ORM |
| Flask-Migrate | 4.1.0 | Database migrations (Alembic) |
| Flask-Login | 0.6.3 | Authentication & sessions |
| Flask-WTF | 1.2.2 | Form handling & CSRF |
| Chart.js | 4.4.4 | Client-side progress charts |
| Bootstrap | 5.3.3 | Responsive CSS framework |
| Docker | - | Containerization |
| GitHub Actions | - | CI/CD pipeline |
| Gunicorn | 23.0.0 | Production WSGI server |
| pytest | 8.3.4 | Unit & integration testing |
| flake8 | 7.1.0 | Code linting |
| pre-commit | 4.0.1 | Git hook management |

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/register` | Multi-step registration form |
| GET/POST | `/login` | User login |
| GET | `/logout` | User logout |

### Workout
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workout` | View active workout plan |
| GET | `/workout/regenerate` | Generate new workout plan |
| POST | `/workout/toggle/<id>` | Toggle exercise completion |
| POST | `/workout/reset-day/<id>` | Reset all exercises for a day |
| GET | `/workout/history` | View past workout plans |

### Calories
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/calories` | Daily calorie tracker with charts |
| POST | `/calories/add` | Log a food entry |
| POST | `/calories/delete/<id>` | Delete a food entry |
| POST | `/calories/lookup` | AI nutrition lookup (USDA API) |

### BMI
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/bmi` | BMI calculator with gauge |

### Progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/progress` | Weight, calorie, volume charts |
| POST | `/progress/weight` | Log a weight entry |

### Reminders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reminders` | View all reminders |
| POST | `/reminders/add` | Create a reminder |
| POST | `/reminders/toggle/<id>` | Toggle reminder ON/OFF |
| POST | `/reminders/delete/<id>` | Delete a reminder |
| GET | `/notifications` | Get pending notifications (from scheduler) |

## Database Schema

PostgreSQL with 7 normalized tables:

- **users** — Account info, body metrics, fitness goals
- **workout_plans** — Generated workout plans per user
- **workout_days** — Days within a plan (Mon-Sun)
- **workout_exercises** — Exercises within a day
- **food_entries** — Daily food log entries with macros
- **weight_logs** — Historical weight measurements
- **reminders** — User reminder schedules

ORM: SQLAlchemy with `lazy="dynamic"` for large collections and `lazy="select"` for small related sets. All migrations managed via Flask-Migrate (Alembic).

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 17+
- Docker (optional)

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/TUES-2026-PBL-11-klas/SMES-FitTracker.git
cd SMES-FitTracker
docker-compose up --build
```
App runs at http://localhost:5000

### Option 2: Local Development
```bash
# Clone and install
git clone https://github.com/TUES-2026-PBL-11-klas/SMES-FitTracker.git
cd SMES-FitTracker
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Setup database
cp .env.example .env         # Edit DATABASE_URL if needed
flask db upgrade

# Run
flask run --debug
```

### Running Tests
```bash
pytest --cov=app --cov-report=term-missing -v
```
Current coverage: **81%** (43 tests — unit + integration)

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Test** — Run pytest with PostgreSQL service container, enforce 50% coverage minimum
2. **Lint** — Run flake8 code style checks
3. **Docker** — Build and verify Docker image

Triggers on push to main and feature branches, and on pull requests to main.

## Configuration & Secrets

- Environment variables via `.env` file (never committed)
- `.env.example` provided as template
- `SECRET_KEY` for Flask sessions
- `DATABASE_URL` for PostgreSQL connection
- `.gitignore` excludes `.env`, `.coverage`, `__pycache__`, `venv/`
- Pre-commit hooks detect private keys before commit

## Multithreading

Background reminder scheduler (`app/scheduler.py`):
- **Daemon thread** runs alongside Flask, checking reminders every 60 seconds
- **Thread-safe queue** with `threading.Lock` for notification passing between threads
- **Producer-consumer pattern**: request threads add reminders (producer), scheduler thread checks and fires them (consumer), notification endpoint retrieves them

## License

MIT License — see [LICENSE](LICENSE)
