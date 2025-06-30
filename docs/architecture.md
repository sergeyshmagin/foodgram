# 🏗️ Архитектура проекта Foodgram

## 📋 Обзор

Foodgram - это современное веб-приложение, построенное по микросервисной архитектуре с использованием контейнеризации Docker. Проект разделен на несколько независимых сервисов, что обеспечивает масштабируемость, надежность и простоту обслуживания.

## 🎯 Архитектурные принципы

### 1. Разделение ответственности
- **Frontend**: Пользовательский интерфейс (React)
- **Backend**: API и бизнес-логика (Django REST Framework)
- **Database**: Хранение данных (PostgreSQL)
- **Cache**: Кеширование и очереди (Redis)
- **Storage**: Файловое хранилище (MinIO)
- **Proxy**: Маршрутизация и балансировка (Nginx)

### 2. Контейнеризация
Каждый сервис работает в изолированном Docker контейнере с четко определенными интерфейсами взаимодействия.

### 3. Stateless API
RESTful API без сохранения состояния между запросами, что обеспечивает горизонтальную масштабируемость.

## 🔧 Компоненты системы

### Frontend (React)
```
frontend/
├── src/
│   ├── components/     # Переиспользуемые компоненты
│   ├── pages/         # Страницы приложения
│   ├── contexts/      # React контексты (состояние)
│   ├── utils/         # Утилиты и хелперы
│   └── api/           # HTTP клиент для API
├── public/            # Статические файлы
└── nginx.conf         # Конфигурация Nginx для фронтенда
```

**Технологии:**
- React 18 + Hooks
- React Router для маршрутизации
- Axios для HTTP запросов
- CSS Modules для стилизации

### Backend (Django)
```
backend/
├── apps/
│   ├── api/           # REST API endpoints
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   └── permissions.py
│   ├── recipes/       # Модель рецептов
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── management/commands/
│   └── users/         # Пользователи и авторизация
│       ├── models.py
│       └── admin.py
├── foodgram/
│   ├── settings/      # Настройки по окружениям
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── storage.py     # MinIO интеграция
└── tests/             # Unit тесты
```

**Технологии:**
- Django 4.2 + Django REST Framework
- JWT Authentication (djoser)
- PostgreSQL с ORM Django
- Redis для кеширования
- MinIO для файлов
- Pytest для тестирования

### База данных (PostgreSQL)

#### Основные модели:

**User (Пользователи)**
```sql
- id (PK)
- email (unique)
- username (unique)
- first_name
- last_name
- password_hash
- created_at
```

**Recipe (Рецепты)**
```sql
- id (PK)
- author_id (FK → User)
- name
- text (описание)
- image (ссылка на MinIO)
- cooking_time
- pub_date
- short_link (уникальная короткая ссылка)
```

**Ingredient (Ингредиенты)**
```sql
- id (PK)
- name
- measurement_unit
```

**Tag (Теги)**
```sql
- id (PK)
- name
- color (HEX)
- slug (unique)
```

**Связывающие модели:**
- `RecipeIngredient` - связь рецептов и ингредиентов с количеством
- `RecipeTag` - связь рецептов и тегов
- `Favorite` - избранные рецепты пользователей
- `ShoppingCart` - корзина покупок
- `Subscription` - подписки между пользователями

### Кеширование (Redis)

**Использование Redis:**
```python
# Кеширование результатов API
CACHE_TTL = 300  # 5 минут

# Кеш для часто запрашиваемых данных
- Список ингредиентов
- Теги рецептов
- Популярные рецепты
- Профили пользователей

# Очереди задач (если используется Celery)
- Отправка email уведомлений
- Генерация PDF списков покупок
- Оптимизация изображений
```

### Файловое хранилище (MinIO)

**Структура хранилища:**
```
foodgram-bucket/
├── recipes/           # Изображения рецептов
│   ├── 2024/01/       # Организация по датам
│   └── ...
├── avatars/           # Аватары пользователей
└── temp/              # Временные файлы
```

**Конфигурация:**
```python
# S3-совместимый интерфейс
AWS_ACCESS_KEY_ID = "minio"
AWS_SECRET_ACCESS_KEY = settings.MINIO_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = "foodgram"
AWS_S3_ENDPOINT_URL = "http://minio:9000"
```

## 🌐 Сетевая архитектура

### Nginx как Reverse Proxy
```nginx
server {
    # Статические файлы фронтенда
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API запросы к бэкенду
    location /api/ {
        proxy_pass http://backend:8000;
    }
    
    # Админ-панель
    location /admin/ {
        proxy_pass http://backend:8000;
    }
    
    # Медиа файлы через MinIO
    location /media/ {
        proxy_pass http://minio:9000/foodgram/;
    }
}
```

### Docker Compose Network
```yaml
networks:
  foodgram-network:
    driver: bridge

services:
  # Все сервисы подключены к общей сети
  # Внутренняя связь по именам контейнеров
```

