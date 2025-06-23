#!/bin/bash

set -e

echo "=== ОСВОБОЖДЕНИЕ ПОРТА 80 ==="

# Проверяем что занимает порт 80
echo "Проверяем что использует порт 80..."
sudo netstat -tlnp | grep :80 || echo "Нет процессов на порту 80"
sudo lsof -i :80 || echo "Нет открытых файлов на порту 80"

# Проверяем запущенные nginx процессы
echo "Проверяем процессы nginx..."
ps aux | grep nginx || echo "Nginx процессы не найдены"

# Останавливаем системный nginx если он запущен
echo "Останавливаем системный nginx..."
sudo systemctl stop nginx 2>/dev/null || echo "Системный nginx не запущен"
sudo systemctl disable nginx 2>/dev/null || echo "Системный nginx уже отключен"

# Убиваем все процессы на порту 80
echo "Принудительно освобождаем порт 80..."
sudo fuser -k 80/tcp 2>/dev/null || echo "Нет процессов для завершения на порту 80"

# Ждём немного
sleep 5

# Проверяем что порт освободился
echo "Проверяем освобождение порта 80..."
if sudo netstat -tlnp | grep :80; then
    echo "❌ Порт 80 всё ещё занят!"
    sudo netstat -tlnp | grep :80
    exit 1
else
    echo "✅ Порт 80 освобождён!"
fi

# Переходим в директорию проекта
cd $HOME/foodgram

# Перезапускаем только nginx контейнер
echo "Перезапускаем nginx контейнер..."
sudo docker compose -f infra/docker-compose.yml up -d nginx

# Проверяем статус
echo "Проверяем статус контейнеров..."
sudo docker compose -f infra/docker-compose.yml ps

echo "=== ГОТОВО ==="
echo "🌐 Сайт должен быть доступен на: http://89.169.174.76" 