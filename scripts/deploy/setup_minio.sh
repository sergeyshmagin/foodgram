#!/bin/bash

# Скрипт для настройки MinIO после деплоя
# Создает bucket и настраивает публичную политику для изображений

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🔧 Настройка MinIO...${NC}"

# Проверяем что MinIO доступен
MINIO_ENDPOINT="localhost:9000"
BUCKET_NAME="foodgram"

echo -e "${YELLOW}⏳ Ожидание запуска MinIO...${NC}"
until curl -f http://$MINIO_ENDPOINT/minio/health/live > /dev/null 2>&1; do
    echo "⏳ MinIO еще не готов, ожидание..."
    sleep 5
done

echo -e "${GREEN}✅ MinIO запущен${NC}"

# Устанавливаем MinIO Client если не установлен
if ! command -v mc &> /dev/null; then
    echo -e "${YELLOW}📦 Установка MinIO Client...${NC}"
    curl https://dl.min.io/client/mc/release/linux-amd64/mc -o /usr/local/bin/mc
    chmod +x /usr/local/bin/mc
fi

# Настраиваем alias для MinIO
echo -e "${YELLOW}🔑 Настройка подключения к MinIO...${NC}"
mc alias set local http://$MINIO_ENDPOINT ${MINIO_ACCESS_KEY} ${MINIO_SECRET_KEY}

# Создаем bucket если не существует
echo -e "${YELLOW}📁 Создание bucket '$BUCKET_NAME'...${NC}"
if ! mc ls local/$BUCKET_NAME > /dev/null 2>&1; then
    mc mb local/$BUCKET_NAME
    echo -e "${GREEN}✅ Bucket '$BUCKET_NAME' создан${NC}"
else
    echo -e "${GREEN}✅ Bucket '$BUCKET_NAME' уже существует${NC}"
fi

# Создаем публичную политику для медиа файлов
echo -e "${YELLOW}🔒 Настройка публичной политики для медиа файлов...${NC}"
cat > /tmp/public-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": "*"},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::$BUCKET_NAME/media/*"]
    }
  ]
}
EOF

# Применяем политику
mc policy set-json /tmp/public-policy.json local/$BUCKET_NAME/media
echo -e "${GREEN}✅ Публичная политика настроена для /media/*${NC}"

# Настраиваем CORS для bucket
echo -e "${YELLOW}🌐 Настройка CORS для bucket...${NC}"
cat > /tmp/cors.json << EOF
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "HEAD"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3600
    }
  ]
}
EOF

mc cors set /tmp/cors.json local/$BUCKET_NAME
echo -e "${GREEN}✅ CORS настроен${NC}"

# Очистка временных файлов
rm -f /tmp/public-policy.json /tmp/cors.json

echo -e "${GREEN}🎉 Настройка MinIO завершена!${NC}"
echo -e "${YELLOW}📊 Статистика bucket:${NC}"
mc ls local/$BUCKET_NAME --recursive | head -10

echo -e "${YELLOW}🔗 Доступные endpoints:${NC}"
echo -e "  • MinIO API: http://$MINIO_ENDPOINT"
echo -e "  • MinIO Console: http://$MINIO_ENDPOINT/minio (доступ через nginx)"
echo -e "  • Media URL: https://foodgram.freedynamicdns.net/media/" 