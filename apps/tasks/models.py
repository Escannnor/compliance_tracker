"""
apps/tasks/models.py

This is the main model of the project.
Each ComplianceTask row = one compliance task in the database.

Django automatically creates an `id` primary key for every model.
ForeignKey = a relationship to another table (like a JOIN in SQL).
"""

from django.db import models
from django.conf import settings


class ComplianceTask(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        OVERDUE = "overdue", "Overdue"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    deadline = models.DateTimeField()
    organisation = models.CharField(max_length=255)

    # ForeignKey links this task to a User.
    # If the assigned user is deleted, the task remains (SET_NULL).
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)  # set once on creation
    updated_at = models.DateTimeField(auto_now=True)       # updated on every save

    class Meta:
        ordering = ["-created_at"]  # newest tasks first by default

    def __str__(self):
        return f"{self.title} [{self.status}]"
