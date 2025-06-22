# 🐳 Docker & Deployment Guide

## 📋 Обзор архитектуры

Проект Foodgram состоит из следующих сервисов:

- **PostgreSQL** - Основная база данных
- **Redis** - Кеширование и очереди
- **MinIO** - S3-совместимое хранилище файлов
- **Django Backend** - REST API сервер
- **React Frontend** - Веб-интерфейс
- **Nginx** - Реверс-прокси и статические файлы

## 🚀 Быстрый старт

### Development окружение

1. **Запуск инфраструктуры:**
```bash
# Запуск PostgreSQL, Redis, MinIO
docker-compose -f docker-compose.dev.yml up -d
```

2. **Настройка backend:**
```bash
cd backend
source venv/bin/activate  # Активация виртуального окружения
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

3. **Запуск frontend:**
```bash
cd frontend
npm install
npm start
```

### Автоматический запуск dev окружения

```bash
chmod +x scripts/dev/start_dev.sh
./scripts/dev/start_dev.sh
```

## 🏭 Production деплой

### 1. Подготовка конфигурации

```bash
# Копируем пример переменных окружения
cp infra/production.env.example infra/.env

# Редактируем конфигурацию под ваше окружение
nano infra/.env
```

### 2. Основные переменные для production

```env
# Безопасность
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False

# База данных
POSTGRES_PASSWORD=secure_database_password

# MinIO
MINIO_SECRET_KEY=secure_minio_password

# Домен
ALLOWED_HOSTS=your-domain.com,192.168.0.10
```

### 3. Деплой через Docker Registry

```bash
# Автоматический деплой (рекомендуется)
chmod +x scripts/deploy/deploy.sh
./scripts/deploy/deploy.sh

# Или ручной деплой
cd infra
docker-compose up --build -d
```

## 🔧 Docker сервисы

### PostgreSQL
- **Порт:** 5432 (dev), internal (prod)
- **База:** foodgram_dev / foodgram
- **Пользователь:** foodgram_user
- **Данные:** Persistent volume `pg_data`

### Redis
- **Порт:** 6379 (dev), internal (prod)
- **Конфигурация:** AOF persistence включен
- **Данные:** Persistent volume `redis_data`

### MinIO
- **API порт:** 9000
- **Console порт:** 9001
- **Пользователь:** foodgram_minio (по умолчанию)
- **Bucket:** foodgram
- **Данные:** Persistent volume `minio_data`

### Backend (Django)
- **Порт:** 8000
- **Health check:** `/api/health/`
- **Settings:** production или development
- **Volumes:** static, media, logs

### Frontend (React)
- **Build:** Multi-stage Docker build
- **Nginx:** Статические файлы отдаются через nginx
- **Proxy:** API проксируется на backend

### Nginx
- **HTTP порт:** 80
- **HTTPS порт:** 443 (опционально)
- **Конфигурация:** Кеширование, gzip, безопасность

## 🌐 Network архитектура

### Development
```
localhost:3000  -> React Frontend
localhost:8000  -> Django Backend
localhost:5432  -> PostgreSQL
localhost:6379  -> Redis
localhost:9000  -> MinIO API
localhost:9001  -> MinIO Console
```

### Production
```
:80/:443        -> Nginx
  /api/         -> Django Backend :8000
  /admin/       -> Django Backend :8000
  /static/      -> Nginx static files
  /media/       -> MinIO или Nginx fallback
  /             -> React Frontend
```

## 🔐 Безопасность

### Environment Variables
- Все секреты через переменные окружения
- `.env` файлы в `.gitignore`
- Разные конфигурации для dev/prod

### Docker Security
- Non-root пользователи в контейнерах
- Read-only volumes где возможно
- Health checks для всех сервисов
- Network изоляция

### Nginx Security Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

## 📊 Мониторинг и логи

### Health Checks
- **Backend:** `GET /api/health/`
- **Database:** `pg_isready`
- **Redis:** `redis-cli ping`
- **MinIO:** `GET /minio/health/live`
- **Nginx:** `curl localhost/health`

### Логи
```bash
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f nginx

# Логи Django в контейнере
docker exec -it foodgram-backend tail -f /app/logs/django.log
```

### Мониторинг ресурсов
```bash
# Статистика контейнеров
docker stats

# Использование volumes
docker system df

# Состояние сервисов
docker-compose ps
```

## 🚀 CI/CD Pipeline

### Workflow
1. **Build** - Сборка Docker images
2. **Test** - Запуск pytest тестов
3. **Push** - Отправка в Docker Registry (192.168.0.4)
4. **Deploy** - Деплой на production сервер (192.168.0.10)

### Скрипты деплоя
- `scripts/deploy/deploy.sh` - Полный production деплой
- `scripts/dev/start_dev.sh` - Development окружение

## 🔄 Backup и восстановление

### База данных
```bash
# Создание backup
docker exec foodgram-db pg_dump -U foodgram_user foodgram > backup.sql

# Восстановление
docker exec -i foodgram-db psql -U foodgram_user foodgram < backup.sql
```

### MinIO данные
```bash
# Backup MinIO bucket
docker exec foodgram-minio mc cp --recursive /data/foodgram /backup/

# Restore MinIO bucket
docker exec foodgram-minio mc cp --recursive /backup/foodgram /data/
```

### Redis данные
```bash
# Redis автоматически создает RDB snapshots
# Данные сохраняются в volume redis_data
```

## ⚠️ Troubleshooting

### Частые проблемы

1. **База данных недоступна:**
```bash
# Проверка состояния
docker exec foodgram-db pg_isready -U foodgram_user

# Перезапуск службы
docker-compose restart db
```

2. **MinIO недоступен:**
```bash
# Проверка health
curl -f http://localhost:9000/minio/health/live

# Создание bucket вручную
docker exec foodgram-backend python manage.py setup_minio
```

3. **Проблемы с правами файлов:**
```bash
# Исправление прав в контейнере
docker exec -u root foodgram-backend chown -R app:app /app
```

4. **Nginx не запускается:**
```bash
# Проверка конфигурации
docker exec foodgram-nginx nginx -t

# Перезагрузка конфигурации
docker exec foodgram-nginx nginx -s reload
```

### Логи отладки
```bash
# Детальные логи Django
docker exec foodgram-backend python manage.py check --deploy

# Статус всех сервисов
docker-compose ps

# Использование ресурсов
docker stats --no-stream
```

## 📝 Полезные команды

### Docker Compose
```bash
# Запуск в фоне
docker-compose up -d

# Остановка
docker-compose down

# Пересборка и запуск
docker-compose up --build

# Просмотр логов
docker-compose logs -f [service_name]

# Выполнение команд в контейнере
docker-compose exec backend python manage.py shell
```

### Управление данными
```bash
# Очистка неиспользуемых образов
docker image prune -a

# Очистка volumes (ОСТОРОЖНО!)
docker volume prune

# Полная очистка системы
docker system prune -a --volumes
```

## 🔗 Полезные ссылки

- [Docker Compose documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [Redis Docker Hub](https://hub.docker.com/_/redis)
- [MinIO Docker Hub](https://hub.docker.com/r/minio/minio)
- [Nginx Docker Hub](https://hub.docker.com/_/nginx) 