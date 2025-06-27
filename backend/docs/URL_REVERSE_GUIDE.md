# 🔗 Руководство по использованию Reverse URLs в Foodgram

## 📋 Обзор

В проекте Foodgram все URL endpoints имеют именованные паттерны для возможности использования Django reverse() функции. Это обеспечивает гибкость и поддерживаемость кода.

## 🛠️ Способы использования

### 1. Стандартный Django reverse()

```python
from django.urls import reverse

# Базовые URL
health_url = reverse("api:v1:health-check")
docs_url = reverse("api:v1:docs")
admin_url = reverse("admin:index")

# URL с параметрами
user_url = reverse("api:v1:users-detail", kwargs={"pk": 1})
recipe_url = reverse("api:v1:recipes-detail", kwargs={"pk": 1})
short_link = reverse("short-link", kwargs={"recipe_id": 1})
```

### 2. Утилитарный класс FoodgramURLs

```python
from apps.api.reverse_utils import FoodgramURLs

# Более читаемый способ
user_url = FoodgramURLs.users_detail(1)
recipe_url = FoodgramURLs.recipes_detail(1)
docs_url = FoodgramURLs.api_docs()
```

### 3. Константы URL_NAMES

```python
from apps.api.reverse_utils import URL_NAMES
from django.urls import reverse

# Использование констант
users_list = reverse(URL_NAMES["USERS_LIST"])
recipe_detail = reverse(URL_NAMES["RECIPES_DETAIL"], kwargs={"pk": 1})
```

### 4. Хелпер-функции

```python
from apps.api.reverse_utils import get_recipe_url, get_user_url, get_api_docs_url

recipe_url = get_recipe_url(recipe_id=1)
user_url = get_user_url(user_id=1)
docs_url = get_api_docs_url()
```

## 📚 Полный список URL

### API Endpoints

| Описание | URL Name | Пример URL | Функция FoodgramURLs |
|----------|----------|------------|---------------------|
| Health Check | `api:v1:health-check` | `/api/v1/health/` | `api_health_check()` |
| Swagger Docs | `api:v1:docs` | `/api/v1/docs/` | `api_docs()` |
| ReDoc | `api:v1:redoc` | `/api/v1/redoc/` | `api_redoc()` |
| OpenAPI Schema | `api:v1:schema` | `/api/v1/schema/` | `api_schema()` |

### Users

| Описание | URL Name | Пример URL | Функция FoodgramURLs |
|----------|----------|------------|---------------------|
| Список пользователей | `api:v1:users-list` | `/api/v1/users/` | `users_list()` |
| Детали пользователя | `api:v1:users-detail` | `/api/v1/users/1/` | `users_detail(1)` |
| Подписки | `api:v1:users-subscriptions` | `/api/v1/users/subscriptions/` | `users_subscriptions()` |
| Подписка | `api:v1:users-subscribe` | `/api/v1/users/1/subscribe/` | `users_subscribe(1)` |
| Аватар | `api:v1:users-avatar` | `/api/v1/users/me/avatar/` | `users_avatar()` |
| Смена пароля | `api:v1:users-set-password` | `/api/v1/users/set_password/` | `users_set_password()` |

### Recipes

| Описание | URL Name | Пример URL | Функция FoodgramURLs |
|----------|----------|------------|---------------------|
| Список рецептов | `api:v1:recipes-list` | `/api/v1/recipes/` | `recipes_list()` |
| Детали рецепта | `api:v1:recipes-detail` | `/api/v1/recipes/1/` | `recipes_detail(1)` |
| Избранное | `api:v1:recipes-favorite` | `/api/v1/recipes/1/favorite/` | `recipes_favorite(1)` |
| Корзина | `api:v1:recipes-shopping-cart` | `/api/v1/recipes/1/shopping_cart/` | `recipes_shopping_cart(1)` |
| Скачать корзину | `api:v1:recipes-download-shopping-cart` | `/api/v1/recipes/download_shopping_cart/` | `recipes_download_shopping_cart()` |
| Короткая ссылка | `api:v1:recipes-get-link` | `/api/v1/recipes/1/get-link/` | `recipes_get_link(1)` |

### Tags

| Описание | URL Name | Пример URL | Функция FoodgramURLs |
|----------|----------|------------|---------------------|
| Список тегов | `api:v1:tags-list` | `/api/v1/tags/` | `tags_list()` |
| Детали тега | `api:v1:tags-detail` | `/api/v1/tags/1/` | `tags_detail(1)` |

### Ingredients

| Описание | URL Name | Пример URL | Функция FoodgramURLs |
|----------|----------|------------|---------------------|
| Список ингредиентов | `api:v1:ingredients-list` | `/api/v1/ingredients/` | `ingredients_list()` |
| Детали ингредиента | `api:v1:ingredients-detail` | `/api/v1/ingredients/1/` | `ingredients_detail(1)` |

### Дополнительные

| Описание | URL Name | Пример URL | Функция FoodgramURLs |
|----------|----------|------------|---------------------|
| Короткая ссылка | `short-link` | `/s/1/` | `short_link(1)` |
| Админка | `admin:index` | `/admin/` | `admin()` |

## 💡 Примеры использования в коде

### В Views

```python
from django.shortcuts import redirect
from apps.api.reverse_utils import FoodgramURLs

def my_view(request):
    # Перенаправление на страницу рецепта
    return redirect(FoodgramURLs.recipes_detail(recipe_id))
```

### В Serializers

```python
from apps.api.reverse_utils import get_recipe_url

class MySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    def get_url(self, obj):
        return get_recipe_url(obj.id)
```

### В Templates (если используются)

```html
{% url 'api:v1:recipes-detail' pk=recipe.id %}
```

### В Тестах

```python
from apps.api.reverse_utils import URL_NAMES, FoodgramURLs

def test_recipe_detail():
    url = reverse(URL_NAMES["RECIPES_DETAIL"], kwargs={"pk": 1})
    # или
    url = FoodgramURLs.recipes_detail(1)
    response = client.get(url)
```

## 🧪 Тестирование

Все reverse URLs покрыты тестами в `tests/test_reverse_urls.py`. Запуск тестов:

```bash
python -m pytest tests/test_reverse_urls.py -v
```

## 🔧 Добавление новых URL

При добавлении новых endpoints:

1. **Добавьте name в urlpatterns:**
```python
path("new-endpoint/", my_view, name="new-endpoint")
```

2. **Обновите reverse_utils.py:**
```python
# В класс FoodgramURLs
@staticmethod
def new_endpoint():
    return reverse("api:v1:new-endpoint")

# В константы URL_NAMES
"NEW_ENDPOINT": "api:v1:new-endpoint"
```

3. **Добавьте тесты:**
```python
def test_new_endpoint_url(self):
    assert FoodgramURLs.new_endpoint() == "/api/v1/new-endpoint/"
```

## ⚠️ Важные замечания

1. **Всегда используйте reverse()** вместо хардкода URL
2. **Namespace структура:** `api:v1:endpoint-name`
3. **Тестируйте все новые URL** на возможность reverse
4. **Используйте константы** из `URL_NAMES` для избежания опечаток
5. **Документируйте новые endpoints** в этом файле 