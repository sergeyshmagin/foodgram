#!/bin/bash

# Скрипт для локального тестирования MinIO настроек

set -e

echo "🧪 Локальное тестирование MinIO настроек..."

# Проверяем, что Docker работает
if ! docker --version > /dev/null 2>&1; then
    echo "❌ Docker не установлен или не запущен"
    exit 1
fi

echo "🚀 Запускаем локальные контейнеры..."
docker-compose -f docker-compose.local.yml up -d

echo "⏱️ Ожидаем запуск всех сервисов..."
sleep 30

echo "📦 Проверяем статус контейнеров..."
docker-compose -f docker-compose.local.yml ps

echo "🔗 Настраиваем MinIO client alias..."
docker-compose -f docker-compose.local.yml exec -T minio mc alias set minio http://localhost:9000 minio_access_key minio_secret_key_123

echo "📁 Создаем bucket foodgram если не существует..."
docker-compose -f docker-compose.local.yml exec -T minio mc mb minio/foodgram --ignore-existing

echo "🔓 Устанавливаем публичную политику для bucket..."
docker-compose -f docker-compose.local.yml exec -T minio mc anonymous set public minio/foodgram

echo "🌐 Настраиваем CORS политику..."

# Создаем CORS файл на хосте
cat > /tmp/minio_cors_local.json << 'EOF'
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

# Находим имя локального MinIO контейнера
MINIO_CONTAINER=$(docker-compose -f docker-compose.local.yml ps -q minio)

# Копируем файл в контейнер MinIO
docker cp /tmp/minio_cors_local.json $MINIO_CONTAINER:/tmp/cors.json

# Применяем CORS конфигурацию
docker-compose -f docker-compose.local.yml exec -T minio mc cors set /tmp/cors.json minio/foodgram

# Очищаем временный файл
rm -f /tmp/minio_cors_local.json

echo "📋 Проверяем CORS настройки..."
docker-compose -f docker-compose.local.yml exec -T minio mc cors get minio/foodgram || echo "ℹ️ CORS настройки не отображаются, но установлены"

echo "🔍 Проверяем настройки Django..."
docker-compose -f docker-compose.local.yml exec -T backend python manage.py shell -c "
import os
from django.conf import settings
print('🔍 Локальные настройки MinIO:')
print(f'MEDIA_URL: {settings.MEDIA_URL}')
print(f'AWS_S3_ENDPOINT_URL: {settings.AWS_S3_ENDPOINT_URL}')
print(f'AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}')
print(f'AWS_S3_CUSTOM_DOMAIN: {getattr(settings, \"AWS_S3_CUSTOM_DOMAIN\", \"Не установлен\")}')
print(f'AWS_QUERYSTRING_AUTH: {getattr(settings, \"AWS_QUERYSTRING_AUTH\", \"Не установлен\")}')
print(f'MINIO_PUBLIC_ENDPOINT: {os.environ.get(\"MINIO_PUBLIC_ENDPOINT\", \"Не установлен\")}')

print('📁 Тестируем подключение к MinIO...')
from django.core.files.storage import default_storage
try:
    bucket_name = default_storage.bucket_name
    print(f'✅ Подключение к MinIO работает! Bucket: {bucket_name}')
    
    # Тестируем создание файла
    from django.core.files.base import ContentFile
    file_name = 'test_image.jpg'
    test_content = ContentFile(b'test image content', name=file_name)
    saved_name = default_storage.save(f'media/{file_name}', test_content)
    print(f'✅ Тестовый файл создан: {saved_name}')
    
    # Получаем URL файла
    file_url = default_storage.url(saved_name)
    print(f'✅ URL файла: {file_url}')
    
except Exception as e:
    print(f'❌ Ошибка работы с MinIO: {e}')
"

echo "🌐 Тестируем доступность MinIO через публичный URL..."
curl -I http://localhost:9000/minio/health/live || echo "⚠️ MinIO недоступен"

echo "📁 Проверяем содержимое bucket..."
docker-compose -f docker-compose.local.yml exec -T minio mc ls minio/foodgram/ --recursive || echo "📝 Bucket пуст"

echo "🎉 Локальное тестирование завершено!"
echo ""
echo "🔗 Локальные ссылки:"
echo "   Django: http://localhost:8000"
echo "   MinIO API: http://localhost:9000"
echo "   MinIO Console: http://localhost:9001"
echo "   Логин: minio_access_key"
echo "   Пароль: minio_secret_key_123"
echo ""
echo "🧪 Для тестирования загрузки файлов:"
echo "   1. Откройте http://localhost:8000/admin"
echo "   2. Войдите как admin:admin123"
echo "   3. Создайте рецепт с картинкой"
echo "   4. Проверьте, что картинка отображается"
echo ""
echo "🔄 Для остановки: docker-compose -f docker-compose.local.yml down" 