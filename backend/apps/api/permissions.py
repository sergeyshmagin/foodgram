"""Custom permissions for Foodgram API."""
from foodgram.constants import SAFE_HTTP_METHODS
from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение для авторов рецептов.
    НЕ включает проверку аутентификации - используется отдельно.
    """

    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения на уровне объекта."""
        # Разрешения на чтение для всех
        if request.method in SAFE_HTTP_METHODS:
            return True

        # Разрешения на запись только для автора
        return getattr(obj, "author", None) == request.user
