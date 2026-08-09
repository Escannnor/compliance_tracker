"""
apps/tasks/serializers.py
"""

from rest_framework import serializers
from .models import ComplianceTask


class ComplianceTaskSerializer(serializers.ModelSerializer):
    # read_only=True means this field is shown in responses but not required in requests
    created_by = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = ComplianceTask
        fields = [
            "id", "title", "description", "status", "priority",
            "deadline", "organisation", "assigned_to", "assigned_to_id",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
