from django.test import TestCase

# Create your tests here.

"""Tests for Foodgram API."""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.recipes.models import Tag, Ingredient, Recipe

User = get_user_model()


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """Автоматический доступ к БД во всех тестах."""
    pass


@pytest.fixture
def api_client():
    """API клиент для тестов."""
    return APIClient()


@pytest.fixture
def user():
    """Создает тестового пользователя."""
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        first_name='Test',
        last_name='User',
        password='testpass123'
    )


@pytest.fixture
def user_token(user):
    """Создает токен для пользователя."""
    token, created = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def authenticated_client(api_client, user_token):
    """Аутентифицированный API клиент."""
    api_client.credentials(HTTP_AUTHORIZATION=f'Token {user_token.key}')
    return api_client


@pytest.fixture
def tag():
    """Создает тестовый тег."""
    return Tag.objects.create(
        name='Завтрак',
        slug='breakfast'
    )


@pytest.fixture
def ingredient():
    """Создает тестовый ингредиент."""
    return Ingredient.objects.create(
        name='Мука',
        measurement_unit='г'
    )


class TestUserAPI:
    """Тесты для API пользователей."""
    
    def test_user_registration(self, api_client):
        """Тест регистрации пользователя."""
        url = reverse('api:users-list')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@example.com').exists()
    
    def test_user_list(self, api_client, user):
        """Тест получения списка пользователей."""
        url = reverse('api:users-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
    
    def test_user_detail(self, api_client, user):
        """Тест получения профиля пользователя."""
        url = reverse('api:users-detail', args=[user.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
    
    def test_current_user(self, authenticated_client, user):
        """Тест получения текущего пользователя."""
        url = reverse('api:users-me')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email


class TestAuthAPI:
    """Тесты для API аутентификации."""
    
    def test_token_login(self, api_client, user):
        """Тест получения токена авторизации."""
        url = reverse('api:users-login')  # Djoser endpoint
        data = {
            'email': user.email,
            'password': 'testpass123'
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'auth_token' in response.data
    
    def test_token_logout(self, authenticated_client):
        """Тест удаления токена."""
        url = reverse('api:users-logout')  # Djoser endpoint
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestTagAPI:
    """Тесты для API тегов."""
    
    def test_tag_list(self, api_client, tag):
        """Тест получения списка тегов."""
        url = reverse('api:tags-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == tag.name
    
    def test_tag_detail(self, api_client, tag):
        """Тест получения тега по ID."""
        url = reverse('api:tags-detail', args=[tag.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == tag.name


class TestIngredientAPI:
    """Тесты для API ингредиентов."""
    
    def test_ingredient_list(self, api_client, ingredient):
        """Тест получения списка ингредиентов."""
        url = reverse('api:ingredients-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == ingredient.name
    
    def test_ingredient_search(self, api_client):
        """Тест поиска ингредиентов по имени."""
        Ingredient.objects.create(name='Мука пшеничная', measurement_unit='г')
        Ingredient.objects.create(name='Молоко', measurement_unit='мл')
        
        url = reverse('api:ingredients-list')
        response = api_client.get(url, {'name': 'Мук'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert 'Мука' in response.data[0]['name']
    
    def test_ingredient_detail(self, api_client, ingredient):
        """Тест получения ингредиента по ID."""
        url = reverse('api:ingredients-detail', args=[ingredient.id])
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == ingredient.name


class TestRecipeAPI:
    """Тесты для API рецептов."""
    
    def test_recipe_list(self, api_client):
        """Тест получения списка рецептов."""
        url = reverse('api:recipes-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_recipe_create_unauthorized(self, api_client):
        """Тест создания рецепта неавторизованным пользователем."""
        url = reverse('api:recipes-list')
        data = {
            'name': 'Тестовый рецепт',
            'text': 'Описание рецепта',
            'cooking_time': 30
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
