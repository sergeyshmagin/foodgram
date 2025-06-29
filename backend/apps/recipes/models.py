"""Recipe models for Foodgram project."""
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (
    MAX_COOKING_TIME,
    MAX_INGREDIENT_AMOUNT,
    MAX_INGREDIENT_NAME_LENGTH,
    MAX_INGREDIENT_UNIT_LENGTH,
    MAX_NAME_LENGTH,
    MAX_RECIPE_NAME_LENGTH,
    MAX_RECIPE_TEXT_LENGTH,
    MAX_SLUG_LENGTH,
    MAX_TAG_COLOR_LENGTH,
    MAX_TAG_NAME_LENGTH,
    MAX_TAG_SLUG_LENGTH,
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
)

User = get_user_model()


class TimeStampedModel(models.Model):
    """Абстрактная модель с полем даты создания."""

    created = models.DateTimeField(
        "Дата создания", auto_now_add=True, help_text="Дата создания записи"
    )

    class Meta:
        abstract = True


class UserActionModel(TimeStampedModel):
    """Абстрактная модель для действий пользователей.

    Используется для избранного, корзины покупок.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="%(class)s_set",
    )

    class Meta:
        abstract = True
        ordering = ["-created"]


class NameSlugModel(models.Model):
    """Абстрактная модель с полями name и slug."""

    name = models.CharField(
        "Название",
        max_length=MAX_NAME_LENGTH,
        unique=True,
        help_text="Уникальное название",
    )
    slug = models.SlugField(
        "Слаг",
        max_length=MAX_SLUG_LENGTH,
        unique=True,
        help_text="Уникальный слаг",
    )

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(NameSlugModel):
    """Модель тега для рецептов."""

    name = models.CharField(
        "Название",
        max_length=MAX_TAG_NAME_LENGTH,
        unique=True,
        help_text="Уникальное название тега",
    )
    color = models.CharField(
        "Цвет",
        max_length=MAX_TAG_COLOR_LENGTH,
        unique=True,
        help_text="Цвет в формате HEX (например, #FF0000)",
    )
    slug = models.SlugField(
        "Слаг",
        max_length=MAX_TAG_SLUG_LENGTH,
        unique=True,
        help_text="Уникальный слаг для тега",
    )

    class Meta(NameSlugModel.Meta):
        """Метаданные модели Tag."""

        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        "Название",
        max_length=MAX_INGREDIENT_NAME_LENGTH,
        help_text="Название ингредиента",
    )
    measurement_unit = models.CharField(
        "Единица измерения",
        max_length=MAX_INGREDIENT_UNIT_LENGTH,
        help_text="Единица измерения ингредиента",
    )

    class Meta:
        """Метаданные модели Ingredient."""

        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_unit",
            )
        ]

    def __str__(self):
        """Строковое представление ингредиента."""
        return f"{self.name} ({self.measurement_unit})"


class Recipe(models.Model):
    """Модель рецепта."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
        help_text="Автор рецепта",
    )
    name = models.CharField(
        "Название",
        max_length=MAX_RECIPE_NAME_LENGTH,
        help_text="Название рецепта",
    )
    image = models.ImageField(
        "Изображение", upload_to="recipes/", help_text="Изображение рецепта"
    )
    text = models.TextField(
        "Описание",
        max_length=MAX_RECIPE_TEXT_LENGTH,
        help_text="Описание рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="IngredientInRecipe",
        related_name="recipes",
        verbose_name="Ингредиенты",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Теги",
        help_text="Теги рецепта",
    )
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления",
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=(
                    f"Время приготовления не может быть меньше "
                    f"{MIN_COOKING_TIME} минуты"
                ),
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=(
                    f"Время приготовления не может быть больше "
                    f"{MAX_COOKING_TIME} минут"
                ),
            ),
        ],
        help_text="Время приготовления в минутах",
    )
    created = models.DateTimeField(
        "Дата создания", auto_now_add=True, help_text="Дата создания рецепта"
    )

    class Meta:
        """Метаданные модели Recipe."""

        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created"]

    def __str__(self):
        """Строковое представление рецепта."""
        return self.name


class IngredientInRecipe(models.Model):
    """Промежуточная модель для связи рецепта и ингредиентов."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient_recipes",
        verbose_name="Ингредиент",
    )
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=(
                    f"Количество не может быть меньше "
                    f"{MIN_INGREDIENT_AMOUNT}"
                ),
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=(
                    f"Количество не может быть больше "
                    f"{MAX_INGREDIENT_AMOUNT}"
                ),
            ),
        ],
        help_text="Количество ингредиента",
    )

    class Meta:
        """Метаданные модели IngredientInRecipe."""

        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"],
                name="unique_recipe_ingredient",
            )
        ]

    def __str__(self):
        """Строковое представление ингредиента в рецепте."""
        return f"{self.ingredient.name} в {self.recipe.name}"


class RecipeUserActionModel(UserActionModel):
    """Базовая модель для действий пользователей с рецептами."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="%(class)s_set",
    )

    class Meta(UserActionModel.Meta):
        abstract = True


class Favorite(RecipeUserActionModel):
    """Модель избранных рецептов."""

    class Meta(RecipeUserActionModel.Meta):
        """Метаданные модели Favorite."""

        verbose_name = "Избранное"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_user_favorite_recipe"
            )
        ]

    def __str__(self):
        """Строковое представление избранного рецепта."""
        return f"{self.user.username} добавил {self.recipe.name} в избранное"


class ShoppingCart(RecipeUserActionModel):
    """Модель списка покупок."""

    class Meta(RecipeUserActionModel.Meta):
        """Метаданные модели ShoppingCart."""

        verbose_name = "Корзина"
        verbose_name_plural = "Корзины покупок"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name="unique_user_shopping_cart_recipe",
            )
        ]

    def __str__(self):
        """Строковое представление корзины."""
        return f"{self.user.username} добавил {self.recipe.name} в корзину"
