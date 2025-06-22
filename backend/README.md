# Foodgram Backend API

Бэкенд для веб-приложения Foodgram - платформы для публикации рецептов.

## ✅ Завершённые этапы разработки

### Этап 1-3: Основа проекта
- ✅ Архитектура Django с приложениями `users`, `recipes`, `api`
- ✅ Модели: User, Recipe, Ingredient, Tag, Favorite, ShoppingCart, Subscription  
- ✅ Загружены данные ингредиентов (2186 записей)
- ✅ Настроена админка для всех моделей
- ✅ Создан суперпользователь: `admin@foodgram.ru` / `admin123`

### Этап 4: REST API ✅ ЗАВЕРШЁН
Полноценный REST API согласно **OpenAPI спецификации** (`docs/openapi-schema.yml`):

#### 👥 Пользователи `/api/users/`
- `GET /api/users/` - список пользователей (пагинация)
- `POST /api/users/` - регистрация нового пользователя
- `GET /api/users/{id}/` - профиль пользователя по ID
- `GET /api/users/me/` - текущий пользователь
- `PUT /api/users/me/avatar/` - установка аватара (base64)
- `DELETE /api/users/me/avatar/` - удаление аватара
- `POST /api/users/set_password/` - смена пароля

#### 🔐 Аутентификация `/api/auth/`
- `POST /api/auth/token/login/` - получить токен по email/password
- `POST /api/auth/token/logout/` - удалить токен

#### 👨‍👩‍👧‍👦 Подписки `/api/users/`
- `GET /api/users/subscriptions/` - мои подписки (с рецептами)
- `POST /api/users/{id}/subscribe/` - подписаться на пользователя
- `DELETE /api/users/{id}/subscribe/` - отписаться от пользователя

#### 🏷️ Теги `/api/tags/`
- `GET /api/tags/` - список всех тегов (без пагинации)
- `GET /api/tags/{id}/` - получить тег по ID

#### 🥕 Ингредиенты `/api/ingredients/`
- `GET /api/ingredients/` - список ингредиентов (без пагинации)
- `GET /api/ingredients/?name=мука` - поиск по началу названия
- `GET /api/ingredients/{id}/` - получить ингредиент по ID

#### 🍳 Рецепты `/api/recipes/`
- `GET /api/recipes/` - список рецептов (пагинация, фильтры)
- `POST /api/recipes/` - создать рецепт (только авторизованные)
- `GET /api/recipes/{id}/` - получить рецепт по ID
- `PATCH /api/recipes/{id}/` - обновить рецепт (только автор)
- `DELETE /api/recipes/{id}/` - удалить рецепт (только автор)
- `GET /api/recipes/{id}/get-link/` - короткая ссылка на рецепт

##### Фильтры для рецептов:
- `?is_favorited=1` - только избранные рецепты
- `?is_in_shopping_cart=1` - только рецепты в корзине
- `?author={user_id}` - рецепты конкретного автора  
- `?tags=breakfast&tags=lunch` - фильтр по тегам (slug)

#### ❤️ Избранное `/api/recipes/{id}/favorite/`
- `POST /api/recipes/{id}/favorite/` - добавить в избранное
- `DELETE /api/recipes/{id}/favorite/` - удалить из избранного

#### 🛒 Список покупок `/api/recipes/{id}/shopping_cart/`
- `POST /api/recipes/{id}/shopping_cart/` - добавить в список покупок
- `DELETE /api/recipes/{id}/shopping_cart/` - удалить из списка покупок
- `GET /api/recipes/download_shopping_cart/` - скачать список покупок (TXT)

## 🛠 Технические особенности

### Аутентификация
- **Token Authentication** - все защищённые endpoints требуют заголовок:
  ```
  Authorization: Token YOUR_TOKEN_HERE
  ```

### Загрузка изображений
- Поддержка **base64** формата для рецептов и аватаров:
  ```json
  {
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAAB..."
  }
  ```

### Права доступа
- **Публичное чтение**: теги, ингредиенты, рецепты, профили пользователей
- **Авторизация требуется**: создание/изменение рецептов, избранное, корзина, подписки
- **Только автор**: изменение/удаление своих рецептов

### Оптимизация запросов
- `select_related()` и `prefetch_related()` для избежания N+1 queries
- Аннотации для подсчёта избранного и рецептов пользователей

## 🚀 Запуск проекта

### Подготовка окружения
```bash
# Запуск инфраструктуры (PostgreSQL, Redis, MinIO)
docker-compose -f docker-compose.dev.yml up -d

# Активация виртуального окружения
source venv/bin/activate  # Linux/Mac
# или
venv/Scripts/activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Загрузка тестовых данных
python manage.py loaddata fixtures/ingredients.json
python manage.py create_test_data
python manage.py create_admin

# Запуск сервера
python manage.py runserver
```

### API доступен по адресу:
- **API Base URL**: http://localhost:8000/api/
- **Админка**: http://localhost:8000/admin/ (admin@foodgram.ru / admin123)
- **API Docs**: `/docs/redoc.html` (ReDoc)

## 🧪 Тестирование

```bash
# Запуск тестов API
pytest apps/api/tests.py -v

# Покрытие тестами
pytest --cov=apps
```

## 📚 Документация API

- **OpenAPI Schema**: `docs/openapi-schema.yml`
- **ReDoc UI**: `docs/redoc.html`
- **Архитектура**: `docs/architecture.md`
- **Best Practices**: `docs/best_practices.md`

## 🔄 Статус проекта

**✅ Этапы 1-4 ЗАВЕРШЕНЫ**
- Готов к интеграции с фронтендом React
- Готов к тестированию полного функционала
- Готов к следующему этапу: деплой и CI/CD

Все API endpoints соответствуют спецификации OpenAPI и готовы к использованию! 