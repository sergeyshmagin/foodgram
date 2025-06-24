#!/usr/bin/env python3
"""
Скрипт для исправления рецептов с некорректными данными.
Добавляет теги и исправляет данные рецептов.
"""

import os
import sys
import django
from django.db import transaction

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings.production')
django.setup()

from django.db import models
from apps.recipes.models import Recipe, Tag, IngredientInRecipe


def fix_recipes_without_tags():
    """Исправляет рецепты без тегов."""
    print("🔧 Исправление рецептов без тегов...")
    
    # Находим рецепты без тегов
    recipes_without_tags = Recipe.objects.filter(tags__isnull=True).distinct()
    
    if recipes_without_tags.exists():
        print(f"Найдено {recipes_without_tags.count()} рецептов без тегов:")
        
        # Получаем первый доступный тег или создаем дефолтный
        default_tag = Tag.objects.first()
        if not default_tag:
            default_tag = Tag.objects.create(
                name="Без категории",
                slug="no-category"
            )
            print(f"Создан дефолтный тег: {default_tag.name}")
        
        for recipe in recipes_without_tags:
            print(f"  - {recipe.name} (ID: {recipe.id})")
            recipe.tags.add(default_tag)
        
        print(f"✅ Добавлен тег '{default_tag.name}' к {recipes_without_tags.count()} рецептам")
    else:
        print("✅ Все рецепты имеют теги")


def fix_recipes_without_ingredients():
    """Исправляет рецепты без ингредиентов."""
    print("\n🔧 Исправление рецептов без ингредиентов...")
    
    # Находим рецепты без ингредиентов
    recipes_with_ingredients = IngredientInRecipe.objects.values_list('recipe_id', flat=True)
    recipes_without_ingredients = Recipe.objects.exclude(id__in=recipes_with_ingredients)
    
    if recipes_without_ingredients.exists():
        print(f"Найдено {recipes_without_ingredients.count()} рецептов без ингредиентов:")
        for recipe in recipes_without_ingredients:
            print(f"  - {recipe.name} (ID: {recipe.id})")
        
        # Эти рецепты нужно удалить, так как без ингредиентов они некорректны
        count = recipes_without_ingredients.count()
        recipes_without_ingredients.delete()
        print(f"✅ Удалено {count} рецептов без ингредиентов")
    else:
        print("✅ Все рецепты имеют ингредиенты")


def fix_recipes_with_empty_fields():
    """Исправляет рецепты с пустыми полями."""
    print("\n🔧 Исправление рецептов с пустыми полями...")
    
    # Находим рецепты с пустыми полями
    recipes_with_empty_fields = Recipe.objects.filter(
        models.Q(name='') |
        models.Q(text='') |
        models.Q(cooking_time__lte=0)
    )
    
    if recipes_with_empty_fields.exists():
        print(f"Найдено {recipes_with_empty_fields.count()} рецептов с пустыми полями:")
        
        for recipe in recipes_with_empty_fields:
            print(f"  - {recipe.name or 'Без названия'} (ID: {recipe.id})")
            
            # Исправляем пустые поля
            if not recipe.name:
                recipe.name = f"Рецепт #{recipe.id}"
            if not recipe.text:
                recipe.text = "Описание рецепта не указано."
            if recipe.cooking_time <= 0:
                recipe.cooking_time = 30  # Дефолтное время 30 минут
            
            recipe.save()
        
        print(f"✅ Исправлено {recipes_with_empty_fields.count()} рецептов")
    else:
        print("✅ Все рецепты имеют корректные поля")


def validate_all_recipes():
    """Проверяет все рецепты на корректность."""
    print("\n📋 Валидация всех рецептов...")
    
    total_recipes = Recipe.objects.count()
    valid_recipes = 0
    invalid_recipes = []
    
    for recipe in Recipe.objects.all():
        is_valid = True
        errors = []
        
        # Проверяем обязательные поля
        if not recipe.name:
            is_valid = False
            errors.append("пустое название")
        
        if not recipe.text:
            is_valid = False
            errors.append("пустое описание")
        
        if recipe.cooking_time <= 0:
            is_valid = False
            errors.append("некорректное время готовки")
        
        # Проверяем теги
        if not recipe.tags.exists():
            is_valid = False
            errors.append("нет тегов")
        
        # Проверяем ингредиенты
        if not recipe.recipe_ingredients.exists():
            is_valid = False
            errors.append("нет ингредиентов")
        
        if is_valid:
            valid_recipes += 1
        else:
            invalid_recipes.append((recipe, errors))
    
    print(f"✅ Корректных рецептов: {valid_recipes}/{total_recipes}")
    
    if invalid_recipes:
        print(f"❌ Некорректных рецептов: {len(invalid_recipes)}")
        for recipe, errors in invalid_recipes:
            print(f"  - {recipe.name} (ID: {recipe.id}): {', '.join(errors)}")
    
    return len(invalid_recipes) == 0


def main():
    """Основная функция."""
    print("🚀 Запуск исправления рецептов...")
    
    try:
        fix_recipes_with_empty_fields()
        fix_recipes_without_tags()
        fix_recipes_without_ingredients()
        
        if validate_all_recipes():
            print("\n✅ Все рецепты корректны!")
        else:
            print("\n⚠️ Некоторые рецепты всё ещё требуют внимания")
        
        print("\n🎯 Исправление завершено!")
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении рецептов: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 