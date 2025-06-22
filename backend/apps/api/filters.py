"""Filters for Foodgram API."""
from django_filters import rest_framework as filters
from django.contrib.auth import get_user_model

from apps.recipes.models import Recipe, Ingredient

User = get_user_model()


class IngredientFilter(filters.FilterSet):
    """Фильтр для поиска ингредиентов по имени."""
    
    name = filters.CharFilter(lookup_expr='istartswith')
    
    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    """Фильтр для рецептов."""
    
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр по избранным рецептам."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтр по рецептам в корзине покупок."""
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset
