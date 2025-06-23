"""Интеграционные тесты для Foodgram - полные сценарии пользователя."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

# Короткое base64 изображение для тестов
TEST_IMAGE_BASE64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@pytest.mark.django_db
class TestUserRegistrationFlow:
    """Интеграционные тесты регистрации пользователя."""

    def test_full_user_registration_flow(self, api_client):
        """Тест полного процесса регистрации пользователя."""
        # 1. Регистрация
        registration_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "newuserpass123",
        }
        response = api_client.post("/api/v1/users/", registration_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data

        # 2. Получение токена
        token_data = {
            "email": "newuser@example.com",
            "password": "newuserpass123",
        }
        response = api_client.post("/api/v1/auth/token/login/", token_data)
        assert response.status_code == status.HTTP_200_OK
        assert "auth_token" in response.data
        token = response.data["auth_token"]

        # 3. Проверка доступа с токеном
        api_client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = api_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "newuser@example.com"


@pytest.mark.django_db
class TestRecipeManagementFlow:
    """Интеграционные тесты управления рецептами."""

    def test_recipe_lifecycle(self, authenticated_client, tag, ingredient):
        """Тест жизненного цикла рецепта."""
        # 1. Создание рецепта
        recipe_data = {
            "name": "Интеграционный рецепт",
            "text": "Описание рецепта",
            "cooking_time": 45,
            "image": TEST_IMAGE_BASE64,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 250}],
        }
        response = authenticated_client.post(
            "/api/v1/recipes/", recipe_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED
        recipe_id = response.data["id"]

        # 2. Добавление в избранное
        response = authenticated_client.post(
            f"/api/v1/recipes/{recipe_id}/favorite/"
        )
        assert response.status_code == status.HTTP_201_CREATED

        # 3. Проверка в избранном
        response = authenticated_client.get("/api/v1/recipes/?is_favorited=1")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        # 4. Добавление в корзину
        response = authenticated_client.post(
            f"/api/v1/recipes/{recipe_id}/shopping_cart/"
        )
        assert response.status_code == status.HTTP_201_CREATED

        # 5. Скачивание списка покупок
        response = authenticated_client.get(
            "/api/v1/recipes/download_shopping_cart/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/plain; charset=utf-8"


@pytest.mark.django_db
class TestSubscriptionFlow:
    """Интеграционные тесты подписок."""

    def test_subscription_flow(
        self, authenticated_client, another_user, tag, ingredient
    ):
        """Тест подписки и просмотра рецептов автора."""
        # 1. Создаем рецепт от имени другого пользователя
        api_client = APIClient()
        api_client.force_authenticate(user=another_user)

        recipe_data = {
            "name": "Рецепт автора",
            "text": "Описание рецепта автора",
            "cooking_time": 30,
            "image": TEST_IMAGE_BASE64,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 100}],
        }
        response = api_client.post(
            "/api/v1/recipes/", recipe_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

        # 2. Подписываемся на автора
        response = authenticated_client.post(
            f"/api/v1/users/{another_user.id}/subscribe/"
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == another_user.email

        # 3. Проверяем список подписок
        response = authenticated_client.get("/api/v1/users/subscriptions/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestFilteringFlow:
    """Интеграционные тесты фильтрации."""

    def test_complex_filtering(self, authenticated_client, another_user):
        """Тест сложного сценария фильтрации."""
        from apps.recipes.models import Ingredient, Tag

        # Создаем тег и ингредиент
        tag = Tag.objects.create(name="Завтрак", slug="breakfast")
        ingredient = Ingredient.objects.create(
            name="Яйца", measurement_unit="шт"
        )

        # Создаем рецепт от другого пользователя
        api_client = APIClient()
        api_client.force_authenticate(user=another_user)

        recipe_data = {
            "name": "Омлет",
            "text": "Вкусный омлет",
            "cooking_time": 15,
            "image": TEST_IMAGE_BASE64,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 2}],
        }
        response = api_client.post(
            "/api/v1/recipes/", recipe_data, format="json"
        )
        assert response.status_code == status.HTTP_201_CREATED

        # Фильтрация по тегу
        response = authenticated_client.get(
            f"/api/v1/recipes/?tags={tag.slug}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

        # Фильтрация по автору
        response = authenticated_client.get(
            f"/api/v1/recipes/?author={another_user.id}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestErrorHandlingFlow:
    """Интеграционные тесты обработки ошибок."""

    def test_error_scenarios(self, authenticated_client, recipe):
        """Тест различных сценариев ошибок."""
        # Попытка добавить в избранное дважды
        response = authenticated_client.post(
            f"/api/v1/recipes/{recipe.id}/favorite/"
        )
        assert response.status_code == status.HTTP_201_CREATED

        response = authenticated_client.post(
            f"/api/v1/recipes/{recipe.id}/favorite/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Доступ к несуществующему рецепту
        response = authenticated_client.get("/api/v1/recipes/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
