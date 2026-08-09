"""
apps/users/models.py

In Django, a Model is a Python class that represents a database table.
Each attribute on the class = a column in the table.

Django's ORM will:
  - Create the table from this class (via migrations)
  - Let you query it with Python: User.objects.filter(role="admin")
  - Handle relationships, validations, and more
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    We extend Django's built-in User model so we keep all the default
    fields (username, email, password, is_active etc.) and just add our own.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        STAFF = "staff", "Staff"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STAFF,
    )
    organisation = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
