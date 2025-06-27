"""Тесты для проверки reverse operations всех URL."""
import pytest
from apps.api.reverse_utils import URL_NAMES, FoodgramURLs, get_recipe_url
from django.urls import reverse


@pytest.mark.django_db
class TestReverseURLs:
    """Тесты для проверки всех reverse операций."""

    def test_api_base_urls(self):
        """Тест базовых API URL."""
        # Health check
        assert FoodgramURLs.api_health_check() == "/api/v1/health/"
        assert reverse(URL_NAMES["API_HEALTH"]) == "/api/v1/health/"

        # Документация
        assert FoodgramURLs.api_docs() == "/api/v1/docs/"
        assert reverse(URL_NAMES["API_DOCS"]) == "/api/v1/docs/"

        assert FoodgramURLs.api_redoc() == "/api/v1/redoc/"
        assert reverse(URL_NAMES["API_REDOC"]) == "/api/v1/redoc/"

        assert FoodgramURLs.api_schema() == "/api/v1/schema/"
        assert reverse(URL_NAMES["API_SCHEMA"]) == "/api/v1/schema/"

    def test_users_urls(self):
        """Тест URL для пользователей."""
        # Список пользователей
        assert FoodgramURLs.users_list() == "/api/v1/users/"
        assert reverse(URL_NAMES["USERS_LIST"]) == "/api/v1/users/"

        # Детальная информация о пользователе
        assert FoodgramURLs.users_detail(1) == "/api/v1/users/1/"
        assert (
            reverse(URL_NAMES["USERS_DETAIL"], kwargs={"id": 1})
            == "/api/v1/users/1/"
        )

        # Подписки
        assert (
            FoodgramURLs.users_subscriptions()
            == "/api/v1/users/subscriptions/"
        )
        assert (
            reverse(URL_NAMES["USERS_SUBSCRIPTIONS"])
            == "/api/v1/users/subscriptions/"
        )

        # Подписка на пользователя
        assert FoodgramURLs.users_subscribe(1) == "/api/v1/users/1/subscribe/"
        assert (
            reverse(URL_NAMES["USERS_SUBSCRIBE"], kwargs={"id": 1})
            == "/api/v1/users/1/subscribe/"
        )

        # Аватар
        assert FoodgramURLs.users_avatar() == "/api/v1/users/me/avatar/"
        assert reverse(URL_NAMES["USERS_AVATAR"]) == "/api/v1/users/me/avatar/"

        # Изменение пароля
        assert (
            FoodgramURLs.users_set_password() == "/api/v1/users/set_password/"
        )
        assert (
            reverse(URL_NAMES["USERS_SET_PASSWORD"])
            == "/api/v1/users/set_password/"
        )

    def test_recipes_urls(self):
        """Тест URL для рецептов."""
        # Список рецептов
        assert FoodgramURLs.recipes_list() == "/api/v1/recipes/"
        assert reverse(URL_NAMES["RECIPES_LIST"]) == "/api/v1/recipes/"

        # Детальная информация о рецепте
        assert FoodgramURLs.recipes_detail(1) == "/api/v1/recipes/1/"
        assert (
            reverse(URL_NAMES["RECIPES_DETAIL"], kwargs={"pk": 1})
            == "/api/v1/recipes/1/"
        )

        # Избранное
        assert (
            FoodgramURLs.recipes_favorite(1) == "/api/v1/recipes/1/favorite/"
        )
        assert (
            reverse(URL_NAMES["RECIPES_FAVORITE"], kwargs={"pk": 1})
            == "/api/v1/recipes/1/favorite/"
        )

        # Корзина покупок
        assert (
            FoodgramURLs.recipes_shopping_cart(1)
            == "/api/v1/recipes/1/shopping_cart/"
        )
        assert (
            reverse(URL_NAMES["RECIPES_SHOPPING_CART"], kwargs={"pk": 1})
            == "/api/v1/recipes/1/shopping_cart/"
        )

        # Скачивание списка покупок
        assert (
            FoodgramURLs.recipes_download_shopping_cart()
            == "/api/v1/recipes/download_shopping_cart/"
        )
        assert (
            reverse(URL_NAMES["RECIPES_DOWNLOAD_CART"])
            == "/api/v1/recipes/download_shopping_cart/"
        )

        # Получение короткой ссылки
        assert (
            FoodgramURLs.recipes_get_link(1) == "/api/v1/recipes/1/get-link/"
        )
        assert (
            reverse(URL_NAMES["RECIPES_GET_LINK"], kwargs={"pk": 1})
            == "/api/v1/recipes/1/get-link/"
        )

    def test_tags_urls(self):
        """Тест URL для тегов."""
        # Список тегов
        assert FoodgramURLs.tags_list() == "/api/v1/tags/"
        assert reverse(URL_NAMES["TAGS_LIST"]) == "/api/v1/tags/"

        # Детальная информация о теге
        assert FoodgramURLs.tags_detail(1) == "/api/v1/tags/1/"
        assert (
            reverse(URL_NAMES["TAGS_DETAIL"], kwargs={"pk": 1})
            == "/api/v1/tags/1/"
        )

    def test_ingredients_urls(self):
        """Тест URL для ингредиентов."""
        # Список ингредиентов
        assert FoodgramURLs.ingredients_list() == "/api/v1/ingredients/"
        assert reverse(URL_NAMES["INGREDIENTS_LIST"]) == "/api/v1/ingredients/"

        # Детальная информация об ингредиенте
        assert FoodgramURLs.ingredients_detail(1) == "/api/v1/ingredients/1/"
        assert (
            reverse(URL_NAMES["INGREDIENTS_DETAIL"], kwargs={"pk": 1})
            == "/api/v1/ingredients/1/"
        )

    def test_short_link_urls(self):
        """Тест URL для коротких ссылок."""
        assert FoodgramURLs.short_link(1) == "/s/1/"
        assert (
            reverse(URL_NAMES["SHORT_LINK"], kwargs={"recipe_id": 1})
            == "/s/1/"
        )

    def test_helper_functions(self, recipe):
        """Тест вспомогательных функций."""
        # Получение URL рецепта
        assert get_recipe_url(recipe.id) == f"/api/v1/recipes/{recipe.id}/"

    def test_all_url_names_exist(self):
        """Проверяем, что все имена URL существуют."""
        for name, url_name in URL_NAMES.items():
            try:
                if (
                    "DETAIL" in name
                    or "SUBSCRIBE" in name
                    or "FAVORITE" in name
                    or "SHOPPING_CART" in name
                    or "GET_LINK" in name
                    or "SHORT_LINK" in name
                ):
                    # URL с параметрами
                    if "SHORT_LINK" in name:
                        reverse(url_name, kwargs={"recipe_id": 1})
                    elif "USERS_" in name:
                        # Users endpoints используют 'id'
                        reverse(url_name, kwargs={"id": 1})
                    else:
                        # Recipes, Tags, Ingredients используют 'pk'
                        reverse(url_name, kwargs={"pk": 1})
                else:
                    # URL без параметров
                    reverse(url_name)
            except Exception as e:
                pytest.fail(
                    f"URL name '{url_name}' для '{name}' не существует: {e}"
                )

    def test_foodgram_urls_class_methods(self):
        """Тест всех методов класса FoodgramURLs."""
        # Проверяем, что все методы возвращают строки, начинающиеся с "/"
        assert FoodgramURLs.api_health_check().startswith("/")
        assert FoodgramURLs.api_docs().startswith("/")
        assert FoodgramURLs.api_redoc().startswith("/")
        assert FoodgramURLs.api_schema().startswith("/")

        assert FoodgramURLs.users_list().startswith("/")
        assert FoodgramURLs.users_detail(1).startswith("/")
        assert FoodgramURLs.users_subscriptions().startswith("/")
        assert FoodgramURLs.users_subscribe(1).startswith("/")
        assert FoodgramURLs.users_avatar().startswith("/")
        assert FoodgramURLs.users_set_password().startswith("/")

        assert FoodgramURLs.recipes_list().startswith("/")
        assert FoodgramURLs.recipes_detail(1).startswith("/")
        assert FoodgramURLs.recipes_favorite(1).startswith("/")
        assert FoodgramURLs.recipes_shopping_cart(1).startswith("/")
        assert FoodgramURLs.recipes_download_shopping_cart().startswith("/")
        assert FoodgramURLs.recipes_get_link(1).startswith("/")

        assert FoodgramURLs.tags_list().startswith("/")
        assert FoodgramURLs.tags_detail(1).startswith("/")

        assert FoodgramURLs.ingredients_list().startswith("/")
        assert FoodgramURLs.ingredients_detail(1).startswith("/")

        assert FoodgramURLs.short_link(1).startswith("/")
