"""
apps/tasks/filters.py

Custom filters for the ComplianceTask model.
Allows filtering tasks by various fields via query parameters.
"""

from django_filters import rest_framework as filters
from .models import ComplianceTask


class TaskFilter(filters.FilterSet):
    """
    Filter tasks by:
    - status: pending, in_progress, completed, overdue
    - priority: low, medium, high, critical
    - organisation: company name
    - assigned_to: user ID
    - search: search in title and description
    """
    
    status = filters.CharFilter(field_name='status', lookup_expr='exact')
    priority = filters.CharFilter(field_name='priority', lookup_expr='exact')
    organisation = filters.CharFilter(field_name='organisation', lookup_expr='icontains')
    assigned_to = filters.NumberFilter(field_name='assigned_to__id')
    
    # Search filter - searches in both title and description
    search = filters.CharFilter(method='filter_search')
    
    class Meta:
        model = ComplianceTask
        fields = ['status', 'priority', 'organisation', 'assigned_to']
    
    def filter_search(self, queryset, name, value):
        """
        Custom search method that searches in both title and description fields.
        """
        if value:
            return queryset.filter(
                title__icontains=value
            ) | queryset.filter(
                description__icontains=value
            )
        return queryset
