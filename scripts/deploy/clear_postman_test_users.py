#!/usr/bin/env python3
"""
Скрипт для удаления конкретных тестовых пользователей Postman.
"""

import os
import sys

# Настройка Django окружения
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings.production')

import django
django.setup()

from django.db import models
from django.contrib.auth import get_user_model
from apps.recipes.models import Recipe, Favorite, ShoppingCart, Subscription

User = get_user_model()

def clear_postman_test_users():
    """Удаляет конкретных тестовых пользователей Postman."""
    print("🧹 Удаление тестовых пользователей Postman...")
    
    # Список тестовых пользователей для удаления
    test_users_data = [
        {'email': 'vivanov@yandex.ru', 'username': 'vasya.ivanov'},
        {'email': 'second_user@email.org', 'username': 'second-user'},
        {'email': 'third-user@user.ru', 'username': 'third-user-username'},
    ]
    
    deleted_count = 0
    
    for user_data in test_users_data:
        email = user_data['email']
        username = user_data['username']
        
        print(f"\n🔍 Поиск пользователя: {email} / {username}")
        
        # Ищем пользователей по email или username
        users_to_delete = User.objects.filter(
            models.Q(email__iexact=email) | models.Q(username__iexact=username)
        )
        
        for user in users_to_delete:
            print(f"  Найден: {user.email} / {user.username} (ID: {user.id})")
            
            # Удаляем связанные данные
            recipes_count = Recipe.objects.filter(author=user).count()
            favorites_count = Favorite.objects.filter(user=user).count()
            cart_count = ShoppingCart.objects.filter(user=user).count()
            subscriptions_count = Subscription.objects.filter(
                models.Q(user=user) | models.Q(author=user)
            ).count()
            
            if recipes_count > 0:
                Recipe.objects.filter(author=user).delete()
                print(f"    ↳ Удалено рецептов: {recipes_count}")
            
            if favorites_count > 0:
                Favorite.objects.filter(user=user).delete()
                print(f"    ↳ Удалено избранного: {favorites_count}")
            
            if cart_count > 0:
                ShoppingCart.objects.filter(user=user).delete()
                print(f"    ↳ Удалено из корзины: {cart_count}")
            
            if subscriptions_count > 0:
                Subscription.objects.filter(
                    models.Q(user=user) | models.Q(author=user)
                ).delete()
                print(f"    ↳ Удалено подписок: {subscriptions_count}")
            
            # Удаляем пользователя
            user.delete()
            print(f"  ✅ Пользователь {email} удален")
            deleted_count += 1
    
    print(f"\n🎯 Итого удалено пользователей: {deleted_count}")
    return deleted_count

def check_current_state():
    """Проверяет текущее состояние данных."""
    print("\n📊 Текущее состояние базы данных:")
    
    total_users = User.objects.count()
    total_recipes = Recipe.objects.count()
    total_favorites = Favorite.objects.count()
    total_cart = ShoppingCart.objects.count()
    total_subscriptions = Subscription.objects.count()
    
    print(f"Пользователей: {total_users}")
    print(f"Рецептов: {total_recipes}")
    print(f"Избранного: {total_favorites}")
    print(f"В корзине: {total_cart}")
    print(f"Подписок: {total_subscriptions}")

def verify_test_users_removed():
    """Проверяет что тестовые пользователи удалены."""
    print("\n🔍 Проверка отсутствия тестовых пользователей...")
    
    test_emails = [
        'vivanov@yandex.ru',
        'second_user@email.org', 
        'third-user@user.ru'
    ]
    
    test_usernames = [
        'vasya.ivanov',
        'second-user',
        'third-user-username'
    ]
    
    remaining_users = User.objects.filter(
        models.Q(email__in=test_emails) | models.Q(username__in=test_usernames)
    )
    
    if remaining_users.exists():
        print("❌ Остались тестовые пользователи:")
        for user in remaining_users:
            print(f"  - {user.email} / {user.username}")
        return False
    else:
        print("✅ Все тестовые пользователи удалены!")
        return True

if __name__ == '__main__':
    print("🚀 Запуск очистки тестовых пользователей Postman...")
    
    try:        
        print("📋 Состояние ДО очистки:")
        check_current_state()
        
        deleted_count = clear_postman_test_users()
        
        print("\n📋 Состояние ПОСЛЕ очистки:")
        check_current_state()
        
        if verify_test_users_removed():
            print("\n✅ Очистка завершена успешно!")
            print("🚀 Теперь Postman тесты регистрации должны проходить!")
        else:
            print("\n❌ Не все тестовые пользователи удалены!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при очистке: {e}")
        import traceback
        traceback.print_exc() 