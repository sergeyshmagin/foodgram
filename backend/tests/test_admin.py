"""Тесты админки Django для Foodgram."""
import pytest
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.recipes.admin import RecipeAdmin, TagAdmin, IngredientAdmin
from apps.recipes.models import Recipe, Tag, Ingredient
from apps.users.admin import CustomUserAdmin

User = get_user_model()


@pytest.mark.django_db
class TestRecipeAdmin:
    """Тесты админки рецептов."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.site = AdminSite()
        self.admin = RecipeAdmin(Recipe, self.site)
        self.factory = RequestFactory()

    def test_recipe_admin_list_display(self):
        """Тест отображения списка рецептов в админке."""
        expected_fields = (
            "id",
            "name",
            "author",
            "image_preview",
            "cooking_time",
            "favorites_count",
            "created",
        )
        assert self.admin.list_display == expected_fields

    def test_recipe_admin_list_filter(self):
        """Тест фильтров в админке рецептов."""
        expected_filters = ("tags", "created", "author")
        assert self.admin.list_filter == expected_filters

    def test_recipe_admin_search_fields(self):
        """Тест полей поиска в админке рецептов."""
        expected_fields = ("name", "author__username", "author__email")
        assert self.admin.search_fields == expected_fields

    def test_favorites_count_method(self, user, recipe):
        """Тест метода подсчета избранного."""
        # Создаем избранное
        from apps.recipes.models import Favorite

        Favorite.objects.create(user=user, recipe=recipe)

        # Получаем рецепт с аннотацией как в админке
        from django.db.models import Count

        from apps.recipes.models import Recipe

        recipe_with_annotation = Recipe.objects.annotate(
            favorites_count_annotated=Count("favorited_by")
        ).get(pk=recipe.pk)

        # Проверяем метод
        count = self.admin.favorites_count(recipe_with_annotation)
        assert count == 1

    def test_favorites_count_method_zero(self, recipe):
        """Тест метода подсчета избранного когда 0."""
        count = self.admin.favorites_count(recipe)
        assert count == 0

    def test_favorites_count_display_description(self):
        """Тест описания метода favorites_count."""
        assert hasattr(self.admin.favorites_count, "short_description")
        assert self.admin.favorites_count.short_description == "В избранном"


@pytest.mark.django_db
class TestCustomUserAdmin:
    """Тесты кастомной админки пользователей."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.site = AdminSite()
        self.admin = CustomUserAdmin(User, self.site)

    def test_user_admin_list_display(self):
        """Тест отображения списка пользователей."""
        expected_fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar_preview",
            "is_active",
            "date_joined",
        )
        assert self.admin.list_display == expected_fields

    def test_user_admin_search_fields(self):
        """Тест полей поиска в админке пользователей."""
        expected_fields = ("username", "email", "first_name", "last_name")
        assert self.admin.search_fields == expected_fields

    def test_user_admin_ordering(self):
        """Тест сортировки в админке пользователей."""
        expected_ordering = ("-date_joined",)
        assert self.admin.ordering == expected_ordering


@pytest.mark.django_db
class TestTagAdmin:
    """Тесты админки тегов."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.site = AdminSite()
        self.admin = TagAdmin(Tag, self.site)

    def test_tag_admin_registered(self):
        """Тест регистрации TagAdmin."""
        assert admin.site.is_registered(Tag)

    def test_tag_admin_list_display(self):
        """Тест отображения списка тегов."""
        expected_fields = ("id", "name", "color_display", "slug")
        assert self.admin.list_display == expected_fields


@pytest.mark.django_db
class TestIngredientAdmin:
    """Тесты админки ингредиентов."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.site = AdminSite()
        self.admin = IngredientAdmin(Ingredient, self.site)

    def test_ingredient_admin_registered(self):
        """Тест регистрации IngredientAdmin."""
        assert admin.site.is_registered(Ingredient)

    def test_ingredient_admin_list_display(self):
        """Тест отображения списка ингредиентов."""
        expected_fields = ("id", "name", "measurement_unit")
        assert self.admin.list_display == expected_fields

    def test_ingredient_admin_search_fields(self):
        """Тест полей поиска в админке ингредиентов."""
        expected_fields = ("name",)
        assert self.admin.search_fields == expected_fields


@pytest.mark.django_db
class TestAdminRegistration:
    """Тесты регистрации моделей в админке."""

    def test_recipe_registered(self):
        """Тест регистрации модели Recipe."""
        assert admin.site.is_registered(Recipe)

    def test_tag_registered(self):
        """Тест регистрации модели Tag."""
        assert admin.site.is_registered(Tag)

    def test_ingredient_registered(self):
        """Тест регистрации модели Ingredient."""
        assert admin.site.is_registered(Ingredient)

    def test_user_registered(self):
        """Тест регистрации кастомной модели User."""
        assert admin.site.is_registered(User)

    def test_group_unregistered(self):
        """Тест что модель Group удалена из админки."""
        from django.contrib.auth.models import Group

        assert not admin.site.is_registered(Group)


@pytest.mark.django_db
class TestAdminPermissions:
    """Тесты прав доступа в админке."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        self.admin = RecipeAdmin(Recipe, self.site)

    def test_admin_access_for_superuser(self, superuser):
        """Тест доступа суперпользователя к админке."""
        request = self.factory.get("/admin/")
        request.user = superuser

        assert self.admin.has_module_permission(request)
        assert self.admin.has_view_permission(request)
        assert self.admin.has_add_permission(request)
        assert self.admin.has_change_permission(request)
        assert self.admin.has_delete_permission(request)

    def test_admin_access_for_staff_user(self, staff_user):
        """Тест доступа staff пользователя к админке."""
        # Добавляем права на просмотр рецептов
        from django.contrib.auth.models import Permission

        permission = Permission.objects.get(codename="view_recipe")
        staff_user.user_permissions.add(permission)

        request = self.factory.get("/admin/")
        request.user = staff_user

        assert self.admin.has_module_permission(request)

    def test_admin_no_access_for_regular_user(self, user):
        """Тест отсутствия доступа обычного пользователя к админке."""
        request = self.factory.get("/admin/")
        request.user = user

        assert not self.admin.has_module_permission(request)


@pytest.mark.django_db
class TestAdminInlines:
    """Тесты inline админки."""

    def setup_method(self):
        """Настройка для каждого теста."""
        self.site = AdminSite()
        self.admin = RecipeAdmin(Recipe, self.site)

    def test_recipe_has_ingredient_inline(self):
        """Тест наличия inline для ингредиентов рецепта."""
        # Проверяем что есть inline для RecipeIngredient
        assert hasattr(self.admin, "inlines")
        assert len(self.admin.inlines) > 0
