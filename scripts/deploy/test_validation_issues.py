#!/usr/bin/env python3
"""
Скрипт для тестирования и исправления проблем валидации API.
"""

import os
import sys
import json
import logging
from io import StringIO

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings.production')

import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from apps.recipes.models import Recipe, Tag, Ingredient

User = get_user_model()

def test_recipe_validation():
    """Тестирует валидацию рецептов."""
    print("🧪 Тестирование валидации рецептов...")
    
    # Создаем пользователя для теста
    user = User.objects.create_user(
        username='test_validation_user',
        email='test_val@example.com',
        password='testpass123'
    )
    
    # Создаем API клиент
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Создаем тег для тестов
    tag = Tag.objects.get_or_create(
        name='Тестовый',
        slug='test'
    )[0]
    
    # Создаем ингредиент для тестов
    ingredient = Ingredient.objects.get_or_create(
        name='Тестовый ингредиент',
        measurement_unit='шт'
    )[0]
    
    # Тестовое изображение
    test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg=="
    
    print("\n📝 Тест 1: Создание рецепта без ингредиентов")
    recipe_data_no_ingredients = {
        "tags": [tag.id],
        "image": test_image,
        "name": "Нет поля с ингредиентами",
        "text": "Ингредиенты не указаны",
        "cooking_time": 12
    }
    
    response = client.post('/api/v1/recipes/', data=recipe_data_no_ingredients, format='json')
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.data}")
    
    if response.status_code == 201:
        print("❌ ОШИБКА: Рецепт создался без ингредиентов!")
    else:
        print("✅ ОК: Рецепт правильно отклонен")
    
    print("\n📝 Тест 2: Создание рецепта без тегов")
    recipe_data_no_tags = {
        "ingredients": [{"id": ingredient.id, "amount": 25}],
        "image": test_image,
        "name": "Нет поля с тегами",
        "text": "Теги не указаны",
        "cooking_time": 12
    }
    
    response = client.post('/api/v1/recipes/', data=recipe_data_no_tags, format='json')
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.data}")
    
    if response.status_code == 201:
        print("❌ ОШИБКА: Рецепт создался без тегов!")
    else:
        print("✅ ОК: Рецепт правильно отклонен")
    
    print("\n📝 Тест 3: Создание корректного рецепта")
    correct_recipe_data = {
        "tags": [tag.id],
        "ingredients": [{"id": ingredient.id, "amount": 25}],
        "image": test_image,
        "name": "Корректный рецепт",
        "text": "Все поля заполнены",
        "cooking_time": 15
    }
    
    response = client.post('/api/v1/recipes/', data=correct_recipe_data, format='json')
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.data}")
    
    if response.status_code == 201:
        print("✅ ОК: Корректный рецепт создан")
        # Удаляем созданный рецепт
        if 'id' in response.data:
            Recipe.objects.filter(id=response.data['id']).delete()
    else:
        print("❌ ОШИБКА: Корректный рецепт не создался!")
    
    # Удаляем тестового пользователя
    user.delete()

def test_user_registration():
    """Тестирует регистрацию пользователей."""
    print("\n👤 Тестирование регистрации пользователей...")
    
    client = APIClient()
    
    # Создаем существующего пользователя
    existing_user = User.objects.create_user(
        username='existing_user',
        email='existing@example.com',
        password='testpass123'
    )
    
    print("\n📝 Тест: Регистрация с существующими данными")
    duplicate_data = {
        "email": "existing@example.com",
        "username": "existing_user",
        "first_name": "Тест",
        "last_name": "Тестов",
        "password": "MySecretPas$word"
    }
    
    response = client.post('/api/v1/users/', data=duplicate_data, format='json')
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.data}")
    
    if response.status_code == 400:
        print("✅ ОК: Дубликаты правильно отклонены")
    else:
        print("❌ ОШИБКА: Дубликаты не отклонены!")
    
    # Удаляем тестового пользователя
    existing_user.delete()

if __name__ == '__main__':
    print("🚀 Запуск тестирования проблем валидации...")
    
    try:
        test_recipe_validation()
        test_user_registration()
        print("\n✅ Тестирование завершено!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc() 