"""Custom permissions for Foodgram API."""
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на изменение только владельцам объекта.
    НЕ включает проверку аутентификации - используется отдельно.
    """
    
    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения на уровне объекта."""
        # Разрешения на чтение для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешения на запись только для владельца
        return obj.author == request.user


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение для авторов рецептов.
    НЕ включает проверку аутентификации - используется отдельно.
    """
    
    def has_object_permission(self, request, view, obj):
        """Проверяет разрешения на уровне объекта."""
        # Разрешения на чтение для всех
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Разрешения на запись только для автора
        return getattr(obj, 'author', None) == request.user 