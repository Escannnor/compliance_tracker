"""
apps/tasks/tests.py

Unit tests for the tasks app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import ComplianceTask
from .serializers import ComplianceTaskSerializer
from .filters import TaskFilter

User = get_user_model()


class ComplianceTaskModelTest(TestCase):
    """Test the ComplianceTask model"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role="admin"
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            role="staff"
        )
    
    def test_create_task(self):
        """Test that a task can be created"""
        task = ComplianceTask.objects.create(
            title="Test Task",
            description="Test description",
            status="pending",
            priority="high",
            deadline="2026-12-31T17:00:00Z",
            organisation="TestOrg",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "pending")
        self.assertEqual(task.priority, "high")
    
    def test_task_str_representation(self):
        """Test the string representation of a task"""
        task = ComplianceTask.objects.create(
            title="Test Task",
            created_by=self.admin_user
        )
        self.assertEqual(str(task), "Test Task")


class ComplianceTaskSerializerTest(TestCase):
    """Test the ComplianceTaskSerializer"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role="admin"
        )
    
    def test_valid_task_serialization(self):
        """Test that valid task data is serialized correctly"""
        task = ComplianceTask.objects.create(
            title="Test Task",
            description="Test description",
            status="pending",
            priority="high",
            deadline="2026-12-31T17:00:00Z",
            organisation="TestOrg",
            created_by=self.admin_user
        )
        serializer = ComplianceTaskSerializer(task)
        data = serializer.data
        
        self.assertEqual(data["title"], "Test Task")
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["priority"], "high")
    
    def test_task_validation(self):
        """Test that invalid task data is rejected"""
        data = {
            "title": "",  # Empty title should fail
            "status": "invalid_status"  # Invalid status
        }
        serializer = ComplianceTaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class TaskFilterTest(TestCase):
    """Test the TaskFilter"""
    
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role="admin"
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            role="staff"
        )
        
        # Create test tasks
        self.task1 = ComplianceTask.objects.create(
            title="Audit Report",
            description="Annual audit",
            status="pending",
            priority="critical",
            organisation="Smartcomply",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        
        self.task2 = ComplianceTask.objects.create(
            title="Security Review",
            description="Security assessment",
            status="completed",
            priority="high",
            organisation="Smartcomply",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        
        self.task3 = ComplianceTask.objects.create(
            title="Compliance Check",
            description="Regular compliance check",
            status="pending",
            priority="medium",
            organisation="OtherOrg",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
    
    def test_filter_by_status(self):
        """Test filtering by status"""
        queryset = ComplianceTask.objects.all()
        filter_obj = TaskFilter({"status": "pending"}, queryset=queryset)
        results = filter_obj.qs
        
        self.assertEqual(results.count(), 2)
        self.assertTrue(all(task.status == "pending" for task in results))
    
    def test_filter_by_priority(self):
        """Test filtering by priority"""
        queryset = ComplianceTask.objects.all()
        filter_obj = TaskFilter({"priority": "critical"}, queryset=queryset)
        results = filter_obj.qs
        
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().priority, "critical")
    
    def test_filter_by_organisation(self):
        """Test filtering by organisation"""
        queryset = ComplianceTask.objects.all()
        filter_obj = TaskFilter({"organisation": "Smartcomply"}, queryset=queryset)
        results = filter_obj.qs
        
        self.assertEqual(results.count(), 2)
        self.assertTrue(all("smartcomply" in task.organisation.lower() for task in results))
    
    def test_search_filter(self):
        """Test the search filter"""
        queryset = ComplianceTask.objects.all()
        filter_obj = TaskFilter({"search": "audit"}, queryset=queryset)
        results = filter_obj.qs
        
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().title, "Audit Report")


class TaskAPITest(TestCase):
    """Test the task API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="password123",
            role="admin"
        )
        self.staff_user = User.objects.create_user(
            username="staff",
            email="staff@example.com",
            password="password123",
            role="staff"
        )
        
        # Get admin token
        response = self.client.post("/api/auth/login/", {
            "username": "admin",
            "password": "password123"
        })
        self.admin_token = response.data["access"]
        
        # Get staff token
        response = self.client.post("/api/auth/login/", {
            "username": "staff",
            "password": "password123"
        })
        self.staff_token = response.data["access"]
    
    def test_admin_can_create_task(self):
        """Test that admin can create tasks"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        
        data = {
            "title": "New Task",
            "description": "New task description",
            "priority": "high",
            "deadline": "2026-12-31T17:00:00Z",
            "organisation": "TestOrg"
        }
        response = self.client.post("/api/tasks/", data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ComplianceTask.objects.count(), 1)
    
    def test_staff_cannot_create_task(self):
        """Test that staff cannot create tasks"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staff_token}")
        
        data = {
            "title": "New Task",
            "description": "New task description",
            "priority": "high",
            "deadline": "2026-12-31T17:00:00Z",
            "organisation": "TestOrg"
        }
        response = self.client.post("/api/tasks/", data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_admin_sees_all_tasks(self):
        """Test that admin sees all tasks"""
        # Create some tasks
        ComplianceTask.objects.create(
            title="Task 1",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        ComplianceTask.objects.create(
            title="Task 2",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/tasks/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
    
    def test_staff_sees_only_assigned_tasks(self):
        """Test that staff sees only their assigned tasks"""
        # Create tasks assigned to staff user
        ComplianceTask.objects.create(
            title="Assigned Task",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        # Create task assigned to someone else
        other_user = User.objects.create_user(
            username="other",
            email="other@example.com",
            password="password123",
            role="staff"
        )
        ComplianceTask.objects.create(
            title="Other Task",
            created_by=self.admin_user,
            assigned_to=other_user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staff_token}")
        response = self.client.get("/api/tasks/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["title"], "Assigned Task")
    
    def test_task_filtering(self):
        """Test that task filtering works"""
        # Create tasks with different statuses
        ComplianceTask.objects.create(
            title="Pending Task",
            status="pending",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        ComplianceTask.objects.create(
            title="Completed Task",
            status="completed",
            created_by=self.admin_user,
            assigned_to=self.staff_user
        )
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        
        # Filter by pending status
        response = self.client.get("/api/tasks/?status=pending")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["status"], "pending")
    
    def test_task_pagination(self):
        """Test that task pagination works"""
        # Create more than 10 tasks
        for i in range(15):
            ComplianceTask.objects.create(
                title=f"Task {i}",
                created_by=self.admin_user,
                assigned_to=self.staff_user
            )
        
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get("/api/tasks/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 10)  # Default page size
        self.assertIsNotNone(response.data["next"])  # Should have next page
