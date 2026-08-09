"""
config/urls.py — The root URL file.
Every URL in your project is registered here.
Django reads this file top to bottom to match incoming requests.
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),  # Django's built-in admin panel

    # API Documentation (Swagger UI)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # JWT auth endpoints
    # POST /api/auth/login/   → returns access + refresh token
    # POST /api/auth/refresh/ → returns new access token
    path("api/auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="refresh"),

    # App URLs — each app manages its own URLs
    path("api/users/", include("apps.users.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
]
