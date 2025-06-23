"""Global pytest configuration and fixtures."""
import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "foodgram.settings.development"
    )
    django.setup()

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.recipes.models import Tag, Ingredient, Recipe

User = get_user_model()

# Короткое base64 изображение для тестов
short_base64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """Автоматический доступ к БД во всех тестах."""
    pass


@pytest.fixture
def api_client():
    """Клиент для API тестирования."""
    return APIClient()


@pytest.fixture
def user():
    """Создает тестового пользователя."""
    return User.objects.create_user(
        email="test@example.com",
        username="testuser",
        first_name="Test",
        last_name="User",
        password="testpass123",
    )


@pytest.fixture
def another_user():
    """Другой тестовый пользователь для тестов подписок."""
    return User.objects.create_user(
        email="another@example.com",
        username="anotheruser",
        first_name="Another",
        last_name="User",
        password="anotherpass123",
    )


@pytest.fixture
def admin_user():
    """Создает администратора."""
    return User.objects.create_superuser(
        email="admin@example.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        password="adminpass123",
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """Аутентифицированный клиент."""
    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client


@pytest.fixture
def tag():
    """Создает тестовый тег."""
    return Tag.objects.create(
        name="Завтрак", color="#FF0000", slug="breakfast"
    )


@pytest.fixture
def ingredient():
    """Создает тестовый ингредиент."""
    return Ingredient.objects.create(name="Молоко", measurement_unit="мл")


@pytest.fixture
def recipe_data(tag, ingredient):
    """Данные для создания рецепта."""
    return {
        "name": "Новый рецепт",
        "text": "Описание нового рецепта",
        "cooking_time": 45,
        "image": short_base64,
        "tags": [tag.id],
        "ingredients": [{"id": ingredient.id, "amount": 100}],
    }


@pytest.fixture
def recipe(user, tag, ingredient):
    """Создает тестовый рецепт."""
    # Создаем тестовое изображение
    image = SimpleUploadedFile(
        name="test_image.jpg",
        content=b"fake_image_content",
        content_type="image/jpeg",
    )

    recipe = Recipe.objects.create(
        author=user,
        name="Тестовый рецепт",
        image=image,
        text="Описание тестового рецепта",
        cooking_time=30,
    )
    recipe.tags.add(tag)
    return recipe


# URL фикстуры
@pytest.fixture
def users_url():
    """URL для списка пользователей."""
    return "/api/v1/users/"


@pytest.fixture
def tags_url():
    """URL для списка тегов."""
    return "/api/v1/tags/"


@pytest.fixture
def ingredients_url():
    """URL для списка ингредиентов."""
    return "/api/v1/ingredients/"


@pytest.fixture
def recipes_url():
    """URL для списка рецептов."""
    return "/api/v1/recipes/"


@pytest.fixture
def recipe_detail_url(recipe):
    """URL для детальной информации о рецепте."""
    return f"/api/v1/recipes/{recipe.pk}/"


@pytest.fixture
def health_check_url():
    """URL для health check."""
    return "/api/v1/health/"


@pytest.fixture
def superuser():
    """Создает суперпользователя для тестов админки."""
    return User.objects.create_superuser(
        email="super@example.com",
        username="superuser",
        first_name="Super",
        last_name="User",
        password="superpass123",
    )


@pytest.fixture
def staff_user():
    """Создает staff пользователя для тестов админки."""
    return User.objects.create_user(
        email="staff@example.com",
        username="staffuser",
        first_name="Staff",
        last_name="User",
        password="staffpass123",
        is_staff=True,
    )
