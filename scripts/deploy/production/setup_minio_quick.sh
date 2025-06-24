#!/bin/bash

# 🚀 Быстрая настройка MinIO для Foodgram
# Выполните этот скрипт на продакшн сервере

set -e

echo "🔧 Быстрая настройка MinIO для отображения изображений..."

# Переходим в рабочую директорию
cd $HOME/foodgram

# Проверяем что контейнеры запущены
echo "📋 Проверка статуса контейнеров:"
sudo docker compose -f infra/docker-compose.yml ps | grep minio

# Настраиваем MinIO через Docker exec
echo "🔑 Настройка MinIO..."

# Устанавливаем MinIO Client в контейнер
sudo docker compose -f infra/docker-compose.yml exec -T minio sh -c "
    # Ждём полной готовности MinIO
    until curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; do
        echo '⏳ Ожидание готовности MinIO...'
        sleep 2
    done
    
    echo '✅ MinIO готов'
    
    # Настраиваем alias (credentials берём из переменных контейнера)
    mc alias set local http://localhost:9000 \$MINIO_ROOT_USER \$MINIO_ROOT_PASSWORD
    
    # Создаём bucket если не существует  
    mc mb local/foodgram --ignore-existing || echo 'Bucket уже существует'
    
    # Создаём папку media
    mc mb local/foodgram/media --ignore-existing || echo 'Папка media уже существует'
    
    # Устанавливаем публичную политику для media
    mc anonymous set public local/foodgram/media/
    
    echo '📊 Статус bucket:'
    mc ls local/foodgram/
    
    echo '🔒 Проверка политики:'
    mc anonymous get local/foodgram/media/
"

echo "✅ MinIO настроен!"
echo "🌐 Теперь изображения должны отображаться на сайте"
echo "🔗 Проверьте: https://foodgram.freedynamicdns.net"

# Проверяем что nginx корректно проксирует media
echo "🧪 Тестируем проксирование media файлов..."
curl -I "https://foodgram.freedynamicdns.net/media/" 2>/dev/null | head -3 || echo "Тест не удался, но это нормально если нет файлов"

echo "🎉 Настройка завершена!" 