# 🐳 Foodgram Docker Infrastructure

## ✅ Ответ на вопросы:

**1. Docker и Docker Compose файлы подготовлены!**

**2. Да, мы используем MinIO и Redis:**
- **MinIO** - S3-совместимое хранилище для изображений рецептов и аватаров
- **Redis** - для кеширования и очередей
- **PostgreSQL** - основная база данных

## 🚀 Быстрый запуск

### Development (разработка)
```bash
# Автоматический запуск
chmod +x scripts/dev/start_dev.sh
./scripts/dev/start_dev.sh

# Или ручной запуск
docker-compose -f docker-compose.dev.yml up -d
cd backend && python manage.py runserver
cd frontend && npm start
```

### Production (продакшн)
```bash
# Настройка конфигурации
cp infra/production.env.example infra/.env
nano infra/.env  # Отредактировать переменные

# Деплой
chmod +x scripts/deploy/deploy.sh
./scripts/deploy/deploy.sh

# Или ручной запуск
cd infra && docker-compose up --build -d
```

## 🏗️ Архитектура сервисов

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │  Django API     │    │   PostgreSQL    │
│  (Frontend)     │◄───┤   (Backend)     │◄───┤   (Database)    │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Nginx      │    │      Redis      │    │      MinIO      │
│   (Proxy)       │    │    (Cache)      │    │  (File Storage) │
│   Port: 80      │    │   Port: 6379    │    │   Port: 9000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Структура файлов

```
├── docker-compose.dev.yml        # Development окружение
├── infra/
│   ├── docker-compose.yml        # Production окружение
│   ├── nginx.conf               # Nginx конфигурация
│   └── production.env.example   # Пример переменных окружения
├── backend/
│   └── Dockerfile              # Django контейнер
├── frontend/
│   └── Dockerfile              # React контейнер
├── scripts/
│   ├── deploy/deploy.sh        # Production деплой
│   └── dev/start_dev.sh        # Development запуск
└── docs/docker_guide.md        # Подробная документация
```

## 🌐 Доступные URL

### Development
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Admin:** http://localhost:8000/admin/
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379
- **MinIO API:** http://localhost:9000
- **MinIO Console:** http://localhost:9001

### Production
- **Application:** http://192.168.0.10
- **API:** http://192.168.0.10/api/
- **Admin:** http://192.168.0.10/admin/
- **MinIO Console:** http://192.168.0.10:9001

## 🔑 Учетные данные по умолчанию

### Development
- **Admin:** admin@foodgram.ru / admin123
- **MinIO:** foodgram_minio / foodgram_minio_password

### Production
- Настраиваются в файле `infra/.env`

## 📋 Основные команды

```bash
# Запуск инфраструктуры для разработки
docker-compose -f docker-compose.dev.yml up -d

# Остановка
docker-compose -f docker-compose.dev.yml down

# Production деплой
cd infra && docker-compose up --build -d

# Просмотр логов
docker-compose logs -f [service-name]

# Статус сервисов
docker-compose ps

# Выполнение команд в контейнере
docker-compose exec backend python manage.py shell
```

## 🔧 Настройка production

1. **Скопировать пример конфигурации:**
   ```bash
   cp infra/production.env.example infra/.env
   ```

2. **Отредактировать основные переменные:**
   ```env
   SECRET_KEY=your-secure-key
   DEBUG=False
   POSTGRES_PASSWORD=secure-password
   MINIO_SECRET_KEY=secure-minio-password
   ALLOWED_HOSTS=your-domain.com,192.168.0.10
   ```

3. **Запустить деплой:**
   ```bash
   ./scripts/deploy/deploy.sh
   ```

## 📚 Подробная документация

Смотрите [docs/docker_guide.md](docs/docker_guide.md) для:
- Детального описания каждого сервиса
- Настройки безопасности
- Мониторинга и логирования
- Backup и восстановления
- Troubleshooting

## 🆘 Помощь

При возникновении проблем:
1. Проверьте логи: `docker-compose logs -f`
2. Статус сервисов: `docker-compose ps`
3. Health checks: `curl http://localhost:8000/api/health/`
4. Изучите [docs/docker_guide.md](docs/docker_guide.md)

---

✅ **Docker инфраструктура готова к использованию!** 