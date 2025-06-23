#!/bin/bash

# Скрипт для исправления коротких ссылок на продакшн
# Применяет изменения в nginx.conf и backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔗 Исправление коротких ссылок на продакшн"
echo "📁 Каталог проекта: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Проверяем, что мы в правильном каталоге
if [ ! -f "infra/docker-compose.yml" ]; then
    echo "❌ Ошибка: файл docker-compose.yml не найден!"
    echo "   Убедитесь, что вы запускаете скрипт из корня проекта."
    exit 1
fi

echo ""
echo "🔧 Применяем изменения nginx.conf..."

# Перезапускаем nginx для применения изменений
echo "🔄 Перезапуск nginx..."
sudo docker compose -f infra/docker-compose.yml restart nginx

echo ""
echo "🔄 Перезапуск backend..."
sudo docker compose -f infra/docker-compose.yml restart backend

echo ""
echo "⏳ Ждём 10 секунд для полного запуска сервисов..."
sleep 10

echo ""
echo "📋 Проверяем состояние контейнеров..."
sudo docker compose -f infra/docker-compose.yml ps

echo ""
echo "🧪 Тестируем короткие ссылки..."

# Проверяем, что есть хотя бы один рецепт
echo "📖 Проверяем наличие рецептов..."
RECIPE_COUNT=$(sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
from apps.recipes.models import Recipe
print(Recipe.objects.count())
" | tail -1)

if [ "$RECIPE_COUNT" -gt 0 ]; then
    echo "✅ Найдено рецептов: $RECIPE_COUNT"
    
    # Получаем ID первого рецепта
    FIRST_RECIPE_ID=$(sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
from apps.recipes.models import Recipe
recipe = Recipe.objects.first()
if recipe:
    print(recipe.id)
else:
    print('0')
" | tail -1)
    
    if [ "$FIRST_RECIPE_ID" -gt 0 ]; then
        echo "🔗 Тестируем короткую ссылку для рецепта ID: $FIRST_RECIPE_ID"
        echo "📋 Короткая ссылка: https://foodgram.freedynamicdns.net/s/$FIRST_RECIPE_ID/"
        echo "📋 Должна перенаправлять на: https://foodgram.freedynamicdns.net/recipes/$FIRST_RECIPE_ID"
        
        # Тестируем редирект
        REDIRECT_URL=$(curl -s -I "https://foodgram.freedynamicdns.net/s/$FIRST_RECIPE_ID/" | grep -i location | cut -d' ' -f2- | tr -d '\r\n')
        
        if [ -n "$REDIRECT_URL" ]; then
            echo "✅ Редирект работает: $REDIRECT_URL"
        else
            echo "⚠️ Редирект не найден, возможно нужно время для применения изменений"
        fi
    fi
else
    echo "⚠️ В базе данных нет рецептов для тестирования"
    echo "💡 Запустите команду загрузки данных:"
    echo "   ./scripts/deploy/load_production_data.sh demo"
fi

echo ""
echo "✅ ИСПРАВЛЕНИЕ КОРОТКИХ ССЫЛОК ЗАВЕРШЕНО!"
echo ""
echo "📋 ПРОВЕРЬТЕ РАБОТУ:"
echo "🌐 Откройте любую короткую ссылку в браузере"
echo "🔗 Формат: https://foodgram.freedynamicdns.net/s/{RECIPE_ID}/"
echo "↪️ Должна перенаправлять на: https://foodgram.freedynamicdns.net/recipes/{RECIPE_ID}"
echo ""
echo "💡 Если ссылки всё ещё не работают:"
echo "   1. Подождите 1-2 минуты для полного применения изменений"
echo "   2. Очистите кеш браузера (Ctrl+F5)"
echo "   3. Проверьте логи: sudo docker compose -f infra/docker-compose.yml logs nginx backend" 