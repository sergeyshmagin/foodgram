#!/bin/bash

# 🩺 Проверка состояния Foodgram в продакшене
# Использование: ./health_check.sh

echo "🩺 === ПРОВЕРКА СОСТОЯНИЯ FOODGRAM ==="
echo "Время проверки: $(date)"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для проверки с цветным выводом
check_status() {
    local service=$1
    local command=$2
    local expected=$3
    
    echo -n "Проверка $service: "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Счетчики
total_checks=0
passed_checks=0

# 1. Проверка Docker контейнеров
echo "📦 КОНТЕЙНЕРЫ:"
containers=("foodgram-backend" "foodgram-frontend" "foodgram-nginx" "foodgram-postgres" "foodgram-redis" "foodgram-minio")

for container in "${containers[@]}"; do
    total_checks=$((total_checks + 1))
    if check_status "$container" "docker ps | grep $container | grep -q Up"; then
        passed_checks=$((passed_checks + 1))
    fi
done

# 2. Проверка портов
echo ""
echo "🌐 СЕТЕВЫЕ СЕРВИСЫ:"
ports=("80:HTTP" "9000:MinIO" "6379:Redis" "5432:PostgreSQL")

for port_service in "${ports[@]}"; do
    port=$(echo $port_service | cut -d: -f1)
    service=$(echo $port_service | cut -d: -f2)
    total_checks=$((total_checks + 1))
    if check_status "$service (порт $port)" "netstat -tlnp | grep -q :$port"; then
        passed_checks=$((passed_checks + 1))
    fi
done

# 3. Проверка HTTP endpoints
echo ""
echo "🔗 HTTP ENDPOINTS:"
endpoints=(
    "http://localhost/:Главная страница"
    "http://localhost/api/:API Root"
    "http://localhost/admin/:Админ-панель"
)

for endpoint_desc in "${endpoints[@]}"; do
    endpoint=$(echo $endpoint_desc | cut -d: -f1)
    desc=$(echo $endpoint_desc | cut -d: -f2)
    total_checks=$((total_checks + 1))
    if check_status "$desc" "curl -f -s $endpoint"; then
        passed_checks=$((passed_checks + 1))
    fi
done

# 4. Проверка базы данных
echo ""
echo "🗃️ БАЗА ДАННЫХ:"
total_checks=$((total_checks + 1))
if check_status "PostgreSQL соединение" "docker exec foodgram-backend python manage.py check --database default"; then
    passed_checks=$((passed_checks + 1))
fi

# 5. Проверка файлового хранилища
echo ""
echo "📁 ФАЙЛОВОЕ ХРАНИЛИЩЕ:"
total_checks=$((total_checks + 1))
if check_status "MinIO доступность" "curl -f -s http://localhost:9000/minio/health/live"; then
    passed_checks=$((passed_checks + 1))
fi

# 6. Проверка кеша
echo ""
echo "⚡ КЕШ:"
total_checks=$((total_checks + 1))
if check_status "Redis доступность" "docker exec foodgram-redis redis-cli ping | grep -q PONG"; then
    passed_checks=$((passed_checks + 1))
fi

# 7. Дополнительная диагностика
echo ""
echo "📊 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ:"

echo "Использование дискового пространства:"
df -h | grep -E "Filesystem|/dev/"

echo ""
echo "Использование памяти:"
free -h

echo ""
echo "Логи последних ошибок (последние 10 строк):"
docker compose -f infra/docker-compose.yml logs --tail=10 2>/dev/null | grep -i error || echo "Ошибок не найдено"

# Итоговый результат
echo ""
echo "📋 === ИТОГИ ПРОВЕРКИ ==="
echo "Общее количество проверок: $total_checks"
echo "Успешных проверок: $passed_checks"
echo "Неудачных проверок: $((total_checks - passed_checks))"

success_rate=$((passed_checks * 100 / total_checks))

if [ $success_rate -eq 100 ]; then
    echo -e "${GREEN}🎉 Система работает отлично! ($success_rate%)${NC}"
elif [ $success_rate -ge 80 ]; then
    echo -e "${YELLOW}⚠️ Система работает с небольшими проблемами ($success_rate%)${NC}"
else
    echo -e "${RED}🚨 Система работает с серьезными проблемами ($success_rate%)${NC}"
    echo "Рекомендуется проверить логи и перезапустить сервисы"
fi

echo "Время завершения: $(date)" 