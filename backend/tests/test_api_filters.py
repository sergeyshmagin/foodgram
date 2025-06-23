"""Тесты фильтров API для Foodgram."""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from apps.api.filters import IngredientFilter, RecipeFilter
from apps.recipes.models import Favorite, Ingredient, Recipe, ShoppingCart

User = get_user_model()


@pytest.mark.django_db
class TestRecipeFilter:
    """Тесты фильтра рецептов."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.factory = APIRequestFactory()

    def test_filter_by_author(self, user, another_user, recipe):
        """Тест фильтрации по автору."""
        # Создаем рецепт от другого автора
        Recipe.objects.create(
            name="Рецепт другого автора",
            text="Описание",
            cooking_time=30,
            author=another_user,
        )

        request = self.factory.get(f"/?author={user.id}")
        request.user = user

        filter_instance = RecipeFilter(
            data={"author": user.id}, request=request
        )

        # Нужно сначала валидировать форму
        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert filtered_queryset.count() == 1
        assert filtered_queryset.first().author == user

    def test_filter_by_tags(self, user, recipe, tag):
        """Тест фильтрации по тегам."""
        # Создаем рецепт без тегов
        Recipe.objects.create(
            name="Рецепт без тегов",
            text="Описание",
            cooking_time=30,
            author=user,
        )

        request = self.factory.get(f"/?tags={tag.slug}")
        request.user = user

        filter_instance = RecipeFilter(
            data={"tags": [tag.slug]}, request=request
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert filtered_queryset.count() == 1
        assert tag in filtered_queryset.first().tags.all()

    def test_filter_is_favorited_true(self, user, recipe, another_user):
        """Тест фильтрации избранных рецептов."""
        # Создаем еще один рецепт
        Recipe.objects.create(
            name="Другой рецепт",
            text="Описание",
            cooking_time=30,
            author=another_user,
        )

        # Добавляем один рецепт в избранное
        Favorite.objects.create(user=user, recipe=recipe)

        request = self.factory.get("/?is_favorited=1")
        request.user = user

        filter_instance = RecipeFilter(
            data={"is_favorited": True}, request=request
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert filtered_queryset.count() == 1
        assert filtered_queryset.first() == recipe

    def test_filter_is_favorited_false(self, user, recipe):
        """Тест фильтрации не избранных рецептов."""
        request = self.factory.get("/?is_favorited=0")
        request.user = user

        filter_instance = RecipeFilter(
            data={"is_favorited": False}, request=request
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        # При is_favorited=False возвращается весь queryset
        assert recipe in filtered_queryset

    def test_filter_is_in_shopping_cart_true(self, user, recipe, another_user):
        """Тест фильтрации рецептов в корзине покупок."""
        # Создаем еще один рецепт
        Recipe.objects.create(
            name="Другой рецепт",
            text="Описание",
            cooking_time=30,
            author=another_user,
        )

        # Добавляем один рецепт в корзину
        ShoppingCart.objects.create(user=user, recipe=recipe)

        request = self.factory.get("/?is_in_shopping_cart=1")
        request.user = user

        filter_instance = RecipeFilter(
            data={"is_in_shopping_cart": True}, request=request
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert filtered_queryset.count() == 1
        assert filtered_queryset.first() == recipe

    def test_filter_is_in_shopping_cart_false(self, user, recipe):
        """Тест фильтрации рецептов не в корзине покупок."""
        request = self.factory.get("/?is_in_shopping_cart=0")
        request.user = user

        filter_instance = RecipeFilter(
            data={"is_in_shopping_cart": False}, request=request
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        # При is_in_shopping_cart=False возвращается весь queryset
        assert recipe in filtered_queryset

    def test_filter_unauthenticated_user(self, recipe):
        """Тест фильтрации для неаутентифицированного пользователя."""
        from django.contrib.auth.models import AnonymousUser

        request = self.factory.get("/?is_favorited=1")
        request.user = AnonymousUser()

        filter_instance = RecipeFilter(
            data={"is_favorited": True}, request=request
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        # Для неаутентифицированного пользователя возвращается весь queryset
        assert filtered_queryset.count() == Recipe.objects.count()


@pytest.mark.django_db
class TestIngredientFilter:
    """Тесты фильтра ингредиентов."""

    def test_filter_by_name(self, ingredient):
        """Тест фильтрации ингредиентов по имени."""
        filter_instance = IngredientFilter(
            data={"name": "Мук"},  # Начинается с "Мук" для "Мука"
            queryset=Ingredient.objects.all(),
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert ingredient in filtered_queryset

    def test_filter_by_name_case_insensitive(self, ingredient):
        """Тест фильтрации ингредиентов по имени (регистронезависимо)."""
        filter_instance = IngredientFilter(
            data={"name": "М"},  # Первая буква в верхнем регистре
            queryset=Ingredient.objects.all(),
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert ingredient in filtered_queryset

    def test_filter_by_name_no_match(self, ingredient):
        """Тест фильтрации ингредиентов без совпадений."""
        filter_instance = IngredientFilter(
            data={"name": "xyz"},  # Нет совпадений
            queryset=Ingredient.objects.all(),
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        assert ingredient not in filtered_queryset
        assert filtered_queryset.count() == 0

    def test_filter_empty_name(self, ingredient):
        """Тест фильтрации без указания имени."""
        filter_instance = IngredientFilter(
            data={}, queryset=Ingredient.objects.all()  # Пустые данные
        )

        assert filter_instance.is_valid()
        filtered_queryset = filter_instance.qs

        # Без фильтра возвращается весь queryset
        assert ingredient in filtered_queryset
        assert filtered_queryset.count() == Ingredient.objects.count()
