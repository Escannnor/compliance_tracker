"""
apps/users/views.py

A View is the function (or class) that runs when a URL is hit.
It receives the request, does something, and returns a response.

DRF gives us generic views that handle common patterns automatically.
"""

from rest_framework import generics, permissions
from .models import User
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Anyone can register — so permission_classes allows unauthenticated access.
    CreateAPIView handles POST automatically using the serializer.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """
    GET /api/users/me/
    Returns the currently logged-in user's profile.
    request.user is automatically set by JWT authentication middleware.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
