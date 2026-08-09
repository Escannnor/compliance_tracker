"""
apps/users/tests.py

Unit tests for the users app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class RegisterSerializerTest(TestCase):
    """Test the RegisterSerializer"""
    
    def test_valid_registration(self):
        """Test that valid registration data creates a user"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "organisation": "TestOrg"
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.role, "staff")  # Should default to staff
        self.assertTrue(user.check_password("password123"))
    
    def test_role_is_ignored(self):
        """Test that role field is ignored during registration"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "admin"  # This should be ignored
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        user = serializer.save()
        self.assertEqual(user.role, "staff")  # Should still be staff
    
    def test_password_min_length(self):
        """Test that password must be at least 8 characters"""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"  # Too short
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class UserSerializerTest(TestCase):
    """Test the UserSerializer"""
    
    def test_user_serialization(self):
        """Test that user data is serialized correctly"""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123",
            role="admin"
        )
        serializer = UserSerializer(user)
        data = serializer.data
        
        self.assertEqual(data["username"], "testuser")
        self.assertEqual(data["email"], "test@example.com")
        self.assertEqual(data["role"], "admin")
        self.assertNotIn("password", data)  # Password should not be in output


class RegistrationAPITest(TestCase):
    """Test the registration API endpoint"""
    
    def setUp(self):
        self.client = APIClient()
    
    def test_registration_endpoint(self):
        """Test that registration endpoint creates a user"""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "organisation": "NewOrg"
        }
        response = self.client.post("/api/users/register/", data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.get(username="newuser")
        self.assertEqual(user.role, "staff")
    
    def test_duplicate_username(self):
        """Test that duplicate usernames are rejected"""
        User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
        
        data = {
            "username": "testuser",  # Duplicate
            "email": "different@example.com",
            "password": "password123"
        }
        response = self.client.post("/api/users/register/", data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)


class LoginAPITest(TestCase):
    """Test the login API endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="password123"
        )
    
    def test_login_with_valid_credentials(self):
        """Test that login works with valid credentials"""
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post("/api/auth/login/", data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
    
    def test_login_with_invalid_credentials(self):
        """Test that login fails with invalid credentials"""
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post("/api/auth/login/", data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
