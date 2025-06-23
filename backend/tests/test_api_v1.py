"""Тесты API для Foodgram."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.recipes.models import Favorite, Recipe, ShoppingCart
from foodgram.constants import MAX_COOKING_TIME, MIN_COOKING_TIME

User = get_user_model()


@pytest.mark.django_db
class TestHealthCheck:
    """Тесты health check endpoint."""

    def test_health_check(self, api_client, health_check_url):
        """Тест health check endpoint."""
        response = api_client.get(health_check_url)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "v1"


@pytest.mark.django_db
class TestUserAPI:
    """Тесты пользовательского API."""

    def test_users_list(self, api_client, users_url, user):
        """Тест получения списка пользователей."""
        response = api_client.get(users_url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert response.data["count"] >= 1

    def test_user_registration(self, api_client, users_url):
        """Тест регистрации пользователя."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
        }

        response = api_client.post(users_url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "password" not in response.data
        assert response.data["email"] == user_data["email"]

    def test_set_password(self, authenticated_client, user):
        """Тест изменения пароля."""
        url = "/api/v1/users/set_password/"
        data = {
            "current_password": "testpass123",
            "new_password": "newpass123",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Проверяем, что пароль действительно изменился
        user.refresh_from_db()
        assert user.check_password("newpass123")

    def test_set_password_invalid_current(self, authenticated_client):
        """Тест изменения пароля с неверным текущим паролем."""
        url = "/api/v1/users/set_password/"
        data = {
            "current_password": "wrongpass",
            "new_password": "newpass123",
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверный текущий пароль" in str(response.data)

    def test_reset_password(self, api_client, user):
        """Тест сброса пароля."""
        url = "/api/v1/users/reset_password/"
        data = {"email": user.email}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "Инструкции отправлены на email" in str(response.data)

    def test_reset_password_nonexistent_user(self, api_client):
        """Тест сброса пароля для несуществующего пользователя."""
        url = "/api/v1/users/reset_password/"
        data = {"email": "nonexistent@example.com"}

        response = api_client.post(url, data, format="json")

        # Должен возвращать тот же ответ, чтобы не раскрывать
        # существование пользователя
        assert response.status_code == status.HTTP_200_OK
        assert "Инструкции отправлены на email" in str(response.data)


@pytest.mark.django_db
class TestTagAPI:
    """Тесты API тегов."""

    def test_tags_list(self, api_client, tags_url, tag):
        """Тест получения списка тегов."""
        response = api_client.get(tags_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["name"] == tag.name


@pytest.mark.django_db
class TestIngredientAPI:
    """Тесты API ингредиентов."""

    def test_ingredients_list(self, api_client, ingredients_url, ingredient):
        """Тест получения списка ингредиентов."""
        response = api_client.get(ingredients_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["name"] == ingredient.name

    def test_ingredients_search(self, api_client, ingredients_url, ingredient):
        """Тест поиска ингредиентов."""
        response = api_client.get(
            ingredients_url, {"name": ingredient.name[:3]}
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestRecipeAPI:
    """Тесты API рецептов."""

    def test_recipes_list(self, api_client, recipes_url, recipe):
        """Тест получения списка рецептов."""
        response = api_client.get(recipes_url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert response.data["count"] >= 1

    def test_recipe_detail(self, api_client, recipe_detail_url, recipe):
        """Тест получения детальной информации о рецепте."""
        response = api_client.get(recipe_detail_url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == recipe.name
        assert response.data["author"]["id"] == recipe.author.id

    def test_recipe_create_unauthenticated(
        self, api_client, recipes_url, recipe_data
    ):
        """Тест создания рецепта неаутентифицированным пользователем."""
        response = api_client.post(recipes_url, recipe_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_recipe_create_authenticated(
        self, authenticated_client, recipes_url, recipe_data
    ):
        """Тест создания рецепта аутентифицированным пользователем."""
        response = authenticated_client.post(
            recipes_url, recipe_data, format="json"
        )

        if response.status_code != status.HTTP_201_CREATED:
            print(f"Response data: {response.data}")
            print(f"Recipe data: {recipe_data}")

        assert response.status_code == status.HTTP_201_CREATED
        assert Recipe.objects.filter(name=recipe_data["name"]).exists()

    @pytest.mark.parametrize(
        "cooking_time,expected_status",
        [
            (0, status.HTTP_400_BAD_REQUEST),  # невалидное значение
            (
                MIN_COOKING_TIME,
                status.HTTP_201_CREATED,
            ),  # минимальное валидное
            (60, status.HTTP_201_CREATED),  # нормальное значение
            (
                MAX_COOKING_TIME,
                status.HTTP_201_CREATED,
            ),  # максимальное валидное
            (
                MAX_COOKING_TIME + 1,
                status.HTTP_400_BAD_REQUEST,
            ),  # превышение максимума
            (-5, status.HTTP_400_BAD_REQUEST),  # отрицательное
        ],
    )
    def test_recipe_cooking_time_validation(
        self,
        authenticated_client,
        recipes_url,
        recipe_data,
        cooking_time,
        expected_status,
    ):
        """Тест валидации времени приготовления."""
        recipe_data["cooking_time"] = cooking_time

        response = authenticated_client.post(
            recipes_url, recipe_data, format="json"
        )

        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "ingredients_data,expected_status",
        [
            ([], status.HTTP_400_BAD_REQUEST),  # пустой список
            (
                [{"id": 1, "amount": 0}],
                status.HTTP_400_BAD_REQUEST,
            ),  # нулевое количество
            (
                [{"id": 1, "amount": -1}],
                status.HTTP_400_BAD_REQUEST,
            ),  # отрицательное количество
            ([{"amount": 100}], status.HTTP_400_BAD_REQUEST),  # без ID
            (
                [{"id": 1, "amount": 100}],
                status.HTTP_201_CREATED,
            ),  # валидные данные
        ],
    )
    def test_recipe_ingredients_validation(
        self,
        authenticated_client,
        recipes_url,
        recipe_data,
        ingredient,
        ingredients_data,
        expected_status,
    ):
        """Тест валидации ингредиентов."""
        # Заменяем ID на реальный
        for ing_data in ingredients_data:
            if "id" in ing_data:
                ing_data["id"] = ingredient.id

        recipe_data["ingredients"] = ingredients_data

        response = authenticated_client.post(
            recipes_url, recipe_data, format="json"
        )

        assert response.status_code == expected_status

    def test_recipe_get_link(self, api_client, recipe):
        """Тест получения короткой ссылки на рецепт."""
        url = f"/api/v1/recipes/{recipe.pk}/get-link/"
        response = api_client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert "short-link" in data
        assert f"/s/{recipe.pk}/" in data["short-link"]

    def test_short_link_redirect(self, api_client, recipe):
        """Тест редиректа по короткой ссылке."""
        url = f"/s/{recipe.pk}/"
        response = api_client.get(url)

        # Проверяем, что происходит редирект
        assert response.status_code == 302
        assert response.url == f"/recipes/{recipe.pk}"


@pytest.mark.django_db
class TestFavoriteAPI:
    """Тесты API избранного."""

    def test_add_to_favorites(self, authenticated_client, recipe, user):
        """Тест добавления рецепта в избранное."""
        url = f"/api/v1/recipes/{recipe.pk}/favorite/"

        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Favorite.objects.filter(recipe=recipe, user=user).exists()

    def test_remove_from_favorites(self, authenticated_client, recipe, user):
        """Тест удаления рецепта из избранного."""
        # Добавляем в избранное
        Favorite.objects.create(user=user, recipe=recipe)

        url = f"/api/v1/recipes/{recipe.pk}/favorite/"
        response = authenticated_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Favorite.objects.filter(recipe=recipe, user=user).exists()


@pytest.mark.django_db
class TestShoppingCartAPI:
    """Тесты API списка покупок."""

    def test_add_to_shopping_cart(self, authenticated_client, recipe, user):
        """Тест добавления рецепта в список покупок."""
        url = f"/api/v1/recipes/{recipe.pk}/shopping_cart/"

        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_201_CREATED
        assert ShoppingCart.objects.filter(recipe=recipe, user=user).exists()

    def test_download_shopping_cart(self, authenticated_client, recipe, user):
        """Тест скачивания списка покупок."""
        # Добавляем рецепт в корзину
        ShoppingCart.objects.create(user=user, recipe=recipe)

        url = "/api/v1/recipes/download_shopping_cart/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/plain; charset=utf-8"
        assert "attachment" in response["Content-Disposition"]

        # Проверяем, что файл не пустой и содержит ожидаемые данные
        content = response.content.decode("utf-8")
        assert "Список покупок" in content
        assert len(content) > 20  # Файл не должен быть пустым

    def test_download_shopping_cart_with_ingredients(
        self, authenticated_client, user, ingredient, tag
    ):
        """Тест скачивания списка покупок с ингредиентами."""
        # Создаем рецепт с ингредиентами
        from apps.recipes.models import IngredientInRecipe, Recipe

        recipe = Recipe.objects.create(
            author=user,
            name="Тестовый рецепт",
            text="Описание рецепта",
            cooking_time=30,
        )
        recipe.tags.add(tag)

        # Добавляем ингредиент в рецепт
        IngredientInRecipe.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=200,
        )

        # Добавляем рецепт в корзину
        ShoppingCart.objects.create(user=user, recipe=recipe)

        url = "/api/v1/recipes/download_shopping_cart/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        content = response.content.decode("utf-8")

        # Проверяем содержимое файла
        assert "Список покупок" in content
        assert ingredient.name in content
        assert ingredient.measurement_unit in content
        assert "200" in content  # количество


@pytest.mark.django_db
class TestAPIVersioning:
    """Тесты версионирования API."""

    def test_v1_endpoint_works(self, api_client):
        """Тест работы v1 endpoint."""
        response = api_client.get("/api/v1/health/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["version"] == "v1"

    def test_default_api_redirects_to_v1(self, api_client):
        """Тест редиректа с основного API на v1."""
        response = api_client.get("/api/health/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["version"] == "v1"

    def test_users_endpoint_v1_explicit(self, api_client):
        """Тест users endpoint с явной версией v1."""
        url = "/api/v1/users/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_users_endpoint_default_version(self, api_client):
        """Тест users endpoint с версией по умолчанию."""
        url = "/api/users/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_tags_endpoint_v1_explicit(self, api_client):
        """Тест tags endpoint с явной версией v1."""
        url = "/api/v1/tags/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_tags_endpoint_default_version(self, api_client):
        """Тест tags endpoint с версией по умолчанию."""
        url = "/api/tags/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_ingredients_endpoint_v1_explicit(self, api_client):
        """Тест ingredients endpoint с явной версией v1."""
        url = "/api/v1/ingredients/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_ingredients_endpoint_default_version(self, api_client):
        """Тест ingredients endpoint с версией по умолчанию."""
        url = "/api/ingredients/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_recipes_endpoint_v1_explicit(self, api_client):
        """Тест recipes endpoint с явной версией v1."""
        url = "/api/v1/recipes/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_recipes_endpoint_default_version(self, api_client):
        """Тест recipes endpoint с версией по умолчанию."""
        url = "/api/recipes/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "endpoint,expected_version",
        [
            ("/api/v1/health/", "v1"),
            ("/api/health/", "v1"),  # По умолчанию v1
        ],
    )
    def test_version_detection(self, api_client, endpoint, expected_version):
        """Параметризованный тест определения версии API."""
        response = api_client.get(endpoint)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["version"] == expected_version
