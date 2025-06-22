#!/bin/bash

echo "🚀 Запуск полной интеграции Foodgram..."

# Stop any running services
echo "1. Остановка существующих сервисов..."
docker-compose -f docker-compose.dev.yml down
cd infra && docker-compose down
cd ..

# Start infrastructure
echo "2. Запуск инфраструктуры (PostgreSQL, Redis, MinIO)..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "3. Ожидание готовности сервисов..."
sleep 10

# Start backend
echo "4. Запуск Backend..."
cd backend
source venv/Scripts/activate
pip install -r requirements/development.txt
python manage.py migrate --settings=foodgram.settings.development
python manage.py collectstatic --noinput --settings=foodgram.settings.development
python manage.py runserver --settings=foodgram.settings.development &
BACKEND_PID=$!
cd ..

# Start frontend
echo "5. Запуск Frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

# Start nginx with full stack
echo "6. Запуск полного стека через docker-compose..."
cd infra
docker-compose up -d
cd ..

echo "✅ Интеграция запущена!"
echo "📋 Доступные сервисы:"
echo "- Backend API: http://localhost:8000"
echo "- Frontend Dev: http://localhost:3000"
echo "- Full Stack: http://localhost (через nginx)"
echo "- MinIO Console: http://localhost:9001"
echo "- Admin: http://localhost:8000/admin/"

echo "🛑 Для остановки используйте Ctrl+C"

# Keep script running
wait $BACKEND_PID $FRONTEND_PID 