## 🔄 Потоки данных

### 1. Аутентификация пользователя
```
Frontend → POST /api/auth/token/login/
Backend → Проверка credentials
Database → Поиск пользователя
Backend → Генерация JWT токена
Frontend ← Токен + данные пользователя
```

### 2. Создание рецепта
```
Frontend → POST /api/recipes/ (+ файл изображения)
Backend → Валидация данных
MinIO ← Загрузка изображения
Database ← Сохранение метаданных рецепта
Redis ← Очистка кеша рецептов
Frontend ← Созданный рецепт
```

### 3. Получение списка рецептов
```
Frontend → GET /api/recipes/?page=1&tags=breakfast
Backend → Проверка кеша Redis
Redis → Кешированные данные (если есть)
Database → SQL запрос (если кеша нет)
Backend → Формирование ответа
Redis ← Кеширование результата
Frontend ← Список рецептов
```

## 🚀 Развертывание

### Локальная разработка
```bash
# Запуск всех сервисов
docker-compose -f infra/docker-compose.yml up -d

# Применение миграций
docker exec foodgram-backend python manage.py migrate

# Загрузка начальных данных
docker exec foodgram-backend python manage.py load_ingredients
```

### Продакшн развертывание
```bash
# Автоматическое через GitHub Actions
git push origin main

# Или ручное
docker-compose -f infra/docker-compose.yml up -d --build
```

## 📊 Мониторинг и логирование

### Логи приложений
```bash
# Backend логи
docker logs foodgram-backend

# Frontend логи (Nginx)
docker logs foodgram-frontend

# База данных
docker logs foodgram-postgres

# Файловое хранилище
docker logs foodgram-minio
```

### Метрики производительности
- **Response Time**: < 200ms для API
- **Throughput**: 1000+ requests/minute
- **Availability**: 99.9% uptime
- **Database**: < 50ms query time

## 🔒 Безопасность

### Аутентификация и авторизация
```python
# JWT токены с временем жизни
ACCESS_TOKEN_LIFETIME = timedelta(days=1)

# Permissions на уровне API
- IsAuthenticated: только для авторизованных
- IsOwnerOrReadOnly: владелец может редактировать
- ReadOnly: только чтение для анонимных
```

### Защита от атак
```python
# CORS настройки
CORS_ALLOWED_ORIGINS = [
    "https://foodgram.freedynamicdns.net",
]

# CSRF защита
CSRF_TRUSTED_ORIGINS = [
    "https://foodgram.freedynamicdns.net",
]

# Rate limiting (через Nginx или Django)
limit_req zone=api burst=10 nodelay;
```

### Валидация данных
```python
# Серализаторы DRF с строгой валидацией
class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    def validate(self, data):
        # Проверка обязательных полей
        # Валидация данных
        # Проверка разрешений
```

## 📈 Масштабирование

### Горизонтальное масштабирование
1. **Backend**: Несколько инстансов Django за load balancer
2. **Database**: Read replicas для читающих запросов
3. **Redis**: Redis Cluster для больших объемов кеша
4. **MinIO**: Distributed MinIO для файлового хранилища

### Вертикальное масштабирование
1. **CPU**: Увеличение вычислительных ресурсов
2. **RAM**: Больше памяти для кеширования
3. **Storage**: SSD диски для быстрого доступа к данным

## 🔧 Конфигурация окружений

### Development
```python
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
DATABASE_URL = "postgresql://localhost/foodgram_dev"
REDIS_URL = "redis://localhost:6379/0"
```

### Production
```python
DEBUG = False
ALLOWED_HOSTS = ["foodgram.freedynamicdns.net"]
DATABASE_URL = "postgresql://postgres:5432/foodgram"
REDIS_URL = "redis://redis:6379/0"
SECURE_SSL_REDIRECT = True
```

## 📚 API Спецификация

### RESTful принципы
- **GET**: Получение данных
- **POST**: Создание новых ресурсов
- **PUT/PATCH**: Обновление существующих
- **DELETE**: Удаление ресурсов

### Стандартные коды ответов
- **200**: Успешный запрос
- **201**: Ресурс создан
- **400**: Ошибка валидации
- **401**: Не авторизован
- **403**: Доступ запрещен
- **404**: Ресурс не найден
- **500**: Внутренняя ошибка сервера

### Пагинация
```json
{
  "count": 123,
  "next": "http://api.example.org/accounts/?page=4",
  "previous": "http://api.example.org/accounts/?page=2",
  "results": [...]
}
```

## 🧪 Тестирование

### Уровни тестирования
1. **Unit Tests**: Отдельные функции и методы
2. **Integration Tests**: Взаимодействие компонентов
3. **API Tests**: Тестирование HTTP endpoints
4. **E2E Tests**: Полные пользовательские сценарии

### Покрытие тестами
- **Models**: 100% покрытие
- **Serializers**: 95% покрытие
- **Views**: 90% покрытие
- **Utils**: 100% покрытие

---