#!/bin/bash

# Check integration between frontend and backend
echo "🔍 Проверка интеграции Foodgram..."

# Check if Docker infrastructure is running
echo "1. Проверка Docker инфраструктуры..."
docker-compose -f docker-compose.dev.yml ps

# Check backend API
echo "2. Проверка Backend API..."
echo "Health check:"
curl -s http://localhost:8000/api/health/ || echo "❌ Backend недоступен"

echo "Tags endpoint:"
curl -s http://localhost:8000/api/tags/ | head -c 100

echo "Recipes endpoint:"
curl -s http://localhost:8000/api/recipes/ | head -c 100

# Check frontend
echo "3. Проверка Frontend..."
if curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend доступен на :3000"
else
    echo "❌ Frontend недоступен на :3000"
fi

# Check nginx proxy
echo "4. Проверка Nginx proxy..."
if curl -s http://localhost/api/health/ >/dev/null 2>&1; then
    echo "✅ Nginx проксирует API запросы"
else
    echo "❌ Nginx proxy недоступен"
fi

if curl -s http://localhost/ >/dev/null 2>&1; then
    echo "✅ Nginx отдает фронтенд"
else
    echo "❌ Nginx не отдает фронтенд"
fi

echo "🏁 Проверка завершена" 