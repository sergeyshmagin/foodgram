#!/bin/bash

# Скрипт для очистки тестовых пользователей с некорректными данными

echo "🧹 Очистка тестовых пользователей..."

# Переходим в директорию backend
cd "$(dirname "$0")/../../backend" || exit 1

# Активируем виртуальное окружение если оно есть
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Очищаем пользователей с пустыми полями
python3 manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Находим и удаляем пользователей с пустыми полями
users_to_fix = User.objects.filter(
    models.Q(username='') | 
    models.Q(first_name='') | 
    models.Q(last_name='') |
    models.Q(email='')
)

print(f"Найдено пользователей для исправления: {users_to_fix.count()}")

for user in users_to_fix:
    print(f"Удаляем пользователя ID {user.id}: username='{user.username}', email='{user.email}'")
    user.delete()

print("✅ Очистка завершена!")
EOF

echo "✅ Скрипт очистки тестовых пользователей выполнен!" 