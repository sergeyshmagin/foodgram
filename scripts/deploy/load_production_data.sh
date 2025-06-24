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
if ! sudo docker compose -f infra/docker-compose.yml ps | grep -q "foodgram-backend.*Up"; then
    echo "❌ Ошибка: backend контейнер не запущен!"
    echo "   Запустите проект командой: sudo docker compose -f infra/docker-compose.yml up -d"
    exit 1
fi

echo "✅ Backend контейнер запущен"

# Функция для безопасного выполнения команд Django
run_django_command() {
    local cmd="$1"
    local description="$2"
    
    echo ""
    echo "🔄 $description..."
    
    if sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py $cmd; then
        echo "✅ $description завершено успешно"
        return 0
    else
        echo "❌ Ошибка при выполнении: $description"
        return 1
    fi
}

# Функция для проверки данных в базе
check_data_status() {
    echo ""
    echo "📊 Проверяем текущее состояние данных..."
    
    # Проверяем администраторов
    admin_count=$(sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(is_superuser=True).count())
" 2>/dev/null | tail -1)
    
    # Проверяем теги
    tags_count=$(sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
from apps.recipes.models import Tag
print(Tag.objects.count())
" 2>/dev/null | tail -1)
    
    # Проверяем ингредиенты
    ingredients_count=$(sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
from apps.recipes.models import Ingredient
print(Ingredient.objects.count())
" 2>/dev/null | tail -1)
    
    # Проверяем рецепты
    recipes_count=$(sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py shell -c "
from apps.recipes.models import Recipe
print(Recipe.objects.count())
" 2>/dev/null | tail -1)
    
    echo "📈 Текущее состояние базы данных:"
    echo "   👤 Администраторы: $admin_count"
    echo "   🏷️  Теги: $tags_count"
    echo "   🥕 Ингредиенты: $ingredients_count"
    echo "   📄 Рецепты: $recipes_count"
}

echo ""
echo "🔧 Начинаем загрузку данных..."

# Проверяем текущее состояние
check_data_status

if [ "$LOAD_TYPE" = "basic" ] || [ "$LOAD_TYPE" = "full" ]; then
    # Загружаем базовые данные (администратор и теги)
    if ! run_django_command "setup_production" "Загрузка базовых данных (администратор и теги)"; then
        echo "⚠️ Проблема с базовыми данными, но продолжаем..."
    fi
    
    # Загружаем ингредиенты
    if [ -f "data/ingredients.csv" ]; then
        if ! run_django_command "load_ingredients --file data/ingredients.csv" "Загрузка ингредиентов из CSV файла"; then
            echo "⚠️ Проблема с загрузкой ингредиентов, но продолжаем..."
        fi
    else
        echo "⚠️ Файл data/ingredients.csv не найден, пропускаем загрузку ингредиентов"
    fi
fi

if [ "$LOAD_TYPE" = "demo" ] || [ "$LOAD_TYPE" = "full" ]; then
    # Загружаем демо-данные
    if ! run_django_command "load_demo_data" "Загрузка демо-данных (рецепты)"; then
        echo "⚠️ Команда load_demo_data не найдена или не сработала, пропускаем"
    fi
fi

echo ""
echo "🔄 Создаём миграции при необходимости..."
if ! run_django_command "makemigrations --dry-run" "Проверка необходимости создания миграций"; then
    echo "ℹ️ Проверка миграций завершена"
fi

# Если есть изменения - создаём миграции
if sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py makemigrations --dry-run | grep -q "would create"; then
    echo "📝 Обнаружены изменения в моделях, создаём миграции..."
    if ! run_django_command "makemigrations" "Создание миграций"; then
        echo "⚠️ Проблема с созданием миграций"
    fi
fi

echo ""
echo "🔄 Применяем миграции для безопасности..."
if ! run_django_command "migrate" "Применение миграций"; then
    echo "⚠️ Проблема с миграциями"
fi

echo ""
echo "🧹 Собираем статические файлы..."
if ! run_django_command "collectstatic --noinput" "Сбор статических файлов"; then
    echo "⚠️ Проблема со сбором статических файлов"
fi

# Финальная проверка данных
check_data_status

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
echo ""
echo "🎯 Теперь можно запускать Postman коллекцию для тестирования API!" 