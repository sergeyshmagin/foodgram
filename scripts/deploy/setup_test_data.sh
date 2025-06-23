#!/bin/bash

set -e

echo "🚀 ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ FOODGRAM"

# Переходим в рабочую директорию
cd ~/foodgram

echo "📦 Загрузка ингредиентов..."
sudo docker compose -f infra/docker-compose.yml exec backend python manage.py load_ingredients

echo "👤 Создание администратора и тестовых данных..."
sudo docker compose -f infra/docker-compose.yml exec backend python manage.py setup_foodgram

echo "🏗️ Настройка MinIO..."
sudo docker compose -f infra/docker-compose.yml exec backend python manage.py setup_minio

echo "📊 Проверка статуса..."
sudo docker compose -f infra/docker-compose.yml exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.recipes.models import Recipe, Tag, Ingredient
User = get_user_model()
print(f'Пользователи: {User.objects.count()}')
print(f'Рецепты: {Recipe.objects.count()}')
print(f'Теги: {Tag.objects.count()}')
print(f'Ингредиенты: {Ingredient.objects.count()}')
"

echo "✅ ГОТОВО! Тестовые данные загружены"
echo ""
echo "🔑 УЧЕТНЫЕ ДАННЫЕ:"
echo "👨‍💻 Администратор:"
echo "   Email: admin@foodgram.ru"
echo "   Пароль: admin123"
echo ""
echo "👤 Тестовый пользователь:"
echo "   Email: test@foodgram.ru"
echo "   Пароль: testpass123"
echo ""
echo "🌐 Сайт: https://foodgram.freedynamicdns.net"
echo "🔧 Админка: https://foodgram.freedynamicdns.net/admin/" 