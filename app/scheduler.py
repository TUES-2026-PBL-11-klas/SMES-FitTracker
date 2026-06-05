"""
Background reminder scheduler using multithreading.

Demonstrates:
- Multithreading with a daemon background thread
- Thread-safe access to shared data via threading.Lock
- Producer-consumer pattern: routes produce reminders, scheduler consumes them
"""

import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Thread-safe notification queue (shared between request threads and scheduler)
_lock = threading.Lock()
_pending_notifications = []


def add_notification(user_id, message):
    """Thread-safe: add a notification (called from request threads — producer)."""
    with _lock:
        _pending_notifications.append({
            "user_id": user_id,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        })
        logger.info("Notification queued for user %s: %s", user_id, message)


def get_notifications(user_id):
    """Thread-safe: retrieve and clear notifications for a user (consumer)."""
    with _lock:
        user_notifs = [n for n in _pending_notifications if n["user_id"] == user_id]
        for n in user_notifs:
            _pending_notifications.remove(n)
        return user_notifs


def _check_reminders(app):
    """Background thread: periodically check for due reminders."""
    import time
    logger.info("Reminder scheduler started (checking every 60s)")

    while True:
        try:
            time.sleep(60)  # Check every minute

            with app.app_context():
                from app.models import Reminder

                now = datetime.now()
                current_day = now.strftime("%A").lower()
                current_time = now.strftime("%H:%M")

                reminders = Reminder.query.filter_by(is_active=True).all()

                for r in reminders:
                    reminder_time = r.time.strftime("%H:%M")
                    day_match = (
                        r.day_of_week == "everyday"
                        or r.day_of_week == current_day
                    )

                    if day_match and reminder_time == current_time:
                        add_notification(r.user_id, r.title)
                        logger.info(
                            "Reminder fired: '%s' for user %s",
                            r.title, r.user_id
                        )

        except Exception as e:
            logger.error("Scheduler error: %s", e)


def start_scheduler(app):
    """Start the background reminder checker as a daemon thread."""
    scheduler_thread = threading.Thread(
        target=_check_reminders,
        args=(app,),
        daemon=True,  # Dies when main thread exits
        name="ReminderScheduler",
    )
    scheduler_thread.start()
    logger.info("Background scheduler thread started: %s", scheduler_thread.name)
