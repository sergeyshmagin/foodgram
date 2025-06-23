"""Тесты сериализаторов API для Foodgram."""
import pytest
from django.contrib.auth import get_user_model

from apps.api.serializers import (
    UserSerializer, TagSerializer, IngredientSerializer,
    RecipeCreateUpdateSerializer, RecipeMinifiedSerializer
)

User = get_user_model()


@pytest.mark.django_db
class TestUserSerializer:
    """Тесты сериализатора пользователей."""
    
    def test_user_serialization(self, user):
        """Тест сериализации пользователя."""
        serializer = UserSerializer(user)
        data = serializer.data
        
        assert data['id'] == user.id
        assert data['email'] == user.email
        assert data['username'] == user.username
        assert 'is_subscribed' in data


@pytest.mark.django_db
class TestTagSerializer:
    """Тесты сериализатора тегов."""
    
    def test_tag_serialization(self, tag):
        """Тест сериализации тега."""
        serializer = TagSerializer(tag)
        data = serializer.data
        
        assert data['id'] == tag.id
        assert data['name'] == tag.name
        assert data['slug'] == tag.slug


@pytest.mark.django_db
class TestIngredientSerializer:
    """Тесты сериализатора ингредиентов."""
    
    def test_ingredient_serialization(self, ingredient):
        """Тест сериализации ингредиента."""
        serializer = IngredientSerializer(ingredient)
        data = serializer.data
        
        assert data['id'] == ingredient.id
        assert data['name'] == ingredient.name
        assert data['measurement_unit'] == ingredient.measurement_unit


@pytest.mark.django_db
class TestRecipeCreateUpdateSerializer:
    """Тесты сериализатора создания/обновления рецептов."""
    
    def test_recipe_creation_invalid_cooking_time(self, tag, ingredient):
        """Тест создания рецепта с невалидным временем приготовления."""
        data = {
            'name': 'Тестовый рецепт',
            'text': 'Описание рецепта',
            'cooking_time': 0,  # Невалидное значение
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'tags': [tag.id],
            'ingredients': [
                {'id': ingredient.id, 'amount': 100}
            ]
        }
        
        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'cooking_time' in serializer.errors
    
    def test_recipe_creation_empty_ingredients(self, tag):
        """Тест создания рецепта без ингредиентов."""
        data = {
            'name': 'Тестовый рецепт',
            'text': 'Описание рецепта',
            'cooking_time': 30,
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==',
            'tags': [tag.id],
            'ingredients': []  # Пустой список
        }
        
        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'ingredients' in serializer.errors


@pytest.mark.django_db
class TestRecipeMinifiedSerializer:
    """Тесты минифицированного сериализатора рецептов."""
    
    def test_recipe_minified_serialization(self, recipe):
        """Тест минифицированной сериализации рецепта."""
        serializer = RecipeMinifiedSerializer(recipe)
        data = serializer.data
        
        assert data['id'] == recipe.id
        assert data['name'] == recipe.name
        assert data['cooking_time'] == recipe.cooking_time
        assert 'image' in data
