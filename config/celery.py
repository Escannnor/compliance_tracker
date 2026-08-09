"""
config/celery.py — Celery setup.

Celery is a task queue. Instead of making the user wait for slow operations
(like sending emails or checking 1000 deadlines), you push the job to Celery,
it goes into Redis, and a background worker picks it up and runs it.

Flow:
  your_view.py calls send_deadline_reminders.delay()
       ↓
  Job is stored in Redis queue
       ↓
  Celery worker picks it up and runs it in the background
       ↓
  User never waited
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("compliance_tracker")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py files inside all installed apps
app.autodiscover_tasks()
