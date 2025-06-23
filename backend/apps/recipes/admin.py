"""Admin configuration for recipes app."""
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
    Subscription,
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
    def color_display(self, obj):
        """Отображение цвета."""
        return mark_safe(
            f'<div style="width: {COLOR_PREVIEW_SIZE}px; '
            f"height: {COLOR_PREVIEW_SIZE}px; "
            f'background-color: {obj.color}; border: 1px solid #ccc;"></div>'
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ для модели Ingredient."""

    list_display = ("id", "name", "measurement_unit")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    list_filter = ("measurement_unit",)
    list_per_page = ADMIN_LIST_PER_PAGE_LARGE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ для модели Recipe."""

    list_display = (
        "id",
        "name",
        "author",
        "image_preview",
        "cooking_time",
        "favorites_count",
        "created",
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
            .prefetch_related("tags")
            .annotate(favorites_count_annotated=Count("favorited_by"))
        )

    @admin.display(description="Изображение")
    def image_preview(self, obj):
        """Предварительный просмотр изображения."""
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="{IMAGE_PREVIEW_SIZE}" '
                f'height="{IMAGE_PREVIEW_SIZE}" style="object-fit: cover;" />'
            )
        return "—"

    @admin.display(
        description="В избранном", ordering="favorites_count_annotated"
    )
    def favorites_count(self, obj):
        """Количество добавлений в избранное."""
        return getattr(obj, "favorites_count_annotated", 0)


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


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Админ для модели Subscription."""

    list_display = ("id", "user", "author", "created")
    list_display_links = ("id",)
    list_filter = ("created",)
    search_fields = ("user__username", "author__username")
    list_per_page = ADMIN_LIST_PER_PAGE_LARGE
