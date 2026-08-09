#!/usr/bin/env python
"""Django's command-line utility for administrative tasks.

Common commands:
  python manage.py runserver          → start the dev server
  python manage.py makemigrations     → create migration files from model changes
  python manage.py migrate            → apply migrations to the database
  python manage.py createsuperuser    → create an admin user
  python manage.py shell              → open a Python shell with Django loaded
"""
import os
import sys

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django not installed.") from exc
    execute_from_command_line(sys.argv)

if __name__ == "__main__":
    main()
