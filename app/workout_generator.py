"""
Backward-compatible wrapper for workout generation.

The actual logic is now in:
- app/strategies.py  (Strategy + Factory patterns)
- app/services.py    (Service layer with DI and threading)
- app/exercises.py   (Exercise data - SRP)
"""

from app.services import generate_workout  # noqa: F401
