#!/bin/bash

# 🚀 Быстрое развертывание Foodgram на продакшене
# Использование: ./quick_deploy.sh

set -e

echo "🚀 === БЫСТРОЕ РАЗВЕРТЫВАНИЕ FOODGRAM ==="
echo "Начало деплоя: $(date)"

# Проверяем, что мы в правильной директории
if [ ! -f "infra/docker-compose.yml" ]; then
    echo "❌ Ошибка: не найден файл infra/docker-compose.yml"
    echo "Запустите скрипт из корневой директории проекта"
    exit 1
fi

# Останавливаем старые контейнеры
echo "🛑 Остановка старых контейнеров..."
docker compose -f infra/docker-compose.yml down --remove-orphans || echo "Нет запущенных контейнеров"

# Очищаем неиспользуемые ресурсы Docker
echo "🧹 Очистка Docker ресурсов..."
docker system prune -f || echo "Не удалось очистить Docker ресурсы"

# Освобождаем порт 80
echo "🔧 Освобождение порта 80..."
sudo systemctl stop nginx 2>/dev/null || echo "Системный nginx не запущен"
sudo fuser -k 80/tcp 2>/dev/null || echo "Порт 80 свободен"

# Сборка и запуск
echo "🔨 Сборка и запуск контейнеров..."
docker compose -f infra/docker-compose.yml up -d --build

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 30

# Применение миграций
echo "🗃️ Применение миграций базы данных..."
docker exec foodgram-backend python manage.py migrate

# Создание суперпользователя если нужно
echo "👤 Проверка суперпользователя..."
docker exec foodgram-backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('⚠️ Суперпользователь не найден!')
    print('Используйте команду create_admin_safe для безопасного создания:')
    print('docker exec foodgram-backend python manage.py create_admin_safe')
    print('Или установите переменные окружения ADMIN_EMAIL и ADMIN_PASSWORD')
else:
    print('✅ Суперпользователь уже существует')
"

# Загрузка начальных данных
echo "📦 Загрузка ингредиентов..."
docker exec foodgram-backend python manage.py load_ingredients

# Сбор статики
echo "🎨 Сбор статических файлов..."
docker exec foodgram-backend python manage.py collectstatic --noinput

# Проверка статуса контейнеров
echo "📊 Проверка статуса контейнеров..."
docker compose -f infra/docker-compose.yml ps

# Проверка доступности API
echo "🌐 Проверка доступности API..."
sleep 5
curl -f http://localhost/api/ >/dev/null 2>&1 && echo "✅ API доступен" || echo "⚠️ API недоступен"

echo "✅ === ДЕПЛОЙ ЗАВЕРШЕН ==="
echo "🌐 Сайт: http://localhost"
echo "🔧 Админ: http://localhost/admin"
echo "📡 API: http://localhost/api"
echo "Время завершения: $(date)" 