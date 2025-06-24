#!/bin/bash

# Скрипт для исправления проблем с отображением картинок MinIO

set -e

echo "🔧 Исправляем настройки MinIO для отображения картинок..."

cd /home/yc-user/foodgram

echo "📦 Проверяем статус контейнеров..."
sudo docker compose -f infra/docker-compose.yml ps

echo "🔗 Настраиваем MinIO client alias..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc alias set minio http://localhost:9000 minio_access_key minio_secret_key_123

echo "📁 Проверяем bucket foodgram..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc ls minio/

echo "🔓 Устанавливаем публичную политику для bucket..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc anonymous set public minio/foodgram

echo "🌐 Настраиваем CORS политику правильно..."

# Создаем временный файл с CORS конфигурацией
sudo docker compose -f infra/docker-compose.yml exec -T minio sh -c 'cat > /tmp/cors.json << EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "POST", "PUT", "DELETE", "HEAD"],
      "AllowedHeaders": ["*"],
      "ExposeHeaders": ["ETag"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF'

# Применяем CORS конфигурацию из файла
sudo docker compose -f infra/docker-compose.yml exec -T minio mc cors set /tmp/cors.json minio/foodgram

echo "📋 Проверяем CORS настройки..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc cors get minio/foodgram

echo "🔧 Обновляем переменные окружения с правильными настройками MinIO..."

# Проверяем файл .env
if [ -f infra/.env ]; then
    echo "📝 Обновляем infra/.env..."
    
    # Обновляем или добавляем MINIO_PUBLIC_ENDPOINT
    if grep -q "MINIO_PUBLIC_ENDPOINT" infra/.env; then
        sed -i 's/MINIO_PUBLIC_ENDPOINT=.*/MINIO_PUBLIC_ENDPOINT=89.169.174.76:9000/' infra/.env
    else
        echo "MINIO_PUBLIC_ENDPOINT=89.169.174.76:9000" >> infra/.env
    fi
    
    # Обновляем ключи доступа на правильные
    sed -i 's/MINIO_ACCESS_KEY=.*/MINIO_ACCESS_KEY=minio_access_key/' infra/.env
    sed -i 's/MINIO_SECRET_KEY=.*/MINIO_SECRET_KEY=minio_secret_key_123/' infra/.env
    
    echo "✅ Файл .env обновлен"
else
    echo "❌ Файл infra/.env не найден!"
fi

echo "🚀 Рестартуем backend для применения изменений..."
sudo docker compose -f infra/docker-compose.yml restart backend

# Ждем запуска backend
echo "⏱️ Ожидаем запуск backend..."
sleep 15

echo "🔍 Проверяем настройки Django..."
sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
import os
from django.conf import settings
print('🔍 Текущие настройки MinIO:')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}')
print(f'AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}')
print(f'AWS_S3_CUSTOM_DOMAIN: {getattr(settings, \"AWS_S3_CUSTOM_DOMAIN\", \"Не установлен\")}')
print(f'MINIO_PUBLIC_ENDPOINT: {os.environ.get(\"MINIO_PUBLIC_ENDPOINT\", \"Не установлен\")}')

print('📁 Тестируем подключение к MinIO...')
from django.core.files.storage import default_storage
try:
    bucket_name = default_storage.bucket_name
    print(f'✅ Подключение к MinIO работает! Bucket: {bucket_name}')
except Exception as e:
    print(f'❌ Ошибка подключения к MinIO: {e}')
"

echo "🌐 Тестируем доступность MinIO через публичный URL..."
curl -I http://89.169.174.76:9000/minio/health/live || echo "⚠️ MinIO недоступен через публичный URL"

echo "📁 Проверяем, есть ли файлы в bucket..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc ls minio/foodgram/media/ --recursive || echo "📝 Папка media пуста или не существует"

echo "🔄 Проверяем, запущен ли frontend..."
if ! sudo docker compose -f infra/docker-compose.yml ps | grep -q frontend; then
    echo "⚠️ Frontend контейнер не запущен. Запускаем все сервисы..."
    sudo docker compose -f infra/docker-compose.yml up -d
    sleep 10
fi

echo "📊 Финальная проверка всех контейнеров..."
sudo docker compose -f infra/docker-compose.yml ps

echo "🎉 Исправление настроек MinIO завершено!"
echo ""
echo "🔗 Доступ к файлам через:"
echo "   MinIO API: http://89.169.174.76:9000"
echo "   MinIO Console: http://89.169.174.76:9001"
echo "   Логин: minio_access_key"
echo "   Пароль: minio_secret_key_123"
echo ""
echo "🧪 Тестирование:"
echo "   1. Откройте сайт: https://foodgram.freedynamicdns.net"
echo "   2. Перейдите к любому рецепту"
echo "   3. Картинки должны отображаться корректно" 