#!/bin/bash

echo "=== ОЧИСТКА DOCKER КОНТЕЙНЕРОВ ==="

# Останавливаем все запущенные контейнеры
echo "Останавливаем все контейнеры..."
sudo docker stop $(sudo docker ps -q) 2>/dev/null || echo "Нет запущенных контейнеров"

# Удаляем все контейнеры
echo "Удаляем все контейнеры..."
sudo docker rm $(sudo docker ps -aq) 2>/dev/null || echo "Нет контейнеров для удаления"

# Удаляем неиспользуемые образы
echo "Удаляем неиспользуемые образы..."
sudo docker image prune -f

# Удаляем неиспользуемые сети
echo "Удаляем неиспользуемые сети..."
sudo docker network prune -f

# Показываем текущее состояние
echo "Текущие контейнеры:"
sudo docker ps -a

echo "Текущие образы:"
sudo docker images

echo "=== ОЧИСТКА ЗАВЕРШЕНА ===" 