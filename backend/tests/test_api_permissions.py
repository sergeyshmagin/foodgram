"""Тесты разрешений API для Foodgram."""
import pytest
from rest_framework.test import APIRequestFactory

from apps.api.permissions import IsAuthorOrReadOnly


@pytest.mark.django_db
class TestIsAuthorOrReadOnly:
    """Тесты разрешения IsAuthorOrReadOnly."""
    
    def setup_method(self):
        """Настройка для каждого теста."""
        self.permission = IsAuthorOrReadOnly()
        self.factory = APIRequestFactory()
    
    def test_safe_methods_allowed_for_any_user(self, user, recipe):
        """Тест доступа на чтение для любого пользователя."""
        request = self.factory.get('/')
        request.user = user
        
        assert self.permission.has_object_permission(request, None, recipe)
    
    def test_author_can_modify_object(self, user, recipe):
        """Тест доступа автора на изменение объекта."""
        request = self.factory.post('/')
        request.user = user  # user является автором recipe
        
        assert self.permission.has_object_permission(request, None, recipe)
    
    def test_non_author_cannot_modify_object(self, another_user, recipe):
        """Тест запрета изменения объекта не автором."""
        request = self.factory.post('/')
        request.user = another_user  # another_user НЕ является автором recipe
        
        assert not self.permission.has_object_permission(request, None, recipe)
