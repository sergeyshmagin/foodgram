#!/usr/bin/env python3
"""
Скрипт для очистки тестовых данных на продакшене.
Удаляет тестовых пользователей, рецепты и связанные данные.
"""

import os
import sys
import django
from django.db import transaction

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings.production')
django.setup()

from django.db import models
from django.contrib.auth import get_user_model
from apps.recipes.models import Recipe, Favorite, ShoppingCart, Subscription, IngredientInRecipe

User = get_user_model()


def clear_test_users():
    """Очищает тестовых пользователей и связанные данные."""
    print("🧹 Очистка тестовых пользователей...")
    
    # Паттерны для определения тестовых пользователей
    test_patterns = [
        'test',
        'demo',
        'example',
        'admin@example.com',
        'user@example.com',
        'test@test.com',
        'admin@admin.com',
    ]
    
    # Создаем Q объекты для поиска тестовых пользователей
    test_q = models.Q()
    
    # Добавляем условия поиска по паттернам
    for pattern in test_patterns:
        test_q |= models.Q(username__icontains=pattern)
        test_q |= models.Q(email__icontains=pattern)
        test_q |= models.Q(first_name__icontains=pattern)
        test_q |= models.Q(last_name__icontains=pattern)
    
    # Добавляем условия для пустых полей
    test_q |= models.Q(username='')
    test_q |= models.Q(first_name='')
    test_q |= models.Q(last_name='')
    test_q |= models.Q(email='')
    
    # Получаем тестовых пользователей, исключая суперпользователей
    test_users = User.objects.filter(test_q).exclude(is_superuser=True)
    
    if test_users.exists():
        print(f"Найдено {test_users.count()} тестовых пользователей:")
        for user in test_users:
            print(f"  - {user.username} ({user.email})")
        
        with transaction.atomic():
            # Удаляем связанные данные
            recipes_count = Recipe.objects.filter(author__in=test_users).count()
            favorites_count = Favorite.objects.filter(user__in=test_users).count()
            cart_count = ShoppingCart.objects.filter(user__in=test_users).count()
            subs_count = Subscription.objects.filter(
                models.Q(user__in=test_users) | models.Q(author__in=test_users)
            ).count()
            
            # Удаляем данные
            Recipe.objects.filter(author__in=test_users).delete()
            Favorite.objects.filter(user__in=test_users).delete()
            ShoppingCart.objects.filter(user__in=test_users).delete()
            Subscription.objects.filter(
                models.Q(user__in=test_users) | models.Q(author__in=test_users)
            ).delete()
            
            # Удаляем пользователей
            users_count = test_users.count()
            test_users.delete()
            
            print(f"✅ Удалено:")
            print(f"  - {users_count} пользователей")
            print(f"  - {recipes_count} рецептов")
            print(f"  - {favorites_count} избранных")
            print(f"  - {cart_count} элементов корзины")
            print(f"  - {subs_count} подписок")
    else:
        print("✅ Тестовые пользователи не найдены")


def clear_invalid_recipes():
    """Очищает рецепты с некорректными данными."""
    print("\n🧹 Очистка некорректных рецептов...")
    
    # Создаем Q объект для поиска некорректных рецептов
    invalid_q = models.Q()
    
    # Рецепты без тегов
    invalid_q |= models.Q(tags__isnull=True)
    
    # Рецепты с пустыми полями
    invalid_q |= models.Q(name='')
    invalid_q |= models.Q(text='')
    invalid_q |= models.Q(cooking_time__lte=0)
    
    # Рецепты без ингредиентов
    recipes_with_ingredients = IngredientInRecipe.objects.values_list('recipe_id', flat=True)
    invalid_q |= ~models.Q(id__in=recipes_with_ingredients)
    
    invalid_recipes = Recipe.objects.filter(invalid_q).distinct()
    
    if invalid_recipes.exists():
        print(f"Найдено {invalid_recipes.count()} некорректных рецептов:")
        for recipe in invalid_recipes[:10]:  # Показываем первые 10
            print(f"  - {recipe.name} (ID: {recipe.id})")
        
        if invalid_recipes.count() > 10:
            print(f"  ... и еще {invalid_recipes.count() - 10} рецептов")
        
        with transaction.atomic():
            count = invalid_recipes.count()
            # Получаем ID рецептов для удаления
            recipe_ids = list(invalid_recipes.values_list('id', flat=True))
            Recipe.objects.filter(id__in=recipe_ids).delete()
            print(f"✅ Удалено {count} некорректных рецептов")
    else:
        print("✅ Некорректные рецепты не найдены")


def show_statistics():
    """Показывает статистику данных."""
    print("\n📊 Статистика данных:")
    print(f"  - Пользователей: {User.objects.count()}")
    print(f"  - Рецептов: {Recipe.objects.count()}")
    print(f"  - Избранных: {Favorite.objects.count()}")
    print(f"  - В корзине: {ShoppingCart.objects.count()}")
    print(f"  - Подписок: {Subscription.objects.count()}")


def main():
    """Основная функция."""
    print("🚀 Запуск очистки тестовых данных на продакшене...")
    
    try:        
        show_statistics()
        clear_test_users()
        clear_invalid_recipes()
        show_statistics()
        
        print("\n✅ Очистка завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при очистке данных: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 