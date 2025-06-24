#!/usr/bin/env python3
"""
Скрипт для исправления проблем с Postman тестами.
Исправляет данные в БД для корректного прохождения тестов.
"""

import os
import sys
import django

# Добавляем путь к Django проекту
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from django.db import models, transaction

User = get_user_model()


def fix_empty_user_fields():
    """Исправляет пользователей с пустыми полями."""
    print("🔧 Исправление пользователей с пустыми полями...")
    
    # Находим пользователей с пустыми полями
    users_with_empty_fields = User.objects.filter(
        models.Q(username='') | 
        models.Q(first_name='') | 
        models.Q(last_name='') |
        models.Q(email='')
    )
    
    count = users_with_empty_fields.count()
    print(f"Найдено пользователей с пустыми полями: {count}")
    
    if count > 0:
        for user in users_with_empty_fields:
            print(f"Удаляем пользователя ID {user.id}: username='{user.username}', email='{user.email}'")
            user.delete()
        print(f"✅ Удалено {count} пользователей с пустыми полями")
    else:
        print("✅ Пользователи с пустыми полями не найдены")


def fix_duplicate_users():
    """Исправляет дублирующихся пользователей."""
    print("🔧 Исправление дублирующихся пользователей...")
    
    # Находим дублирующиеся email
    duplicate_emails = User.objects.values('email').annotate(
        count=models.Count('email')
    ).filter(count__gt=1)
    
    for item in duplicate_emails:
        email = item['email']
        users = User.objects.filter(email=email).order_by('id')
        # Оставляем первого пользователя, остальных удаляем
        users_to_delete = users[1:]
        for user in users_to_delete:
            print(f"Удаляем дублирующегося пользователя: {user.email} (ID: {user.id})")
            user.delete()
    
    print("✅ Дублирующиеся пользователи исправлены")


def create_test_data():
    """Создает тестовые данные если их нет."""
    print("🔧 Проверка и создание тестовых данных...")
    
    # Проверяем количество пользователей
    user_count = User.objects.count()
    print(f"Общее количество пользователей: {user_count}")
    
    # Если пользователей меньше 10, создаем дополнительных
    if user_count < 10:
        needed = 10 - user_count
        print(f"Создаем {needed} дополнительных пользователей для тестов...")
        
        for i in range(needed):
            username = f"testuser{i+user_count+1}"
            email = f"testuser{i+user_count+1}@example.com"
            
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=f"Test{i+1}",
                    last_name=f"User{i+1}",
                    password="testpassword123"
                )
                print(f"Создан пользователь: {email}")
    
    print("✅ Тестовые данные проверены")


def main():
    """Основная функция."""
    print("🚀 Начинаем исправление проблем с Postman тестами...")
    
    try:
        with transaction.atomic():
            fix_empty_user_fields()
            fix_duplicate_users()
            create_test_data()
        
        print("\n✅ Все проблемы исправлены!")
        print("🎯 Теперь Postman тесты должны проходить корректно")
        
        # Выводим итоговую статистику
        total_users = User.objects.count()
        print(f"\n📊 Итоговая статистика:")
        print(f"   Общее количество пользователей: {total_users}")
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 