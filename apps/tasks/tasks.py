"""
apps/tasks/tasks.py — Celery background jobs

@shared_task turns a regular Python function into a background job.

How to run it:
  Option 1 — call it immediately in background:
    check_overdue_tasks.delay()

  Option 2 — schedule it (in celery beat config):
    runs automatically every day at midnight

The function runs inside the Celery worker process, not the web server.
So the user never waits for it.
"""

from celery import shared_task
from django.utils import timezone
from .models import ComplianceTask


@shared_task
def check_overdue_tasks():
    """
    Finds all tasks past their deadline that aren't completed yet,
    and marks them as overdue.

    In a real app you'd also send an email here.
    """
    now = timezone.now()

    overdue = ComplianceTask.objects.filter(
        deadline__lt=now,           # deadline is in the past
        status__in=["pending", "in_progress"],  # not done yet
    )

    count = overdue.update(status=ComplianceTask.Status.OVERDUE)

    return f"{count} tasks marked as overdue."


@shared_task
def send_deadline_reminder(task_id):
    """
    Send a reminder for a specific task.
    Call this from a view: send_deadline_reminder.delay(task.id)
    """
    try:
        task = ComplianceTask.objects.get(id=task_id)
        # In production: send email to task.assigned_to.email
        print(f"REMINDER: Task '{task.title}' is due on {task.deadline}")
        return f"Reminder sent for task {task_id}"
    except ComplianceTask.DoesNotExist:
        return f"Task {task_id} not found"
