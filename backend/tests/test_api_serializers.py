"""Тесты сериализаторов API для Foodgram."""
import pytest
from apps.api.serializers import (
    IngredientInRecipeSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer,
    TagSerializer,
    UserSerializer,
)
from apps.recipes.models import Recipe
from django.contrib.auth import get_user_model

User = get_user_model()

# Короткое base64 изображение для тестов
short_base64 = (
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
    "AAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


@pytest.mark.django_db
class TestUserSerializer:
    """Тесты сериализатора пользователей."""

    def test_user_serialization(self, user):
        """Тест сериализации пользователя."""
        serializer = UserSerializer(user)
        data = serializer.data

        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["username"] == user.username
        assert data["first_name"] == user.first_name
        assert data["last_name"] == user.last_name
        assert "is_subscribed" in data

    def test_is_subscribed_anonymous(self, user):
        """Тест поля is_subscribed для анонимного пользователя."""
        serializer = UserSerializer(user)
        data = serializer.data
        assert data["is_subscribed"] is False

    def test_is_subscribed_authenticated(
        self, user, another_user, subscription
    ):
        """Тест поля is_subscribed для авторизованного пользователя."""
        context = {"request": type("Request", (), {"user": user})()}
        serializer = UserSerializer(another_user, context=context)
        data = serializer.data
        assert data["is_subscribed"] is True


@pytest.mark.django_db
class TestTagSerializer:
    """Тесты сериализатора тегов."""

    def test_tag_serialization(self, tag):
        """Тест сериализации тега."""
        serializer = TagSerializer(tag)
        data = serializer.data

        assert data["id"] == tag.id
        assert data["name"] == tag.name
        assert data["slug"] == tag.slug


@pytest.mark.django_db
class TestIngredientSerializer:
    """Тесты сериализатора ингредиентов."""

    def test_ingredient_serialization(self, ingredient):
        """Тест сериализации ингредиента."""
        serializer = IngredientSerializer(ingredient)
        data = serializer.data

        assert data["id"] == ingredient.id
        assert data["name"] == ingredient.name
        assert data["measurement_unit"] == ingredient.measurement_unit


@pytest.mark.django_db
class TestIngredientInRecipeSerializer:
    """Тесты сериализатора ингредиентов в рецепте."""

    def test_serialization(self, ingredient_in_recipe):
        """Тест сериализации ингредиента в рецепте."""
        serializer = IngredientInRecipeSerializer(ingredient_in_recipe)
        data = serializer.data

        assert data["id"] == ingredient_in_recipe.ingredient.id
        assert data["name"] == ingredient_in_recipe.ingredient.name
        assert (
            data["measurement_unit"]
            == ingredient_in_recipe.ingredient.measurement_unit
        )
        assert data["amount"] == ingredient_in_recipe.amount


@pytest.mark.django_db
class TestRecipeCreateUpdateSerializer:
    """Тесты сериализатора создания/обновления рецептов."""

    def test_recipe_creation_invalid_cooking_time(self, tag, ingredient):
        """Тест создания рецепта с невалидным временем приготовления."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 0,  # Невалидное значение
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 100}],
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "cooking_time" in serializer.errors

    def test_recipe_creation_empty_ingredients(self, tag):
        """Тест создания рецепта без ингредиентов."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [],  # Пустой список
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors

    def test_recipe_creation_empty_tags(self, ingredient):
        """Тест создания рецепта без тегов."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [],  # Пустой список
            "ingredients": [{"id": ingredient.id, "amount": 100}],
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "tags" in serializer.errors

    def test_recipe_creation_nonexistent_ingredient(self, tag):
        """Тест создания рецепта с несуществующим ингредиентом."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [{"id": 99999, "amount": 100}],  # Несуществующий ID
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors
        assert "не существует" in str(serializer.errors["ingredients"])

    def test_recipe_creation_invalid_ingredient_amount(self, tag, ingredient):
        """Тест создания рецепта с невалидным количеством ингредиента."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [
                {"id": ingredient.id, "amount": 0}
            ],  # Невалидное количество
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors

    def test_recipe_creation_duplicate_ingredients(self, tag, ingredient):
        """Тест создания рецепта с повторяющимися ингредиентами."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [
                {"id": ingredient.id, "amount": 100},
                {"id": ingredient.id, "amount": 200},  # Дубликат
            ],
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors

    def test_recipe_creation_duplicate_tags(self, tag, ingredient):
        """Тест создания рецепта с повторяющимися тегами."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id, tag.id],  # Дубликат
            "ingredients": [{"id": ingredient.id, "amount": 100}],
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "tags" in serializer.errors

    def test_recipe_creation_string_amount(self, tag, ingredient):
        """Тест создания рецепта с количеством ингредиента в виде строки."""
        data = {
            "name": "Тестовый рецепт",
            "text": "Описание рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [
                {"id": ingredient.id, "amount": "abc"}
            ],  # Строка вместо числа
        }

        serializer = RecipeCreateUpdateSerializer(data=data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors

    def test_recipe_update_nonexistent_ingredient(self, recipe, tag):
        """Тест обновления рецепта с несуществующим ингредиентом."""
        data = {
            "name": "Обновленный рецепт",
            "text": "Обновленное описание",
            "cooking_time": 45,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [{"id": 99999, "amount": 150}],  # Несуществующий ID
        }

        serializer = RecipeCreateUpdateSerializer(instance=recipe, data=data)
        assert not serializer.is_valid()
        assert "ingredients" in serializer.errors
        assert "не существует" in str(serializer.errors["ingredients"])

    def test_recipe_creation_valid_data(self, tag, ingredient, user):
        """Тест создания рецепта с валидными данными."""
        data = {
            "name": "Валидный рецепт",
            "text": "Описание валидного рецепта",
            "cooking_time": 30,
            "image": short_base64,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 100}],
        }

        context = {"request": type("Request", (), {"user": user})()}
        serializer = RecipeCreateUpdateSerializer(data=data, context=context)
        assert serializer.is_valid(), serializer.errors

        recipe = serializer.save()
        assert isinstance(recipe, Recipe)
        assert recipe.name == "Валидный рецепт"
        assert recipe.author == user

    def test_recipe_update_without_image(self, recipe, tag, ingredient):
        """Тест обновления рецепта без изображения."""
        data = {
            "name": "Обновленный рецепт",
            "text": "Обновленное описание",
            "cooking_time": 45,
            "tags": [tag.id],
            "ingredients": [{"id": ingredient.id, "amount": 150}],
        }

        serializer = RecipeCreateUpdateSerializer(instance=recipe, data=data)
        assert serializer.is_valid(), serializer.errors

        updated_recipe = serializer.save()
        assert updated_recipe.name == "Обновленный рецепт"
        assert updated_recipe.text == "Обновленное описание"
        assert updated_recipe.cooking_time == 45


@pytest.mark.django_db
class TestRecipeMinifiedSerializer:
    """Тесты минифицированного сериализатора рецептов."""

    def test_recipe_minified_serialization(self, recipe):
        """Тест минифицированной сериализации рецепта."""
        serializer = RecipeMinifiedSerializer(recipe)
        data = serializer.data

        assert data["id"] == recipe.id
        assert data["name"] == recipe.name
        assert data["cooking_time"] == recipe.cooking_time
        assert "image" in data
