# FitTracker

Уеб приложение за фитнес проследяване, изградено с Flask и PostgreSQL. FitTracker помага на потребителите да управляват тренировките си, да следят храненето, да наблюдават телесния състав и да спазват графика си с напомняния.

## Функционалности

- **Планиране на тренировки** — Автоматично генерирани седмични програми според фитнес целите, с проследяване на завършени упражнения
- **Калориен тракер** — Дневен дневник за храна с автоматично търсене на хранителни стойности чрез USDA API, проследяване на макроси (протеин/въглехидрати/мазнини), седмични графики
- **BMI калкулатор** — Интерактивен калкулатор за индекс на телесна маса с SVG визуализация
- **Графики за прогрес** — Chart.js графики за тегло, дневни калории и обем на тренировките
- **Напомняния** — Настройваеми фитнес напомняния с фонов scheduler thread
- **Потребителски профили** — Регистрация с телесни показатели, BMR/TDEE изчисление, ниво на активност

## Архитектура

FitTracker използва **MVC (Model-View-Controller)** архитектура чрез Flask Blueprints:

```
app/
├── __init__.py          # Application factory (създаване на Flask приложение)
├── models.py            # Data слой — SQLAlchemy ORM модели
├── routes/
│   ├── auth.py          # Controller — автентикация (вход, регистрация, изход)
│   └── main.py          # Controller — основни маршрути (тренировки, калории, BMI и др.)
├── templates/           # View слой — Jinja2 HTML шаблони
│   ├── base.html        # Базов шаблон с навигация
│   ├── dashboard.html   # Табло с BMI, калории, профил
│   ├── workout.html     # Седмична тренировъчна програма
│   ├── calories.html    # Калориен тракер с AI търсене
│   ├── bmi.html         # BMI калкулатор с SVG скала
│   ├── progress.html    # Chart.js графики за прогрес
│   └── reminders.html   # Управление на напомняния
├── static/
│   └── style.css        # Dark theme CSS стилове
├── services.py          # Бизнес логика — сервиз за генериране на тренировки
├── strategies.py        # Strategy pattern — конфигурации за различни цели
├── exercises.py         # База данни с упражнения и селектор
├── exceptions.py        # Йерархия от custom exceptions
├── scheduler.py         # Фонов thread за напомняния (multithreading)
└── forms.py             # Flask-WTF дефиниции на форми
```

## Шаблони за проектиране (Design Patterns)

### 1. Strategy Pattern (`app/strategies.py`)
**Проблем:** Различните фитнес цели (отслабване, качване на мускулна маса, поддържане) изискват напълно различни конфигурации за тренировки — брой повторения, почивка, кардио, избор на упражнения.

**Решение:** Всяка цел е капсулирана в собствен клас-стратегия, имплементиращ общ интерфейс `WorkoutStrategy`. Добавянето на нова цел означава създаване на нов клас без промяна на съществуващия код.

### 2. Factory Pattern (`app/strategies.py` — `StrategyFactory`)
**Проблем:** Клиентският код трябва да създаде правилната стратегия на база текстов вход (избраната от потребителя цел), без да познава всички конкретни класове.

**Решение:** `StrategyFactory.create(goal)` свързва текстовите цели към инстанции на стратегии, централизирайки създаването на обекти.

### 3. Dependency Injection (`app/routes/main.py` + `app/services.py`)
**Проблем:** `WorkoutService` не трябва да е тясно свързан с конкретна имплементация на стратегия.

**Решение:** Стратегията се инжектира в `WorkoutService(strategy=strategy)` по време на изпълнение. Сервизът зависи от абстракцията, а не от конкретния клас.

## SOLID принципи

| Принцип | Къде е приложен | Пример |
|---------|----------------|--------|
| **SRP** — Единствена отговорност | `strategies.py`, `services.py` | Всяка стратегия обработва само конфигурацията за своята цел; `WorkoutService` само генерира програми |
| **OCP** — Отворен/Затворен | `strategies.py` | Нови фитнес цели = нов клас стратегия, нула промени в съществуващия код |
| **LSP** — Заместване на Лисков | Подкласове на `WorkoutStrategy` | Всяка стратегия може да замести друга — `LoseWeightStrategy` и `GainMuscleStrategy` са взаимозаменяеми |
| **ISP** — Разделяне на интерфейси | `WorkoutStrategy` ABC | Интерфейсът дефинира само `get_config()` — стратегиите не са принудени да имплементират ненужни методи |
| **DIP** — Инверсия на зависимости | `services.py` | `WorkoutService` зависи от абстрактен `WorkoutStrategy`, не от конкретни имплементации |

## ООП принципи

- **Наследяване:** `FitTrackerError` → `InvalidProfileError`, `WorkoutGenerationError`; `WorkoutStrategy` → конкретни стратегии
- **Полиморфизъм:** `get_config()` на всяка стратегия връща различни конфигурации; `bmi_category` property връща различни низове
- **Капсулация:** User моделът скрива хеширането на пароли (`set_password`/`check_password`); вътрешната логика на стратегиите е зад `get_config()`
- **Абстракция:** `WorkoutStrategy` ABC дефинира интерфейс; Flask blueprints абстрахират групирането на маршрути

## Използвани технологии

