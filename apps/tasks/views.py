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
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ComplianceTask
from .serializers import ComplianceTaskSerializer

CACHE_KEY = "all_compliance_tasks"
CACHE_TTL = 60  # seconds


class IsAdminUser(permissions.BasePermission):
    """Custom permission — only Admin role can access."""
    def has_permission(self, request, view):
        return request.user.role == "admin"


class TaskListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        GET /api/tasks/
        Admins see all tasks. Staff see only their assigned tasks.
        Result is cached in Redis for 60 seconds.
        """
        # Step 1: check Redis first
        cached = cache.get(CACHE_KEY)
        if cached:
            # Cache hit — return immediately, no DB query
            return Response({"source": "cache", "data": cached})

        # Step 2: cache miss — query the database
        if request.user.role == "admin":
            tasks = ComplianceTask.objects.all()
        else:
            tasks = ComplianceTask.objects.filter(assigned_to=request.user)

        serializer = ComplianceTaskSerializer(tasks, many=True)

        # Step 3: store result in Redis so next request is instant
        cache.set(CACHE_KEY, serializer.data, CACHE_TTL)

        return Response({"source": "database", "data": serializer.data})

    def post(self, request):
        """
        POST /api/tasks/
        Only admins can create tasks.
        After creating, clear the cache so the list is fresh.
        """
        if request.user.role != "admin":
            return Response({"error": "Only admins can create tasks."}, status=403)

        serializer = ComplianceTaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            cache.delete(CACHE_KEY)  # clear stale cache
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            task = ComplianceTask.objects.get(pk=pk)
            # Staff can only view their own tasks
            if user.role != "admin" and task.assigned_to != user:
                return None, True  # forbidden
            return task, False
        except ComplianceTask.DoesNotExist:
            return None, False

    def get(self, request, pk):
        """GET /api/tasks/<id>/"""
        task, forbidden = self.get_object(pk, request.user)
        if forbidden:
            return Response({"error": "Access denied."}, status=403)
        if not task:
            return Response({"error": "Not found."}, status=404)
        return Response(ComplianceTaskSerializer(task).data)

    def patch(self, request, pk):
        """
        PATCH /api/tasks/<id>/
        Update a task. Clears cache after update.
        partial=True means only send the fields you want to change.
        """
        task, forbidden = self.get_object(pk, request.user)
        if forbidden:
            return Response({"error": "Access denied."}, status=403)
        if not task:
            return Response({"error": "Not found."}, status=404)

        serializer = ComplianceTaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache.delete(CACHE_KEY)  # clear stale cache
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """DELETE /api/tasks/<id>/ — admin only"""
        if request.user.role != "admin":
            return Response({"error": "Only admins can delete tasks."}, status=403)
        task, _ = self.get_object(pk, request.user)
        if not task:
            return Response({"error": "Not found."}, status=404)
        task.delete()
        cache.delete(CACHE_KEY)
        return Response(status=status.HTTP_204_NO_CONTENT)
