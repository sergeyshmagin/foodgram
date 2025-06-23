#!/bin/bash

set -e

echo "🔧 БЫСТРОЕ ИСПРАВЛЕНИЕ NGINX"

# Переходим в директорию проекта
cd $HOME/foodgram

# Освобождаем порт 80
echo "Освобождаем порт 80..."
sudo systemctl stop nginx 2>/dev/null || echo "Системный nginx не запущен"
sudo fuser -k 80/tcp 2>/dev/null || echo "Порт 80 уже свободен"

sleep 3

# Перезапускаем nginx контейнер
echo "Перезапускаем nginx контейнер..."
sudo docker compose -f infra/docker-compose.yml restart nginx

sleep 5

# Проверяем результат
echo "Проверяем статус..."
sudo docker compose -f infra/docker-compose.yml ps

# Тестируем доступность
echo "Тестируем доступность сайта..."
curl -s -o /dev/null -w "%{http_code}" http://localhost/ || echo "Сайт недоступен"

echo "✅ Готово!" 