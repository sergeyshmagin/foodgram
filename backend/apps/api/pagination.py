"""Кастомные пагинаторы для API."""
from foodgram.constants import MAX_PAGE_SIZE, RECIPES_PAGE_SIZE
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомный пагинатор с поддержкой параметра limit."""

    page_size = RECIPES_PAGE_SIZE
    page_size_query_param = "limit"  # Используем 'limit' вместо 'page_size'
    max_page_size = MAX_PAGE_SIZE
