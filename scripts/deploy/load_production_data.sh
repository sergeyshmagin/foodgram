#!/bin/bash

# Скрипт для загрузки данных в продакшн
# Использование: ./load_production_data.sh [basic|demo|full]

set -e

LOAD_TYPE=${1:-basic}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Загрузка данных в продакшн (тип: $LOAD_TYPE)"
echo "📁 Каталог проекта: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Проверяем, что мы в правильном каталоге
if [ ! -f "infra/docker-compose.yml" ]; then
    echo "❌ Ошибка: файл docker-compose.yml не найден!"
    echo "   Убедитесь, что вы запускаете скрипт из корня проекта."
    exit 1
fi

echo "📋 Проверяем состояние контейнеров..."
sudo docker compose -f infra/docker-compose.yml ps

echo ""
echo "🔧 Начинаем загрузку данных..."

if [ "$LOAD_TYPE" = "basic" ] || [ "$LOAD_TYPE" = "full" ]; then
    echo ""
    echo "📦 Загружаем базовые данные (администратор и теги)..."
    sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py setup_production
    
    echo ""
    echo "🥕 Загружаем ингредиенты из CSV файла..."
    sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py load_ingredients --file data/ingredients.csv
fi

if [ "$LOAD_TYPE" = "demo" ] || [ "$LOAD_TYPE" = "full" ]; then
    echo ""
    echo "🍽️ Загружаем демо-данные (рецепты)..."
    if sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py load_demo_data 2>/dev/null; then
        echo "✅ Демо-данные загружены"
    else
        echo "⚠️ Команда load_demo_data не найдена, пропускаем"
    fi
fi

echo ""
echo "✅ ЗАГРУЗКА ДАННЫХ ЗАВЕРШЕНА!"
echo ""
echo "📋 АККАУНТЫ ДЛЯ ВХОДА:"
echo "👤 Администратор: admin@foodgram.local / admin123"
echo ""
echo "🌐 Admin панель: https://foodgram.freedynamicdns.net/admin/"
echo "🌐 Сайт: https://foodgram.freedynamicdns.net/"
echo ""
echo "💡 Для проверки данных в админке:"
echo "   - Перейдите в админку по ссылке выше"
echo "   - Войдите под учетной записью администратора"
echo "   - Проверьте разделы 'Теги' и 'Ингредиенты'" 