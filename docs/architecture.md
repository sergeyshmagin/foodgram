# 🏗️ Архитектура проекта Foodgram

## 📋 Обзор проекта
Foodgram - веб-приложение для публикации рецептов, где пользователи могут:
- Публиковать собственные рецепты
- Просматривать рецепты других пользователей
- Добавлять рецепты в избранное и список покупок
- Подписываться на авторов
- Скачивать список покупок

## 🛠️ Технологический стек

### Backend
- **Framework**: Django 3.2.16 + Django REST Framework 3.12.4
- **Database**: PostgreSQL (через psycopg2-binary)
- **Authentication**: Djoser + JWT токены
- **Cache**: Redis (для кеширования и очередей)
- **Storage**: MinIO (для хранения файлов)
- **WSGI**: Gunicorn
- **Testing**: pytest + pytest-django

### Frontend
- **Framework**: React.js
- **Сборка**: Create React App

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (реверс-прокси + статические файлы)
- **CI/CD**: GitHub Actions
- **Registry**: Docker Registry на 192.168.0.4

## 🌐 Сетевая архитектура

### Продуктивная среда:
- **Продакшен**: 192.168.0.10
- **Docker Registry**: 192.168.0.4
- **Redis**: 192.168.0.3
- **MinIO + PostgreSQL**: 192.168.0.4

### Порты:
- **Frontend**: 3000 (dev), 80 (prod)
- **Backend API**: 8000 (dev), 8000 (prod)
- **PostgreSQL**: 5432
- **Redis**: 6379
- **MinIO**: 9000

## 📁 Структура приложений Django

### 1. `users` - Управление пользователями
- Кастомная модель User (расширение AbstractUser)
- Аутентификация через email
- Управление аватарами
- Смена пароля

### 2. `recipes` - Основная логика рецептов
- Модели: Recipe, Ingredient, Tag, IngredientInRecipe
- ViewSets для CRUD операций
- Фильтрация и пагинация
- Загрузка изображений

### 3. `favorites` - Избранные рецепты
- Модель Favorite
- API для добавления/удаления

### 4. `shopping` - Список покупок
- Модель ShoppingCart
- Генерация PDF со списком покупок

### 5. `subscriptions` - Подписки на авторов
- Модель Subscription
- API управления подписками

## 🔐 Система авторизации

### Роли пользователей:
1. **Гость** - просмотр рецептов, регистрация
2. **Пользователь** - все операции кроме админки
3. **Автор** - управление собственными рецептами
4. **Администратор** - полный доступ

### Permissions:
- `IsOwnerOrReadOnly` - для рецептов
- `IsAuthenticated` - для избранного/покупок/подписок
- `AllowAny` - для просмотра рецептов

## 🗄️ Схема базы данных

### Ключевые связи:
```
User 1:N Recipe (автор)
User N:N Recipe (избранное) через Favorite
User N:N Recipe (покупки) через ShoppingCart
User N:N User (подписки) через Subscription
Recipe N:N Ingredient через IngredientInRecipe
Recipe N:N Tag
```

## 🚀 API Endpoints

### Основные группы:
- `/api/auth/` - аутентификация (Djoser)
- `/api/users/` - пользователи и подписки
- `/api/recipes/` - рецепты, избранное, покупки
- `/api/ingredients/` - ингредиенты (поиск)
- `/api/tags/` - теги (список)

## 🐳 Контейнеризация

### Сервисы Docker Compose:
1. **backend** - Django приложение
2. **frontend** - React приложение (build)
3. **nginx** - веб-сервер
4. **db** - PostgreSQL
5. **redis** - кеширование

### Volumes:
- `static_volume` - статические файлы Django
- `media_volume` - пользовательские файлы
- `postgres_data` - данные БД

## 📊 Мониторинг и логирование

### Метрики:
- Время отклика API
- Количество активных пользователей
- Популярные рецепты

### Логи:
- Django логи (ERROR, WARNING)
- Nginx access/error логи
- PostgreSQL медленные запросы

## 🔧 Конфигурация

### Environment переменные:
```bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,192.168.0.10

# Database
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://192.168.0.3:6379/0

# MinIO
MINIO_ACCESS_KEY=access_key
MINIO_SECRET_KEY=secret_key
MINIO_BUCKET_NAME=foodgram
```

## 🔄 CI/CD Pipeline

### Этапы:
1. **Тестирование** - pytest, flake8, mypy
2. **Сборка** - Docker образы backend/frontend
3. **Пуш** - в registry 192.168.0.4
4. **Деплой** - на 192.168.0.10
5. **Проверки** - health checks

## 📈 Масштабирование

### Горизонтальное:
- Load balancer перед Django
- Реплики PostgreSQL
- Redis Cluster

### Вертикальное:
- Увеличение ресурсов контейнеров
- Оптимизация SQL запросов
- Кеширование в Redis 