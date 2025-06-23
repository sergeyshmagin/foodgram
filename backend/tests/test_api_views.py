"""Тесты views API для Foodgram - Edge Cases."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestUserViewSetEdgeCases:
    """Тесты UserViewSet - edge cases."""

    def test_me_endpoint_unauthenticated(self, api_client):
        """Тест /me для неаутентифицированного пользователя."""
        response = api_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_set_password_invalid_current_password(self, authenticated_client):
        """Тест смены пароля с неверным текущим паролем."""
        data = {
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        }
        response = authenticated_client.post(
            "/api/v1/users/set_password/", data
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_set_avatar_invalid_format(self, authenticated_client):
        """Тест установки аватара в неверном формате."""
        data = {"avatar": "invalid_base64_string"}
        response = authenticated_client.put(
            "/api/v1/users/me/avatar/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSubscriptionViewSetEdgeCases:
    """Тесты подписок - edge cases."""

    def test_subscribe_to_self(self, authenticated_client, user):
        """Тест подписки на самого себя."""
        response = authenticated_client.post(
            f"/api/v1/users/{user.id}/subscribe/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_subscribe_twice(self, authenticated_client, another_user):
        """Тест повторной подписки на того же пользователя."""
        # Первая подписка
        response1 = authenticated_client.post(
            f"/api/v1/users/{another_user.id}/subscribe/"
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Повторная подписка
        response2 = authenticated_client.post(
            f"/api/v1/users/{another_user.id}/subscribe/"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_unsubscribe_when_not_subscribed(
        self, authenticated_client, another_user
    ):
        """Тест отписки когда не подписан."""
        response = authenticated_client.delete(
            f"/api/v1/users/{another_user.id}/subscribe/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestRecipeViewSetEdgeCases:
    """Тесты RecipeViewSet - edge cases."""

    def test_create_recipe_without_image(
        self, authenticated_client, tag, ingredient
    ):
        """Тест создания рецепта без изображения."""
        data = {
            "name": "Рецепт без изображения",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 100}],
        }
        response = authenticated_client.post(
            "/api/v1/recipes/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_recipe_by_non_author(
        self, api_client, another_user, recipe
    ):
        """Тест обновления рецепта не автором."""
        api_client.force_authenticate(user=another_user)
        data = {"name": "Измененное название"}
        response = api_client.patch(
            f"/api/v1/recipes/{recipe.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestFavoriteViewSetEdgeCases:
    """Тесты избранного - edge cases."""

    def test_add_to_favorites_twice(self, authenticated_client, recipe):
        """Тест добавления в избранное дважды."""
        # Первое добавление
        response1 = authenticated_client.post(
            f"/api/v1/recipes/{recipe.id}/favorite/"
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Повторное добавление
        response2 = authenticated_client.post(
            f"/api/v1/recipes/{recipe.id}/favorite/"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_remove_from_favorites_when_not_favorited(
        self, authenticated_client, recipe
    ):
        """Тест удаления из избранного когда рецепт не в избранном."""
        response = authenticated_client.delete(
            f"/api/v1/recipes/{recipe.id}/favorite/"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestShoppingCartViewSetEdgeCases:
    """Тесты корзины покупок - edge cases."""

    def test_add_to_shopping_cart_twice(self, authenticated_client, recipe):
        """Тест добавления в корзину дважды."""
        # Первое добавление
        response1 = authenticated_client.post(
            f"/api/v1/recipes/{recipe.id}/shopping_cart/"
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Повторное добавление
        response2 = authenticated_client.post(
            f"/api/v1/recipes/{recipe.id}/shopping_cart/"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST

    def test_download_empty_shopping_cart(self, authenticated_client):
        """Тест скачивания пустой корзины покупок."""
        response = authenticated_client.get(
            "/api/v1/recipes/download_shopping_cart/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response["Content-Type"] == "text/plain; charset=utf-8"


@pytest.mark.django_db
class TestAuthenticationEdgeCases:
    """Тесты аутентификации - edge cases."""

    def test_access_protected_endpoint_without_token(self, api_client):
        """Тест доступа к защищенному endpoint без токена."""
        response = api_client.post("/api/v1/recipes/", {})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_access_with_invalid_token(self, api_client):
        """Тест доступа с невалидным токеном."""
        api_client.credentials(HTTP_AUTHORIZATION="Token invalid_token_here")
        response = api_client.get("/api/v1/users/me/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
