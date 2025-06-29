"""Serializers for Foodgram API."""

from apps.recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from apps.users.models import Subscription
from django.contrib.auth import get_user_model
from django.db import transaction
from djoser.serializers import UserCreateSerializer
from djoser.serializers import UserSerializer as DjoserUserSerializer
from foodgram.constants import MAX_COOKING_TIME, MIN_COOKING_TIME
from rest_framework import serializers

from .fields import Base64ImageField

User = get_user_model()


class IngredientInRecipeCreateSerializer(serializers.Serializer):
    """Сериализатор для создания ингредиентов в рецепте."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        error_messages={
            "does_not_exist": "Ингредиент с указанным ID не существует."
        },
    )
    amount = serializers.IntegerField(
        error_messages={
            "invalid": "Количество ингредиента должно быть целым числом.",
            "required": "Укажите количество ингредиента.",
        },
    )

    def validate_amount(self, value):
        """Валидация количества ингредиента."""
        if value is None:
            raise serializers.ValidationError(
                "Укажите количество ингредиента."
            )
        if value <= 0:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть больше 0."
            )
        if value > 10000:
            raise serializers.ValidationError(
                "Количество ингредиента не может быть больше 10000."
            )
        return value

    def validate(self, data):
        """Дополнительная валидация данных ингредиента."""
        return data


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, obj):
        """Проверяет подписку текущего пользователя на данного."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user, author=obj
            ).exists()
        return False


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )

    def validate_email(self, value):
        """Валидация email."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким Email уже существует."
            )
        return value

    def validate_username(self, value):
        """Валидация username."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким Имя пользователя уже существует."
            )
        return value


class SetAvatarSerializer(serializers.Serializer):
    """Сериализатор для установки аватара пользователя."""

    avatar = Base64ImageField()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id",)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов в рецепте."""

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Минифицированный сериализатор рецепта для избранного/корзины."""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source="recipe_ingredients", many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = ("id", "author")

    def get_is_favorited(self, obj):
        """Проверяет находится ли рецепт в избранном."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Проверяет находится ли рецепт в списке покупок."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        return False


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления рецептов."""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = IngredientInRecipeCreateSerializer(
        many=True, write_only=True, required=True
    )
    image = Base64ImageField(required=False)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME, max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate(self, data):
        """Общая валидация данных рецепта."""
        # Проверяем обязательные поля
        required_fields = ["tags", "ingredients", "name", "text"]

        errors = {}

        for field in required_fields:
            if field not in data or not data[field]:
                if field == "tags":
                    errors[field] = ["Необходимо выбрать хотя бы один тег."]
                elif field == "ingredients":
                    errors[field] = [
                        "Необходимо добавить хотя бы один ингредиент."
                    ]
                elif field == "name":
                    errors[field] = ["Название рецепта обязательно."]
                elif field == "text":
                    errors[field] = ["Описание рецепта обязательно."]

        # Проверяем изображение только при создании нового рецепта
        if not self.instance and ("image" not in data or not data["image"]):
            errors["image"] = ["Необходимо загрузить изображение."]

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def validate_ingredients(self, value):
        """Валидация ингредиентов на уникальность."""
        if not value:
            raise serializers.ValidationError(
                "Необходимо добавить хотя бы один ингредиент."
            )

        # Используем множества для проверки дубликатов
        ingredient_ids = {item["id"].id for item in value}

        if len(ingredient_ids) != len(value):
            raise serializers.ValidationError(
                "Ингредиенты не должны повторяться."
            )

        return value

    def validate_tags(self, value):
        """Валидация тегов."""
        if not value:
            raise serializers.ValidationError(
                "Необходимо выбрать хотя бы один тег."
            )

        if len(value) != len(set(value)):
            raise serializers.ValidationError("Теги не должны повторяться.")

        return value

    @transaction.atomic
    def create(self, validated_data):
        """Создание нового рецепта."""
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")

        recipe = Recipe.objects.create(
            author=self.context["request"].user, **validated_data
        )

        self._create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновление рецепта."""
        tags = validated_data.pop("tags", None)
        ingredients = validated_data.pop("ingredients", None)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            instance.recipe_ingredients.all().delete()
            self._create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def _create_ingredients(self, recipe, ingredients):
        """Создание связей рецепта с ингредиентами."""
        ingredient_recipes = []

        for ingredient_data in ingredients:
            ingredient_recipes.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                )
            )

        IngredientInRecipe.objects.bulk_create(ingredient_recipes)

    def to_representation(self, instance):
        """Возвращает представление созданного рецепта."""
        return RecipeSerializer(instance, context=self.context).data


class UserWithRecipesSerializer(UserSerializer):
    """Сериализатор пользователя с рецептами для подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes(self, obj):
        """Возвращает рецепты пользователя."""
        request = self.context.get("request")
        recipes_limit = None

        if request:
            recipes_limit = request.query_params.get("recipes_limit")

        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[: int(recipes_limit)]
            except ValueError:
                pass

        return RecipeMinifiedSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов пользователя."""
        return obj.recipes.count()
