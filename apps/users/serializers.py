"""
apps/users/serializers.py

A Serializer does two things:
  1. Converts a Model instance → JSON (for responses)
  2. Validates incoming JSON → Python data (for creating/updating records)

Think of it as the layer between your database and the outside world.
"""

from rest_framework import serializers
from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    # write_only=True means this field appears in input but never in output
    password = serializers.CharField(write_only=True, min_length=8)
    # read_only=True means this field appears in output but cannot be set by client
    role = serializers.CharField(read_only=True, default='staff')

    class Meta:
        model = User
        # Only these fields are accepted/returned
        # role is read_only to prevent privilege escalation during registration
        fields = ["id", "username", "email", "password", "role", "organisation"]

    def create(self, validated_data):
        # Force all self-registered users to be 'staff' by default
        # This prevents users from registering as 'admin'
        validated_data['role'] = 'staff'
        # create_user hashes the password — never store plain text passwords
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "organisation"]
