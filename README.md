# 🍽️ Foodgram - Платформа кулинарных рецептов

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2+-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)](https://redis.io)

> 🚀 **Современная платформа для публикации кулинарных рецептов с возможностью создания списка покупок и подписки на авторов.**

## ✨ Особенности

- 📝 **Публикация рецептов** с фотографиями и подробным описанием
- ⭐ **Избранное** - сохраняйте понравившиеся рецепты
- 🛒 **Умный список покупок** - автоматическое создание на основе выбранных рецептов
- 👥 **Подписки** на любимых авторов рецептов
- 📱 **Адаптивный дизайн** для всех устройств
- 🔍 **Поиск и фильтрация** по тегам и ингредиентам
- 🔗 **Короткие ссылки** для быстрого обмена рецептами
- 📊 **REST API** с полной документацией

## 🌐 Live Demo

- 🎯 **Основной сайт**: [foodgram.freedynamicdns.net](https://foodgram.freedynamicdns.net)
- 🔧 **Админ-панель**: [foodgram.freedynamicdns.net/admin](https://foodgram.freedynamicdns.net/admin)
- 📡 **API Documentation**: [foodgram.freedynamicdns.net/api/docs](https://foodgram.freedynamicdns.net/api/docs)

## 🏗️ Технологический стек

### Backend
- **🐍 Python 3.9+** - основной язык разработки
- **🎯 Django 4.2+** - веб-фреймворк
- **🔌 Django REST Framework** - создание REST API
- **🐘 PostgreSQL 13+** - основная база данных
- **⚡ Redis 7.0** - кеширование и очереди
- **📦 MinIO** - S3-совместимое файловое хранилище
- **🔒 JWT Authentication** - безопасная аутентификация

### Frontend
- **⚛️ React 18** - пользовательский интерфейс
- **🚦 React Router** - маршрутизация
- **📡 Axios** - HTTP клиент
- **🎨 CSS Modules** - стилизация компонентов

### DevOps & Infrastructure
- **🐳 Docker & Docker Compose** - контейнеризация
- **🌐 Nginx** - веб-сервер и реверс-прокси
- **🔄 GitHub Actions** - CI/CD пайплайн
- **📊 Prometheus & Grafana** - мониторинг (опционально)

## 🚀 Быстрый старт

### Предварительные требования
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 1️⃣ Клонирование проекта
```bash
git clone https://github.com/sergeyshmagin/foodgram.git
cd foodgram
```

### 2️⃣ Настройка окружения
```bash
# Копируем пример конфигурации
cp infra/production.env.example infra/.env

# Редактируем переменные окружения
nano infra/.env
```

### 3️⃣ Запуск приложения
```bash
# Запуск всех сервисов
docker compose -f infra/docker-compose.yml up -d --build

# Выполнение миграций
docker exec foodgram-backend python manage.py migrate

# Загрузка начальных данных
docker exec foodgram-backend python manage.py load_ingredients

# Создание суперпользователя
docker exec -it foodgram-backend python manage.py createsuperuser
```

### 4️⃣ Доступ к приложению
- 🌐 **Веб-сайт**: http://localhost
- 📡 **API**: http://localhost/api/
- 🔧 **Админ-панель**: http://localhost/admin/
- 🗄️ **MinIO Console**: http://localhost:9001

## 📚 API Документация

### 🔑 Аутентификация
```bash
# Получение токена
POST /api/auth/token/login/
{
  "email": "user@example.com",
  "password": "password"
}

# Выход из системы
POST /api/auth/token/logout/
```

### 👥 Пользователи
```bash
GET    /api/users/                    # Список пользователей
POST   /api/users/                    # Регистрация
GET    /api/users/{id}/               # Профиль пользователя
POST   /api/users/{id}/subscribe/     # Подписка/отписка
GET    /api/users/subscriptions/      # Мои подписки
```

### 📝 Рецепты
```bash
GET    /api/recipes/                  # Список рецептов
POST   /api/recipes/                  # Создание рецепта
GET    /api/recipes/{id}/             # Детали рецепта
PUT    /api/recipes/{id}/             # Обновление рецепта
DELETE /api/recipes/{id}/             # Удаление рецепта
POST   /api/recipes/{id}/favorite/    # Добавить в избранное
POST   /api/recipes/{id}/shopping_cart/ # Добавить в корзину
GET    /api/recipes/download_shopping_cart/ # Скачать список покупок
```

### 🏷️ Дополнительные endpoints
```bash
GET /api/ingredients/     # Список ингредиентов
GET /api/tags/           # Список тегов
```

**📖 Полная документация**: [/api/docs/](https://foodgram.freedynamicdns.net/api/docs/)

## 🧪 Тестирование

### Unit тесты
```bash
# Запуск всех тестов
docker exec foodgram-backend python -m pytest

# Тесты с покрытием
docker exec foodgram-backend python -m pytest --cov=apps --cov-report=html

# Статус: ✅ 143/143 тестов проходят (100% успех)
```

### Postman коллекция
Готовая коллекция для тестирования API:

1. **Импортируйте**: `postman_collection/foodgram.postman_collection.json`
2. **Настройте базовый URL**: `https://foodgram.freedynamicdns.net`
3. **Запустите автоматическое тестирование**

**📋 Подробная инструкция**: [scripts/deploy/docs/](./scripts/deploy/docs/)

## 🛠️ Локальная разработка

### Backend разработка
```bash
# Переход в backend директорию
cd backend

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/macOS
# или venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements/development.txt

# Настройка переменных окружения
cp env.example .env
nano .env

# Запуск сервера разработки
python manage.py migrate
python manage.py runserver
```

### Frontend разработка
```bash
# Переход в frontend директорию
cd frontend

# Установка зависимостей
npm install

# Запуск сервера разработки
npm start
```

### Качество кода
```bash
# Форматирование кода
black backend/
isort backend/

# Проверка стиля
flake8 backend/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## 📁 Структура проекта

```
foodgram/
├── 🔧 backend/                    # Django REST API
│   ├── apps/                     # Django приложения
│   │   ├── api/                  # REST API endpoints
│   │   ├── recipes/              # Модели рецептов
│   │   └── users/                # Пользователи и авторизация
│   ├── foodgram/                 # Настройки проекта
│   │   ├── settings/             # Настройки по окружениям
│   │   └── ...
│   ├── requirements/             # Зависимости
│   └── tests/                    # Unit тесты
├── ⚛️ frontend/                   # React приложение
│   ├── public/                   # Публичные файлы
│   ├── src/                      # Исходный код
│   │   ├── components/           # React компоненты
│   │   ├── pages/               # Страницы приложения
│   │   └── utils/               # Утилиты
│   └── package.json             # Зависимости Node.js
├── 🚀 infra/                     # Инфраструктура
│   ├── docker-compose.yml       # Docker Compose конфигурация
│   ├── nginx.conf               # Настройки Nginx
│   └── *.env.example           # Примеры переменных окружения
├── 📋 scripts/                   # Скрипты автоматизации
│   └── deploy/                  # Скрипты развертывания
│       ├── production/          # Продакшн скрипты
│       ├── maintenance/         # Обслуживание
│       ├── testing/            # Тестирование
│       └── docs/               # Документация
└── 📊 data/                     # Данные (ингредиенты, демо-контент)
```

## 🚀 Развертывание на продакшене

### Автоматическое развертывание (рекомендуется)
Проект настроен для автоматического развертывания через GitHub Actions:

1. **Fork репозитория**
2. **Настройте GitHub Secrets**:
   - `PROD_USER` - пользователь сервера
   - `PROD_SSH_KEY` - SSH ключ
   - `SECRET_KEY` - Django secret key
   - `POSTGRES_PASSWORD` - пароль PostgreSQL
   - `MINIO_SECRET_KEY` - ключ MinIO
   - `ADMIN_PASSWORD` - пароль администратора

3. **Push в main ветку** - автоматический деплой запустится

### Ручное развертывание
```bash
# На сервере
git clone https://github.com/your-username/foodgram.git
cd foodgram

# Настройка окружения
cp infra/production.env.example infra/.env
nano infra/.env

# Запуск
docker compose -f infra/docker-compose.yml up -d --build

# Инициализация
./scripts/deploy/production/load_production_data.sh
```

## 🔧 Обслуживание

### Полезные скрипты
```bash
# Очистка тестовых данных
python scripts/deploy/maintenance/clear_prod_test_data.py

# Валидация рецептов
python scripts/deploy/maintenance/fix_recipes_validation.py

# Очистка Docker
./scripts/deploy/maintenance/cleanup_containers.sh
```

### Мониторинг
- **Логи**: `docker logs foodgram-backend`
- **Статус сервисов**: `docker ps`
- **Использование ресурсов**: `docker stats`

## 🤝 Вклад в проект

1. **Fork** репозитория
2. **Создайте** feature branch (`git checkout -b feature/amazing-feature`)
3. **Зафиксируйте** изменения (`git commit -m 'Add amazing feature'`)
4. **Push** в branch (`git push origin feature/amazing-feature`)
5. **Откройте** Pull Request

### Стандарты кода
- Следуйте **PEP 8** для Python
- Используйте **pre-commit hooks**
- Покрытие тестами **>80%**
- Документируйте новый функционал

## 📄 Лицензия

Этот проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE) для подробностей.

## 👨‍💻 Автор

**Sergey Shmagin**
- GitHub: [@sergeyshmagin](https://github.com/sergeyshmagin)
- Email: sergey.shmagin@gmail.com

## 🙏 Благодарности

- Команде **Django** за отличный фреймворк
- Команде **React** за мощную библиотеку
- Команде **Яндекс.Практикум** за техническое задание
- Сообществу **Open Source** за вдохновение

---

⭐ **Поставьте звезду, если проект был полезен!**

