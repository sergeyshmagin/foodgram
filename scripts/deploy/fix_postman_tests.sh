#!/bin/bash

# Скрипт для исправления проблем с Postman тестами

set -e  # Выходим при любой ошибке

echo "🚀 Исправление проблем с Postman тестами..."

# Определяем директории
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "📁 Директория проекта: $PROJECT_ROOT"
echo "📁 Директория backend: $BACKEND_DIR"

# Переходим в директорию backend
cd "$BACKEND_DIR" || {
    echo "❌ Не удалось перейти в директорию backend"
    exit 1
}

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "Создайте виртуальное окружение: python -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
elif [ -f "venv/bin/activate" ]; then
    # Linux/Mac
    source venv/bin/activate
else
    echo "❌ Не удалось найти скрипт активации виртуального окружения"
    exit 1
fi

echo "✅ Виртуальное окружение активировано"

# Проверяем Django проект
echo "🔍 Проверяем Django проект..."
python manage.py check

# Запускаем миграции
echo "🔄 Применяем миграции..."
python manage.py migrate

# Запускаем скрипт исправления
echo "🔧 Запускаем исправления..."
python "$SCRIPT_DIR/fix_postman_issues.py"

echo ""
echo "✅ Все исправления применены!"
echo "🎯 Теперь можно запускать Postman тесты"
echo ""
echo "📋 Основные исправления:"
echo "   1. ✅ Метод set_password теперь возвращает статус 204"
echo "   2. ✅ Профили пользователей доступны без авторизации"  
echo "   3. ✅ Пагинация поддерживает параметр 'limit'"
echo "   4. ✅ Очищены пользователи с пустыми полями"
echo "   5. ✅ Удалены дублирующиеся пользователи"
echo ""
echo "🚀 Готово к тестированию!" 