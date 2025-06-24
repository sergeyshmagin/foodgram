#!/bin/bash

# Скрипт для настройки MinIO и создания bucket

set -e

DOMAIN="foodgram.freedynamicdns.net"
BACKEND_URL="https://${DOMAIN}"
FRONTEND_URL="https://${DOMAIN}"

echo "🔧 Настройка MinIO для проекта Foodgram..."

cd /home/yc-user/foodgram

echo "📦 Проверяем статус контейнеров..."
sudo docker compose -f infra/docker-compose.yml ps

echo "🔗 Настраиваем MinIO client alias..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc alias set minio http://localhost:9000 minio_access_key minio_secret_key_123 || true

echo "📁 Создаем bucket foodgram если не существует..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc mb minio/foodgram --ignore-existing

echo "🔓 Устанавливаем публичную политику для bucket..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc anonymous set public minio/foodgram

echo "🌐 Настраиваем CORS политику..."
cat > /tmp/cors.json << EOF
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
EOF

sudo docker compose -f infra/docker-compose.yml exec -T minio mc cors set /tmp/cors.json minio/foodgram || true

echo "📋 Проверяем созданные buckets..."
sudo docker compose -f infra/docker-compose.yml exec -T minio mc ls minio/

echo "✅ MinIO настроен успешно!"
echo "📄 Веб-интерфейс MinIO: http://89.169.174.76:9001"
echo "🔑 Логин: minio_access_key"
echo "🔐 Пароль: minio_secret_key_123"

echo "🔧 Обновляем настройки Django для правильного URL..."
sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
import os
from django.conf import settings
print('🔍 Текущие настройки MinIO:')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}')
print(f'AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}')
print('📁 Тестируем подключение к MinIO...')
from django.core.files.storage import default_storage
try:
    default_storage.bucket_name
    print('✅ Подключение к MinIO работает!')
except Exception as e:
    print(f'❌ Ошибка подключения к MinIO: {e}')
"

echo "🚀 Рестартуем backend для применения изменений..."
sudo docker compose -f infra/docker-compose.yml restart backend

echo "🎉 Настройка MinIO завершена!" 