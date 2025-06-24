#!/bin/bash

# 🧪 Скрипт для тестирования загрузки ингредиентов
# Использование: bash scripts/deploy/test_ingredients_loading.sh

set -e

echo "🧪 Тестирование загрузки ингредиентов..."

# Проверяем состояние контейнера
if ! docker ps | grep -q "foodgram-backend"; then
    echo "❌ Backend контейнер не запущен!"
    exit 1
fi

echo "✅ Backend контейнер запущен"

# Проверяем доступность файла в контейнере
echo "📁 Проверяем наличие файла ингредиентов в контейнере..."
if docker exec foodgram-backend ls -la /app/data/ingredients.csv 2>/dev/null; then
    echo "✅ Файл ингредиентов найден в контейнере"
else
    echo "❌ Файл ингредиентов НЕ найден в контейнере!"
    echo "📋 Содержимое /app/data/:"
    docker exec foodgram-backend ls -la /app/data/ || echo "Директория /app/data/ не существует"
    exit 1
fi

# Считаем количество ингредиентов в файле
INGREDIENTS_IN_FILE=$(docker exec foodgram-backend wc -l < /app/data/ingredients.csv)
echo "📊 Ингредиентов в файле: $INGREDIENTS_IN_FILE"

# Считаем количество ингредиентов в базе
INGREDIENTS_IN_DB=$(docker exec foodgram-backend python manage.py shell -c "from apps.recipes.models import Ingredient; print(Ingredient.objects.count())")
echo "📊 Ингредиентов в базе: $INGREDIENTS_IN_DB"

# Пробуем загрузить ингредиенты
echo "🔄 Попытка загрузки ингредиентов..."
if docker exec foodgram-backend python manage.py load_ingredients; then
    echo "✅ Загрузка ингредиентов успешна!"
    
    # Проверяем количество после загрузки
    NEW_INGREDIENTS_IN_DB=$(docker exec foodgram-backend python manage.py shell -c "from apps.recipes.models import Ingredient; print(Ingredient.objects.count())")
    echo "📊 Ингредиентов в базе после загрузки: $NEW_INGREDIENTS_IN_DB"
    
    LOADED=$(($NEW_INGREDIENTS_IN_DB - $INGREDIENTS_IN_DB))
    echo "✅ Загружено новых ингредиентов: $LOADED"
else
    echo "❌ Ошибка при загрузке ингредиентов!"
    exit 1
fi

echo "🎉 Тест завершен успешно!" 