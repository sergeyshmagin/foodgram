"""URL configuration for Foodgram API."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet, health_check

app_name = 'api'

# Создаем роутер и регистрируем ViewSets
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # Health check endpoint
    path('health/', health_check, name='health-check'),
    
    # API endpoints
    path('', include(router.urls)),
    
    # Djoser authentication endpoints
    path('auth/', include('djoser.urls.authtoken')),
] 