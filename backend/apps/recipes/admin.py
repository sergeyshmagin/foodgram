"""Админ-панель для приложения recipes."""
from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe
from foodgram.constants import (
    ADMIN_LIST_PER_PAGE,
    ADMIN_LIST_PER_PAGE_LARGE,
    COLOR_PREVIEW_SIZE,
    IMAGE_PREVIEW_SIZE,
)

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)


class IngredientInRecipeInline(admin.TabularInline):
    """Inline для ингредиентов в рецепте."""

    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админ для модели Tag."""

    list_display = ("id", "name", "color_display", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_per_page = ADMIN_LIST_PER_PAGE

    @admin.display(description="Цвет")
    @mark_safe
    def color_display(self, obj):
        """Отображение цвета."""
        return (
            f'<div style="width: {COLOR_PREVIEW_SIZE}px; '
            f"height: {COLOR_PREVIEW_SIZE}px; "
            f'background-color: {obj.color}; border: 1px solid #ccc;"></div>'
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ для модели Ingredient."""

    list_display = ("id", "name", "measurement_unit", "recipes_count")
    list_display_links = ("id", "name")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)
    list_per_page = ADMIN_LIST_PER_PAGE_LARGE

    def get_queryset(self, request):
        """Оптимизированный queryset с аннотациями."""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            recipes_count_annotated=Count("ingredient_recipes", distinct=True)
        )

    @admin.display(
        description="Применений в рецептах", ordering="recipes_count_annotated"
    )
    def recipes_count(self, obj):
        """Количество применений ингредиента в рецептах."""
        return getattr(obj, "recipes_count_annotated", 0)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ для модели Recipe."""

    list_display = (
        "id",
        "name",
        "cooking_time_display",
        "author",
        "tags_display",
        "ingredients_display",
        "image_preview",
        "favorites_count",
    )
    list_display_links = ("id", "name")
    list_filter = ("tags", "created", "author")
    search_fields = ("name", "author__username", "author__email")
    readonly_fields = ("created", "image_preview", "favorites_count")
    filter_horizontal = ("tags",)
    inlines = (IngredientInRecipeInline,)
    list_per_page = ADMIN_LIST_PER_PAGE

    fieldsets = (
        (None, {"fields": ("name", "author", "image", "image_preview")}),
        ("Содержание", {"fields": ("text", "cooking_time", "tags")}),
        (
            "Информация",
            {
                "fields": ("created", "favorites_count"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_queryset(self, request):
        """Оптимизированный queryset с аннотациями."""
        queryset = super().get_queryset(request)
        return (
            queryset.select_related("author")
            .prefetch_related("tags", "recipe_ingredients__ingredient")
            .annotate(
                favorites_count_annotated=Count("favorites", distinct=True)
            )
        )

    @admin.display(description="Время готовки (мин)", ordering="cooking_time")
    def cooking_time_display(self, obj):
        """Отображение времени готовки."""
        return f"{obj.cooking_time} мин"

    @admin.display(description="Теги")
    @mark_safe
    def tags_display(self, obj):
        """Отображение тегов с цветами."""
        if not obj.tags.exists():
            return "—"

        tags_html = []
        for tag in obj.tags.all():
            tags_html.append(
                f'<span style="background-color: {tag.color}; '
                f"color: white; padding: 2px 6px; border-radius: 3px; "
                f'font-size: 10px; margin-right: 3px;">{tag.name}</span>'
            )
        return "".join(tags_html)

    @admin.display(description="Ингредиенты")
    @mark_safe
    def ingredients_display(self, obj):
        """Отображение ингредиентов."""
        ingredients = [
            ingredient_recipe.ingredient.name
            for ingredient_recipe in obj.recipe_ingredients.all()[:3]
        ]

        if not ingredients:
            return "—"

        result = ", ".join(ingredients)

        # Если ингредиентов больше 3, добавляем "..."
        total_count = obj.recipe_ingredients.count()
        if total_count > 3:
            result += f" <em>(+{total_count - 3} еще)</em>"

        return result

    @admin.display(description="Изображение")
    @mark_safe
    def image_preview(self, obj):
        """Предварительный просмотр изображения."""
        if obj.image:
            return (
                f'<img src="{obj.image.url}" width="{IMAGE_PREVIEW_SIZE}" '
                f'height="{IMAGE_PREVIEW_SIZE}" style="object-fit: cover; '
                f'border-radius: 4px; border: 1px solid #ddd;" />'
            )
        return '<span style="color: #999;">Нет изображения</span>'

    @admin.display(
        description="В избранном", ordering="favorites_count_annotated"
    )
    def favorites_count(self, obj):
        """Количество добавлений в избранное."""
        count = getattr(obj, "favorites_count_annotated", 0)
        if count == 0:
            return "0 раз"
        elif count == 1:
            return "1 раз"
        elif 2 <= count <= 4:
            return f"{count} раза"
        else:
            return f"{count} раз"


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админ для модели IngredientInRecipe."""

    list_display = ("id", "recipe", "ingredient", "amount")
    list_display_links = ("id",)
    list_filter = ("ingredient__measurement_unit",)
    search_fields = ("recipe__name", "ingredient__name")
    list_per_page = ADMIN_LIST_PER_PAGE_LARGE


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ для модели Favorite."""

    list_display = ("id", "user", "recipe", "created")
    list_display_links = ("id",)
    list_filter = ("created",)
    search_fields = ("user__username", "recipe__name")
    list_per_page = ADMIN_LIST_PER_PAGE_LARGE


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ для модели ShoppingCart."""

    list_display = ("id", "user", "recipe", "created")
    list_display_links = ("id",)
    list_filter = ("created",)
    search_fields = ("user__username", "recipe__name")
    list_per_page = ADMIN_LIST_PER_PAGE_LARGE


# Удаляем стандартную регистрацию Group из админки
try:
    from django.contrib.auth.models import Group

    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass
