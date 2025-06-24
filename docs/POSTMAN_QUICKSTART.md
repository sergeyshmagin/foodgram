# 🚀 Postman Quick Start - Шпаргалка

Быстрый старт для тестирования API Foodgram через Postman.

## ⚡ Быстрая настройка (5 минут)

### 1. Импорт коллекции
```
File → Import → Выбрать файл postman_collection/foodgram.postman_collection.json
```

### 2. Изменение базового URL
```
Коллекция → Три точки → Edit → Variables → baseUrl
Изменить на: https://foodgram.freedynamicdns.net
```

### 3. Запуск тестов
```
Коллекция → Три точки → Run collection → Run Foodgram
```

## 🎯 Ключевые эндпоинты для проверки

| Эндпоинт | Метод | Описание |
|----------|-------|----------|
| `/api/users/` | POST | Регистрация пользователя |
| `/api/auth/token/login/` | POST | Получение токена |
| `/api/recipes/` | GET | Список рецептов |
| `/api/recipes/` | POST | Создание рецепта |
| `/api/tags/` | GET | Список тегов |
| `/api/ingredients/` | GET | Список ингредиентов |
| `/api/recipes/download_shopping_cart/` | GET | Скачивание списка покупок |

## 🔧 Основные настройки

### Среда (Environment)
```
baseUrl: https://foodgram.freedynamicdns.net
```

### Заголовки аутентификации
```
Authorization: Token {{user_1_token}}
```

### Параметры запуска коллекции
- **Delay**: 500ms
- **Persist responses**: ✅ Включено
- **Save responses**: ✅ Включено

## ✅ Ожидаемые результаты

### Успешная регистрация
```json
{
    "email": "test@example.com",
    "id": 1,
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User"
}
```

### Успешная аутентификация
```json
{
    "auth_token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### Список рецептов
```json
{
    "count": 6,
    "next": null,
    "previous": null,
    "results": [...]
}
```

## 🚨 Частые проблемы

| Ошибка | Решение |
|--------|---------|
| `401 Unauthorized` | Проверьте токен в заголовке Authorization |
| `404 Not Found` | Проверьте правильность URL |
| `400 Bad Request` | Проверьте обязательные поля в теле запроса |
| `500 Internal Server Error` | Проверьте логи сервера |

## 📊 Критерии успеха

- [ ] ✅ Все тесты регистрации прошли (статус 201)
- [ ] ✅ Получены токены аутентификации
- [ ] ✅ Создан тестовый рецепт
- [ ] ✅ Работает поиск ингредиентов
- [ ] ✅ Работает добавление в избранное
- [ ] ✅ Работает скачивание списка покупок
- [ ] ✅ Время ответа < 2000ms

## 🔗 Полезные ссылки

- 📖 **Полная инструкция**: [docs/POSTMAN_TESTING.md](POSTMAN_TESTING.md)
- 🌐 **Продакшн сайт**: https://foodgram.freedynamicdns.net/
- 🛠️ **Admin панель**: https://foodgram.freedynamicdns.net/admin/
- 📋 **API документация**: https://foodgram.freedynamicdns.net/api/docs/

---

💡 **Совет**: Запускайте тесты по отдельности для детальной диагностики проблем. 