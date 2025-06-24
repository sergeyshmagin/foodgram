#!/bin/bash

# 💾 Резервное копирование Foodgram
# Использование: ./backup.sh

set -e

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="foodgram_backup_$DATE"

echo "💾 === РЕЗЕРВНОЕ КОПИРОВАНИЕ FOODGRAM ==="
echo "Время начала: $(date)"

# Создаем директорию для бэкапов
mkdir -p $BACKUP_DIR/$BACKUP_NAME

echo "📁 Создана директория: $BACKUP_DIR/$BACKUP_NAME"

# 1. Бэкап базы данных PostgreSQL
echo "🗃️ Создание бэкапа базы данных..."
docker exec foodgram-postgres pg_dump -U foodgram_user foodgram > $BACKUP_DIR/$BACKUP_NAME/database.sql
echo "✅ Бэкап базы данных сохранен: database.sql"

# 2. Бэкап данных MinIO (изображения рецептов)
echo "📷 Создание бэкапа изображений..."
docker exec foodgram-minio mc mirror /data/foodgram /tmp/backup/ >/dev/null 2>&1 || echo "⚠️ Не удалось создать зеркало MinIO"
docker cp foodgram-minio:/tmp/backup $BACKUP_DIR/$BACKUP_NAME/minio_data 2>/dev/null || echo "⚠️ Копирование файлов MinIO пропущено"
echo "✅ Бэкап изображений завершен"

# 3. Бэкап конфигурационных файлов
echo "⚙️ Создание бэкапа конфигурации..."
cp -r infra/ $BACKUP_DIR/$BACKUP_NAME/infra/
cp docker-compose.yml $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || echo "docker-compose.yml не найден в корне"
echo "✅ Конфигурационные файлы сохранены"

# 4. Создание архива
echo "📦 Создание архива..."
cd $BACKUP_DIR
tar -czf ${BACKUP_NAME}.tar.gz $BACKUP_NAME/
cd ..

# 5. Расчет размера и проверка
BACKUP_SIZE=$(du -h $BACKUP_DIR/${BACKUP_NAME}.tar.gz | cut -f1)
echo "📊 Размер бэкапа: $BACKUP_SIZE"

# 6. Удаление временной директории
rm -rf $BACKUP_DIR/$BACKUP_NAME

# 7. Очистка старых бэкапов (оставляем последние 7)
echo "🧹 Очистка старых бэкапов..."
cd $BACKUP_DIR
ls -t foodgram_backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || echo "Старых бэкапов для удаления нет"
cd ..

REMAINING_BACKUPS=$(ls $BACKUP_DIR/foodgram_backup_*.tar.gz 2>/dev/null | wc -l)
echo "📋 Оставлено бэкапов: $REMAINING_BACKUPS"

echo ""
echo "✅ === БЭКАП ЗАВЕРШЕН ==="
echo "📁 Файл бэкапа: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"
echo "📊 Размер: $BACKUP_SIZE"
echo "⏰ Время завершения: $(date)"

echo ""
echo "📝 Для восстановления используйте:"
echo "   ./restore.sh $BACKUP_DIR/${BACKUP_NAME}.tar.gz" 