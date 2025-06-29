"""Configuration for pytest."""
import base64
import os
import tempfile

import django
import pytest
from apps.recipes.models import Ingredient, Recipe, Tag
from apps.users.models import Subscription
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

# Настройка Django перед импортом моделей
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "foodgram.settings.development"
)
django.setup()

User = get_user_model()

short_base64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)

# Создаем временную директорию для медиа-файлов в тестах
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


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
    """Фикстура для создания обычного пользователя."""
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="testpass123",
    )


@pytest.fixture
def another_user():
    """Фикстура для создания второго пользователя."""
    return User.objects.create_user(
        username="anotheruser",
        email="another@example.com",
        first_name="Another",
        last_name="User",
        password="anotherpass123",
    )


@pytest.fixture
def subscription(user, another_user):
    """Фикстура для создания подписки."""
    return Subscription.objects.create(user=user, author=another_user)


@pytest.fixture
def ingredient_in_recipe(recipe, ingredient):
    """Создает связь ингредиента с рецептом."""
    from apps.recipes.models import IngredientInRecipe

    return IngredientInRecipe.objects.get(recipe=recipe, ingredient=ingredient)


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
def tag():
    """Создает тестовый тег."""
    return Tag.objects.create(
        name="Завтрак", color="#FF0000", slug="breakfast"
    )


@pytest.fixture
def ingredient():
    """Создает тестовый ингредиент."""
    return Ingredient.objects.create(name="Мука", measurement_unit="г")


@pytest.fixture
def recipe(user, tag, ingredient):
    """Создает тестовый рецепт."""
    image = SimpleUploadedFile(
        name="test_image.jpg",
        content=base64.b64decode(short_base64.split(",")[1]),
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

    from apps.recipes.models import IngredientInRecipe

    IngredientInRecipe.objects.create(
        recipe=recipe, ingredient=ingredient, amount=100
    )

    return recipe


@pytest.fixture
def user_token(user):
    """Создает токен для пользователя."""
    token, created = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def authenticated_client(api_client, user_token):
    """Аутентифицированный API клиент."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {user_token.key}")
    return api_client


@pytest.fixture
def recipe_data(tag, ingredient):
    """Данные для создания рецепта."""
    return {
        "name": "Новый рецепт",
        "text": "Описание нового рецепта",
        "cooking_time": 45,
        "image": short_base64,
        "tags": [tag.id],
        "ingredients": [{"id": ingredient.id, "amount": 200}],
    }


@pytest.fixture
def superuser():
    """Фикстура для создания суперпользователя."""
    return User.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        password="adminpass123",
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


@pytest.fixture
def users_url():
    """URL для API пользователей."""
    return reverse("api:v1:users-list")


@pytest.fixture
def tags_url():
    """URL для API тегов."""
    return reverse("api:v1:tags-list")


@pytest.fixture
def ingredients_url():
    """URL для API ингредиентов."""
    return reverse("api:v1:ingredients-list")


@pytest.fixture
def recipes_url():
    """URL для API рецептов."""
    return reverse("api:v1:recipes-list")


@pytest.fixture
def recipe_detail_url(recipe):
    """URL для детального просмотра рецепта."""
    return reverse("api:v1:recipes-detail", kwargs={"pk": recipe.id})


@pytest.fixture
def health_check_url():
    """URL для проверки здоровья API."""
    return reverse("api:v1:health-check")


@pytest.fixture
def media_tmp(settings, tmp_path):
    """Фикстура для временного каталога медиа-файлов."""
    media_root = tmp_path / "media"
    media_root.mkdir()
    settings.MEDIA_ROOT = media_root
    return media_root
