"""
apps/tasks/views.py

This is where Redis caching happens.

cache.get(key)        → check if data exists in Redis
cache.set(key, data)  → store data in Redis
cache.delete(key)     → remove data from Redis (when task is updated/deleted)

Without caching:
  Request → Django → PostgreSQL → Response   (slow if many tasks)

With caching:
  Request → Django → Redis hit? → Response   (instant)
                          ↓ miss
                       PostgreSQL → store in Redis → Response
"""

from django.core.cache import cache
from rest_framework import generics, permissions, status, pagination, views
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters import rest_framework as filters
from .models import ComplianceTask
from .serializers import ComplianceTaskSerializer
from .filters import TaskFilter
from .pagination import TaskPagination

CACHE_KEY = "all_compliance_tasks"
CACHE_TTL = 60  # seconds


class IsAdminUser(permissions.BasePermission):
    """Custom permission — only Admin role can access."""
    def has_permission(self, request, view):
        return request.user.role == "admin"


class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplianceTaskSerializer
    pagination_class = TaskPagination
    filterset_class = TaskFilter

    def get_queryset(self):
        """
        Admins see all tasks. Staff see only their assigned tasks.
        Results can be filtered using query parameters.
        """
        queryset = ComplianceTask.objects.all()
        
        # Apply role-based filtering
        if self.request.user.role != "admin":
            queryset = queryset.filter(assigned_to=self.request.user)
        
        # Apply filters
        queryset = self.filterset_class(self.request.GET, queryset=queryset).qs
        
        return queryset

    def perform_create(self, serializer):
        """
        Only admins can create tasks.
        After creating, clear the cache so the list is fresh.
        """
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admins can create tasks.")
        serializer.save(created_by=self.request.user)
        cache.delete(CACHE_KEY)  # clear stale cache


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ComplianceTaskSerializer

    def get_queryset(self):
        """
        Admins can access all tasks. Staff can only access their assigned tasks.
        """
        if self.request.user.role == "admin":
            return ComplianceTask.objects.all()
        else:
            return ComplianceTask.objects.filter(assigned_to=self.request.user)

    def perform_update(self, serializer):
        """
        Update a task. Clears cache after update.
        """
        serializer.save()
        cache.delete(CACHE_KEY)  # clear stale cache

    def perform_destroy(self, instance):
        """
        Delete a task. Only admins can delete. Clears cache after deletion.
        """
        if self.request.user.role != "admin":
            raise PermissionDenied("Only admins can delete tasks.")
        instance.delete()
        cache.delete(CACHE_KEY)
