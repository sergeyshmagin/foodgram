"""Утилиты для reverse operations в Foodgram API."""
from django.urls import reverse


class FoodgramURLs:
    """Класс с методами для получения URL через reverse."""

    # Базовые API endpoints
    @staticmethod
    def api_health_check():
        """URL для health check."""
        return reverse("api:v1:health-check")

    @staticmethod
    def api_docs():
        """URL для Swagger документации."""
        return reverse("api:v1:docs")

    @staticmethod
    def api_redoc():
        """URL для ReDoc документации."""
        return reverse("api:v1:redoc")

    @staticmethod
    def api_schema():
        """URL для OpenAPI схемы."""
        return reverse("api:v1:schema")

    # Users endpoints
    @staticmethod
    def users_list():
        """URL для списка пользователей."""
        return reverse("api:v1:users-list")

    @staticmethod
    def users_detail(user_id):
        """URL для детальной информации о пользователе."""
        return reverse("api:v1:users-detail", kwargs={"id": user_id})

    @staticmethod
    def users_subscriptions():
        """URL для списка подписок пользователя."""
        return reverse("api:v1:users-subscriptions")

    @staticmethod
    def users_subscribe(user_id):
        """URL для подписки на пользователя."""
        return reverse("api:v1:users-subscribe", kwargs={"id": user_id})

    @staticmethod
    def users_avatar():
        """URL для управления аватаром пользователя."""
        return reverse("api:v1:users-avatar")

    @staticmethod
    def users_set_password():
        """URL для изменения пароля."""
        return reverse("api:v1:users-set-password")

    # Recipes endpoints
    @staticmethod
    def recipes_list():
        """URL для списка рецептов."""
        return reverse("api:v1:recipes-list")

    @staticmethod
    def recipes_detail(recipe_id):
        """URL для детальной информации о рецепте."""
        return reverse("api:v1:recipes-detail", kwargs={"pk": recipe_id})

    @staticmethod
    def recipes_favorite(recipe_id):
        """URL для добавления рецепта в избранное."""
        return reverse("api:v1:recipes-favorite", kwargs={"pk": recipe_id})

    @staticmethod
    def recipes_shopping_cart(recipe_id):
        """URL для добавления рецепта в корзину."""
        return reverse(
            "api:v1:recipes-shopping-cart", kwargs={"pk": recipe_id}
        )

    @staticmethod
    def recipes_download_shopping_cart():
        """URL для скачивания списка покупок."""
        return reverse("api:v1:recipes-download-shopping-cart")

    @staticmethod
    def recipes_get_link(recipe_id):
        """URL для получения короткой ссылки на рецепт."""
        return reverse("api:v1:recipes-get-link", kwargs={"pk": recipe_id})

    # Tags endpoints
    @staticmethod
    def tags_list():
        """URL для списка тегов."""
        return reverse("api:v1:tags-list")

    @staticmethod
    def tags_detail(tag_id):
        """URL для детальной информации о теге."""
        return reverse("api:v1:tags-detail", kwargs={"pk": tag_id})

    # Ingredients endpoints
    @staticmethod
    def ingredients_list():
        """URL для списка ингредиентов."""
        return reverse("api:v1:ingredients-list")

    @staticmethod
    def ingredients_detail(ingredient_id):
        """URL для детальной информации об ингредиенте."""
        return reverse(
            "api:v1:ingredients-detail", kwargs={"pk": ingredient_id}
        )

    # Short links
    @staticmethod
    def short_link(recipe_id):
        """URL для короткой ссылки на рецепт."""
        return reverse("short-link", kwargs={"recipe_id": recipe_id})

    # Admin
    @staticmethod
    def admin():
        """URL для админ-панели."""
        return reverse("admin:index")


# Функции-хелперы для быстрого доступа
def get_recipe_url(recipe_id):
    """Получить URL рецепта."""
    return FoodgramURLs.recipes_detail(recipe_id)


def get_user_url(user_id):
    """Получить URL пользователя."""
    return FoodgramURLs.users_detail(user_id)


def get_short_link_url(recipe_id):
    """Получить короткую ссылку на рецепт."""
    return FoodgramURLs.short_link(recipe_id)


def get_api_docs_url():
    """Получить URL документации API."""
    return FoodgramURLs.api_docs()


# Константы с именами URL для использования в коде
URL_NAMES = {
    # API
    "API_HEALTH": "api:v1:health-check",
    "API_DOCS": "api:v1:docs",
    "API_REDOC": "api:v1:redoc",
    "API_SCHEMA": "api:v1:schema",
    # Users
    "USERS_LIST": "api:v1:users-list",
    "USERS_DETAIL": "api:v1:users-detail",
    "USERS_SUBSCRIPTIONS": "api:v1:users-subscriptions",
    "USERS_SUBSCRIBE": "api:v1:users-subscribe",
    "USERS_AVATAR": "api:v1:users-avatar",
    "USERS_SET_PASSWORD": "api:v1:users-set-password",
    # Recipes
    "RECIPES_LIST": "api:v1:recipes-list",
    "RECIPES_DETAIL": "api:v1:recipes-detail",
    "RECIPES_FAVORITE": "api:v1:recipes-favorite",
    "RECIPES_SHOPPING_CART": "api:v1:recipes-shopping-cart",
    "RECIPES_DOWNLOAD_CART": "api:v1:recipes-download-shopping-cart",
    "RECIPES_GET_LINK": "api:v1:recipes-get-link",
    # Tags
    "TAGS_LIST": "api:v1:tags-list",
    "TAGS_DETAIL": "api:v1:tags-detail",
    # Ingredients
    "INGREDIENTS_LIST": "api:v1:ingredients-list",
    "INGREDIENTS_DETAIL": "api:v1:ingredients-detail",
    # Short links
    "SHORT_LINK": "short-link",
}
