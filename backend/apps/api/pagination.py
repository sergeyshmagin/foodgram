"""Кастомные пагинаторы для API."""
from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомный пагинатор с поддержкой параметра limit."""

    page_size = 6
    page_size_query_param = "limit"  # Используем 'limit' вместо 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Возвращает пагинированный ответ."""
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
