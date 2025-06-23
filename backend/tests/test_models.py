"""Тесты моделей для Foodgram."""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError

from apps.recipes.models import (Favorite, Ingredient, IngredientInRecipe,
                                 Recipe, ShoppingCart, Subscription, Tag)
from foodgram.constants import MAX_RECIPE_NAME_LENGTH

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Тесты модели User."""

    def test_user_creation(self):
        """Тест создания пользователя."""
        user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.check_password("testpass123")

    def test_superuser_creation(self):
        """Тест создания суперпользователя."""
        admin = User.objects.create_superuser(
            email="admin@example.com",
            username="admin",
            password="adminpass123",
        )

        assert admin.is_staff
        assert admin.is_superuser

    def test_user_str_representation(self, user):
        """Тест строкового представления пользователя."""
        assert str(user) == user.username


@pytest.mark.django_db
class TestTagModel:
    """Тесты модели Tag."""

    def test_tag_creation(self):
        """Тест создания тега."""
        tag = Tag.objects.create(
            name="Завтрак", color="#FF0000", slug="breakfast"
        )

        assert tag.name == "Завтрак"
        assert tag.color == "#FF0000"
        assert tag.slug == "breakfast"

    def test_tag_str_representation(self, tag):
        """Тест строкового представления тега."""
        assert str(tag) == tag.name

    def test_tag_slug_unique(self, tag):
        """Тест уникальности slug тега."""
        with pytest.raises(IntegrityError):
            Tag.objects.create(
                name="Другой завтрак",
                color="#00FF00",
                slug=tag.slug,  # Дублирующийся slug
            )


@pytest.mark.django_db
class TestIngredientModel:
    """Тесты модели Ingredient."""

    def test_ingredient_creation(self):
        """Тест создания ингредиента."""
        ingredient = Ingredient.objects.create(
            name="Молоко", measurement_unit="мл"
        )

        assert ingredient.name == "Молоко"
        assert ingredient.measurement_unit == "мл"

    def test_ingredient_str_representation(self, ingredient):
        """Тест строкового представления ингредиента."""
        expected = f"{ingredient.name} ({ingredient.measurement_unit})"
        assert str(ingredient) == expected


@pytest.mark.django_db
class TestRecipeModel:
    """Тесты модели Recipe."""

    def test_recipe_creation(self, user):
        """Тест создания рецепта."""
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

        assert recipe.author == user
        assert recipe.name == "Тестовый рецепт"
        assert recipe.text == "Описание тестового рецепта"
        assert recipe.cooking_time == 30

    def test_recipe_str_representation(self, recipe):
        """Тест строкового представления рецепта."""
        assert str(recipe) == recipe.name

    @pytest.mark.parametrize(
        "cooking_time,should_raise",
        [
            (0, True),  # меньше минимума
            (1, False),  # минимальное валидное
            (60, False),  # нормальное значение
            (-1, True),  # отрицательное
        ],
    )
    def test_recipe_cooking_time_validation(
        self, user, cooking_time, should_raise
    ):
        """Тест валидации времени приготовления."""
        # Создаем тестовое изображение
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake_image_content",
            content_type="image/jpeg",
        )

        recipe = Recipe(
            author=user,
            name="Тестовый рецепт",
            image=image,
            text="Описание тестового рецепта",
            cooking_time=cooking_time,
        )

        if should_raise:
            with pytest.raises(ValidationError):
                recipe.full_clean()
        else:
            recipe.full_clean()  # Не должно вызвать исключение

    def test_recipe_name_max_length(self, user):
        """Тест максимальной длины названия рецепта."""
        long_name = "А" * (MAX_RECIPE_NAME_LENGTH + 1)

        # Создаем тестовое изображение
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"fake_image_content",
            content_type="image/jpeg",
        )

        recipe = Recipe(
            author=user,
            name=long_name,
            image=image,
            text="Описание",
            cooking_time=30,
        )

        with pytest.raises(ValidationError):
            recipe.full_clean()


@pytest.mark.django_db
class TestIngredientInRecipeModel:
    """Тесты модели IngredientInRecipe."""

    def test_ingredient_in_recipe_creation(self, user):
        """Тест создания связи ингредиента с рецептом."""
        # Создаем новый рецепт и ингредиент для этого теста
        recipe = Recipe.objects.create(
            author=user,
            name="Новый рецепт",
            image=SimpleUploadedFile(
                name="test.jpg",
                content=b"fake_image_content",
                content_type="image/jpeg",
            ),
            text="Описание",
            cooking_time=30,
        )
        ingredient = Ingredient.objects.create(
            name="Новый ингредиент", measurement_unit="кг"
        )

        ingredient_in_recipe = IngredientInRecipe.objects.create(
            recipe=recipe, ingredient=ingredient, amount=100
        )

        assert ingredient_in_recipe.recipe == recipe
        assert ingredient_in_recipe.ingredient == ingredient
        assert ingredient_in_recipe.amount == 100

    def test_ingredient_in_recipe_str_representation(self, user):
        """Тест строкового представления ингредиента в рецепте."""
        # Создаем новый рецепт и ингредиент для этого теста
        recipe = Recipe.objects.create(
            author=user,
            name="Рецепт для теста",
            image=SimpleUploadedFile(
                name="test2.jpg",
                content=b"fake_image_content",
                content_type="image/jpeg",
            ),
            text="Описание",
            cooking_time=30,
        )
        ingredient = Ingredient.objects.create(
            name="Ингредиент для теста", measurement_unit="л"
        )

        ingredient_in_recipe = IngredientInRecipe.objects.create(
            recipe=recipe, ingredient=ingredient, amount=100
        )

        expected = f"{ingredient.name} в {recipe.name}"
        assert str(ingredient_in_recipe) == expected

    def test_ingredient_in_recipe_unique_together(self, user):
        """Тест уникальности связи рецепт-ингредиент."""
        # Создаем новый рецепт и ингредиент для этого теста
        recipe = Recipe.objects.create(
            author=user,
            name="Рецепт для уникальности",
            image=SimpleUploadedFile(
                name="test3.jpg",
                content=b"fake_image_content",
                content_type="image/jpeg",
            ),
            text="Описание",
            cooking_time=30,
        )
        ingredient = Ingredient.objects.create(
            name="Ингредиент для уникальности", measurement_unit="шт"
        )

        IngredientInRecipe.objects.create(
            recipe=recipe, ingredient=ingredient, amount=100
        )

        with pytest.raises(IntegrityError):
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,  # Дублирующаяся связь
                amount=200,
            )


@pytest.mark.django_db
class TestFavoriteModel:
    """Тесты модели Favorite."""

    def test_favorite_creation(self, user, recipe):
        """Тест создания избранного рецепта."""
        favorite = Favorite.objects.create(user=user, recipe=recipe)

        assert favorite.user == user
        assert favorite.recipe == recipe

    def test_favorite_str_representation(self, user, recipe):
        """Тест строкового представления избранного."""
        favorite = Favorite.objects.create(user=user, recipe=recipe)

        expected = f"{user.username} добавил {recipe.name} в избранное"
        assert str(favorite) == expected

    def test_favorite_unique_together(self, user, recipe):
        """Тест уникальности связи пользователь-рецепт в избранном."""
        Favorite.objects.create(user=user, recipe=recipe)

        with pytest.raises(IntegrityError):
            Favorite.objects.create(
                user=user, recipe=recipe  # Дублирующаяся связь
            )


@pytest.mark.django_db
class TestShoppingCartModel:
    """Тесты модели ShoppingCart."""

    def test_shopping_cart_creation(self, user, recipe):
        """Тест создания элемента корзины покупок."""
        cart_item = ShoppingCart.objects.create(user=user, recipe=recipe)

        assert cart_item.user == user
        assert cart_item.recipe == recipe

    def test_shopping_cart_str_representation(self, user, recipe):
        """Тест строкового представления корзины покупок."""
        cart_item = ShoppingCart.objects.create(user=user, recipe=recipe)

        expected = f"{user.username} добавил {recipe.name} в корзину"
        assert str(cart_item) == expected


@pytest.mark.django_db
class TestSubscriptionModel:
    """Тесты модели Subscription."""

    def test_subscription_creation(self, user, another_user):
        """Тест создания подписки."""
        subscription = Subscription.objects.create(
            user=user, author=another_user
        )

        assert subscription.user == user
        assert subscription.author == another_user

    def test_subscription_str_representation(self, user, another_user):
        """Тест строкового представления подписки."""
        subscription = Subscription.objects.create(
            user=user, author=another_user
        )

        expected = f"{user.username} подписан на {another_user.username}"
        assert str(subscription) == expected

    def test_subscription_unique_together(self, user, another_user):
        """Тест уникальности связи пользователь-автор."""
        Subscription.objects.create(user=user, author=another_user)

        with pytest.raises(IntegrityError):
            Subscription.objects.create(
                user=user, author=another_user  # Дублирующаяся связь
            )
