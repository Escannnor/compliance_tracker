"""
settings.py — All Django configuration lives here.
Think of this like your .env + app config combined.
"""

from decouple import config
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-in-production")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = ["*"]

# ── Apps ──────────────────────────────────────────────────────────────────────
# Django needs to know which apps exist in your project.
# Think of each app as a feature module.
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework",           # Django REST Framework — turns Django into an API
    "rest_framework_simplejwt", # JWT authentication
    "drf_spectacular",          # API documentation (Swagger UI)
    "django_filters",           # Filtering support
    # Our apps
    "apps.users",
    "apps.tasks",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
AUTH_USER_MODEL = "users.User"  # tells Django to use our custom User model

# ── Database ──────────────────────────────────────────────────────────────────
# Django's ORM will talk to PostgreSQL using these credentials.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="compliance_db"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# ── Redis Cache ───────────────────────────────────────────────────────────────
# This tells Django to use Redis as its cache backend.
# django-redis is the library that connects them.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT": 60,  # cache expires after 60 seconds
    }
}

# ── Celery ────────────────────────────────────────────────────────────────────
# Celery uses Redis as a "broker" — a queue to store background jobs.
# When you call a Celery task, it goes into Redis first, then Celery picks it up.
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

# ── DRF Configuration ─────────────────────────────────────────────────────────
# This tells DRF to use JWT for authentication on all endpoints by default.
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# JWT token settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# ── API Documentation (drf-spectacular) ────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "Compliance Tracker API",
    "DESCRIPTION": "A REST API for managing compliance tasks with PostgreSQL, Redis, and Celery",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates",
              "DIRS": [], "APP_DIRS": True,
              "OPTIONS": {"context_processors": [
                  "django.template.context_processors.debug",
                  "django.template.context_processors.request",
                  "django.contrib.auth.context_processors.auth",
                  "django.contrib.messages.context_processors.messages",
              ]}}]

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_TZ = True