| Технология | Версия | Предназначение |
|-----------|--------|----------------|
| Python | 3.12+ | Език за програмиране (backend) |
| Flask | 3.1.1 | Уеб framework |
| PostgreSQL | 17 | Релационна база данни |
| SQLAlchemy | 2.x | ORM |
| Flask-Migrate | 4.1.0 | Миграции на базата данни (Alembic) |
| Flask-Login | 0.6.3 | Автентикация и сесии |
| Flask-WTF | 1.2.2 | Обработка на форми и CSRF защита |
| Chart.js | 4.4.4 | Графики от страна на клиента |
| Bootstrap | 5.3.3 | Responsive CSS framework |
| Docker | - | Контейнеризация |
| GitHub Actions | - | CI/CD pipeline |
| Gunicorn | 23.0.0 | Production WSGI сървър |
| pytest | 8.3.4 | Unit и интеграционно тестване |
| flake8 | 7.1.0 | Статичен анализ на кода |
| pre-commit | 4.0.1 | Управление на Git hooks |

## API Endpoints

### Автентикация
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET/POST | `/register` | Многостъпкова регистрация |
| GET/POST | `/login` | Вход в системата |
| GET | `/logout` | Изход от системата |

### Тренировки
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/workout` | Преглед на активна тренировъчна програма |
| GET | `/workout/regenerate` | Генериране на нова програма |
| POST | `/workout/toggle/<id>` | Превключване на завършеност на упражнение |
| POST | `/workout/reset-day/<id>` | Нулиране на всички упражнения за деня |
| GET | `/workout/history` | Преглед на минали програми |

### Калории
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/calories` | Дневен калориен тракер с графики |
| POST | `/calories/add` | Добавяне на хранителен запис |
| POST | `/calories/delete/<id>` | Изтриване на хранителен запис |
| POST | `/calories/lookup` | AI търсене на хранителни стойности (USDA API) |

### BMI
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET/POST | `/bmi` | BMI калкулатор с визуална скала |

### Прогрес
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/progress` | Графики за тегло, калории и обем |
| POST | `/progress/weight` | Записване на тегло |

### Напомняния
| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/reminders` | Преглед на всички напомняния |
| POST | `/reminders/add` | Създаване на напомняне |
| POST | `/reminders/toggle/<id>` | Превключване на напомняне ВКЛ/ИЗКЛ |
| POST | `/reminders/delete/<id>` | Изтриване на напомняне |
| GET | `/notifications` | Получаване на изчакващи нотификации (от scheduler) |

## Схема на базата данни

PostgreSQL със 7 нормализирани таблици:

- **users** — Информация за акаунт, телесни показатели, фитнес цели
- **workout_plans** — Генерирани тренировъчни програми за потребител
- **workout_days** — Дни в рамките на програма (Пон-Нед)
- **workout_exercises** — Упражнения в рамките на ден
- **food_entries** — Дневни записи за храна с макроси
- **weight_logs** — Исторически измервания на тегло
- **reminders** — Графици за напомняния на потребители

ORM: SQLAlchemy с `lazy="dynamic"` за големи колекции и `lazy="select"` за малки свързани набори. Всички миграции се управляват чрез Flask-Migrate (Alembic).

## Стартиране на проекта

### Изисквания
- Python 3.12+
- PostgreSQL 17+
- Docker (по избор)

### Вариант 1: Docker (Препоръчителен)
```bash
git clone https://github.com/TUES-2026-PBL-11-klas/SMES-FitTracker.git
cd SMES-FitTracker
docker-compose up --build
```
Приложението работи на http://localhost:5000

### Вариант 2: Локална разработка
```bash
# Клониране и инсталиране
git clone https://github.com/TUES-2026-PBL-11-klas/SMES-FitTracker.git
cd SMES-FitTracker
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# Настройка на базата данни
cp .env.example .env         # Редактирайте DATABASE_URL ако е необходимо
flask db upgrade

# Стартиране
flask run --debug
```

### Пускане на тестове
```bash
pytest --cov=app --cov-report=term-missing -v
```
Текущо покритие: **81%** (43 теста — unit + интеграционни)

### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci.yml`):

1. **Test** — Пускане на pytest с PostgreSQL service container, минимум 50% покритие
2. **Lint** — Проверка за стил на кода с flake8
3. **Docker** — Изграждане и верификация на Docker образ

Задейства се при push към main и feature branch-ове, и при pull requests към main.

## Управление на конфигурация и тайни

- Променливи на средата чрез `.env` файл (никога не се качва в git)
- `.env.example` предоставен като шаблон
- `SECRET_KEY` за Flask сесии
- `DATABASE_URL` за PostgreSQL връзка
- `.gitignore` изключва `.env`, `.coverage`, `__pycache__`, `venv/`
- Pre-commit hooks засичат частни ключове преди commit

## Multithreading

Фонов scheduler за напомняния (`app/scheduler.py`):
- **Daemon thread** работи паралелно с Flask, проверявайки напомняния на всеки 60 секунди
- **Thread-safe опашка** с `threading.Lock` за предаване на нотификации между нишки
- **Producer-consumer pattern**: нишки от заявки добавят напомняния (producer), scheduler нишката ги проверява и задейства (consumer), endpoint за нотификации ги извлича

## Лиценз

MIT License — виж [LICENSE](LICENSE)
