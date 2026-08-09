"""
apps/tasks/pagination.py

Custom pagination class that exposes page_size parameter in API schema.
"""

from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    """
    Custom pagination for tasks with configurable page size.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
