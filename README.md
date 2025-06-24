# Foodgram

Платформа для публикации кулинарных рецептов с возможностью создания списка покупок и подписки на авторов.

## Описание проекта

Foodgram - это веб-приложение для любителей кулинарии, которое позволяет:
- Публиковать рецепты с фотографиями
- Добавлять рецепты в избранное
- Создавать список покупок на основе выбранных рецептов
- Подписываться на других авторов рецептов
- Скачивать список покупок в формате PDF

## Технологический стек

### Backend:
- Python 3.9
- Django 3.2.16
- Django REST Framework 3.12.4
- PostgreSQL 13
- Redis 7.0
- MinIO (S3-совместимое хранилище)
- Celery (фоновые задачи)
- Gunicorn (WSGI сервер)

### Frontend:
- React 18
- React Router
- Axios
- CSS Modules

### Инфраструктура:
- Docker & Docker Compose
- Nginx (реверс-прокси)
- GitHub Actions (CI/CD)

## Быстрый старт

### Предварительные требования:
- Docker и Docker Compose
- Git

### Локальная установка:

#### 1. Клонирование репозитория:
```bash
git clone https://github.com/your-username/FINAL.git
cd FINAL
```

#### 2. Настройка переменных окружения:
```bash
cp infra/production.env.example infra/.env
# Отредактируйте infra/.env под ваши нужды
```

#### 3. Запуск приложения:
```bash
docker-compose -f infra/docker-compose.yml up -d --build
```

#### 4. Инициализация:
```bash
# Миграции базы данных
docker exec foodgram-backend python manage.py migrate

# Создание суперпользователя
docker exec -it foodgram-backend python manage.py createsuperuser

# Загрузка данных
docker exec foodgram-backend python manage.py load_ingredients
```

### Доступ к приложению:
- **Сайт**: http://localhost
- **API**: http://localhost/api/
- **Админ-панель**: http://localhost/admin/
- **MinIO Console**: http://localhost:9001

## Развертывание

#### 1. Подготовка сервера:
```bash
# Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Клонирование репозитория
git clone https://github.com/your-username/FINAL.git
cd FINAL
```

#### 2. Настройка окружения:
```bash
cp infra/production.env.example infra/.env
# Настройте переменные окружения
```

#### 3. Запуск:
```bash
docker-compose -f infra/docker-compose.yml up -d --build
```

## Продакшн URL-адреса

- **🌐 Сайт**: https://foodgram.freedynamicdns.net
- **🔧 Админка**: https://foodgram.freedynamicdns.net/admin/
- **📡 API**: https://foodgram.freedynamicdns.net/api/
- **🗄️ MinIO Console**: https://foodgram.freedynamicdns.net:9001/

## API Документация

### Основные endpoints:

#### Аутентификация:
- `POST /api/auth/token/login/` - получение токена
- `POST /api/auth/token/logout/` - выход из системы

#### Пользователи:
- `GET /api/users/` - список пользователей
- `POST /api/users/` - регистрация
- `GET /api/users/{id}/` - профиль пользователя
- `POST /api/users/{id}/subscribe/` - подписка на пользователя

#### Рецепты:
- `GET /api/recipes/` - список рецептов
- `POST /api/recipes/` - создание рецепта
- `GET /api/recipes/{id}/` - получение рецепта
- `PUT /api/recipes/{id}/` - обновление рецепта
- `DELETE /api/recipes/{id}/` - удаление рецепта
- `POST /api/recipes/{id}/favorite/` - добавление в избранное
- `POST /api/recipes/{id}/shopping_cart/` - добавление в корзину

#### Дополнительные:
- `GET /api/ingredients/` - список ингредиентов
- `GET /api/tags/` - список тегов
- `GET /api/recipes/download_shopping_cart/` - скачать список покупок

### Полная документация API доступна по адресу: `/api/docs/`

## 🧪 Тестирование API

### Postman коллекция
Для тестирования API используйте готовую Postman коллекцию:

- 📖 **Полная инструкция**: [docs/POSTMAN_TESTING.md](docs/POSTMAN_TESTING.md)
- 🚀 **Быстрый старт**: [docs/POSTMAN_QUICKSTART.md](docs/POSTMAN_QUICKSTART.md)
- 📋 **Коллекция**: `postman_collection/foodgram.postman_collection.json`

### Быстрая настройка Postman:
1. Импортируйте коллекцию из `postman_collection/foodgram.postman_collection.json`
2. Измените базовый URL на `https://foodgram.freedynamicdns.net`
3. Запустите коллекцию для автоматического тестирования всех endpoints

## Разработка

### Локальная разработка:

#### 1. Настройка окружения:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

pip install -r requirements/development.txt
```

#### 2. Настройка переменных:
```bash
cp env.example .env
# Отредактируйте .env
```

#### 3. Запуск:
```bash
python manage.py migrate
python manage.py runserver
```

### Тестирование:
```bash
# Запуск тестов
pytest

# Запуск с покрытием
pytest --cov=apps --cov-report=html
```

## Структура проекта

```
FINAL/
├── backend/                # Django REST API
│   ├── apps/              # Приложения Django
│   ├── foodgram/          # Настройки проекта
│   ├── requirements/      # Зависимости
│   └── tests/            # Тесты
├── frontend/              # React приложение
├── infra/                # Docker конфигурация
├── docs/                 # Документация
└── scripts/              # Скрипты развертывания
```

## Лицензия

MIT License

## Авторы

Проект разработан в рамках обучения на курсе "Python-разработчик" от Яндекс.Практикум

