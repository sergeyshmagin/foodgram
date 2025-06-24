# 🧪 Тестирование API Foodgram через Postman

Полная инструкция по тестированию API продакшн версии Foodgram с помощью Postman коллекции.

## 📋 Предварительные требования

### 1. Установка Postman
- Скачайте и установите [Postman](https://www.postman.com/downloads/)
- Создайте бесплатный аккаунт (рекомендуется для синхронизации коллекций)

### 2. Состояние продакшн сервера
Убедитесь, что продакшн сервер запущен и доступен:
- ✅ **Сайт**: https://foodgram.freedynamicdns.net/
- ✅ **API**: https://foodgram.freedynamicdns.net/api/
- ✅ **Admin**: https://foodgram.freedynamicdns.net/admin/

### 3. Данные загружены
Убедитесь, что на сервере загружены тестовые данные:
```bash
# На продакшн сервере
bash scripts/deploy/load_production_data.sh full
```

## 🚀 Настройка Postman коллекции

### Шаг 1: Импорт коллекции

1. **Запустите Postman**
2. **Импортируйте коллекцию**:
   - Нажмите `File` → `Import`
   - Выберите файл `postman_collection/foodgram.postman_collection.json`
   - Нажмите `Import`

### Шаг 2: Настройка переменных среды

1. **Создайте новую среду**:
   - В правом верхнем углу нажмите на выпадающий список сред
   - Выберите `Create Environment`
   - Назовите среду `Foodgram Production`

2. **Добавьте переменные**:
   ```
   Variable Name: baseUrl
   Initial Value: https://foodgram.freedynamicdns.net
   Current Value: https://foodgram.freedynamicdns.net
   ```

3. **Сохраните среду** и **активируйте её**

### Шаг 3: Обновление базового URL в коллекции

**ВАЖНО!** Коллекция по умолчанию настроена на localhost. Нужно изменить базовый URL:

1. **Откройте коллекцию** в левой панели
2. **Нажмите на три точки** рядом с названием коллекции
3. **Выберите `Edit`**
4. **Перейдите на вкладку `Variables`**
5. **Измените переменную `baseUrl`**:
   - **Initial Value**: `https://foodgram.freedynamicdns.net`
   - **Current Value**: `https://foodgram.freedynamicdns.net`
6. **Сохраните изменения**

## 🧪 Запуск тестов

### Автоматический запуск всей коллекции

1. **Запустите коллекцию**:
   - Наведите курсор на коллекцию
   - Нажмите три точки → `Run collection`

2. **Настройте параметры запуска**:
   - ✅ Включите `Persist responses for a session`
   - ✅ Включите `Save responses`
   - ⚙️ Delay: `500ms` (для стабильности)
   - 🔄 Iterations: `1`

3. **Запустите тесты**: нажмите `Run Foodgram`

### Ручное тестирование отдельных запросов

Для детального тестирования рекомендуется запускать запросы по отдельности:

#### 1. Регистрация пользователей
```
POST /api/users/
```
- Создаёт 3 тестовых пользователя автоматически
- Проверяет корректность регистрации

#### 2. Аутентификация
```
POST /api/auth/token/login/
```
- Получает токены для тестовых пользователей
- Сохраняет токены в переменных коллекции

#### 3. Профили пользователей
```
GET /api/users/
GET /api/users/{id}/
```
- Проверяет получение списка пользователей
- Проверяет получение профиля пользователя

#### 4. Подписки
```
POST /api/users/{id}/subscribe/
DELETE /api/users/{id}/subscribe/
GET /api/users/subscriptions/
```

#### 5. Теги и ингредиенты
```
GET /api/tags/
GET /api/ingredients/
GET /api/ingredients/?search=мука
```

#### 6. Рецепты
```
GET /api/recipes/
POST /api/recipes/
GET /api/recipes/{id}/
PATCH /api/recipes/{id}/
DELETE /api/recipes/{id}/
```

#### 7. Избранное и корзина
```
POST /api/recipes/{id}/favorite/
DELETE /api/recipes/{id}/favorite/
POST /api/recipes/{id}/shopping_cart/
DELETE /api/recipes/{id}/shopping_cart/
GET /api/recipes/download_shopping_cart/
```

## 📊 Анализ результатов

### Успешные тесты
- ✅ **Status Code**: 200, 201, 204 (в зависимости от запроса)
- ✅ **Response Time**: < 2000ms
- ✅ **Content-Type**: application/json
- ✅ **Required Fields**: присутствуют в ответе

### Типичные ошибки и их решения

#### 🔴 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```
**Решение**: Проверьте, что токен аутентификации передаётся в заголовке `Authorization: Token <your_token>`

#### 🔴 400 Bad Request
```json
{
    "field_name": ["This field is required."]
}
```
**Решение**: Проверьте обязательные поля в теле запроса

#### 🔴 404 Not Found
```json
{
    "detail": "Not found."
}
```
**Решение**: Проверьте правильность URL и существование ресурса

#### 🔴 500 Internal Server Error
**Решение**: Проверьте логи сервера, возможно проблема с базой данных или конфигурацией

## 🔧 Продвинутые возможности

### Использование переменных коллекции

Коллекция автоматически сохраняет важные данные в переменных:
- `user_1_token`, `user_2_token`, `user_3_token` - токены пользователей
- `user_1_id`, `user_2_id`, `user_3_id` - ID пользователей
- `recipe_id` - ID созданного рецепта
- `tag_ids` - массив ID тегов
- `ingredient_ids` - массив ID ингредиентов

### Настройка дополнительных тестов

Вы можете добавить собственные тесты в раздел `Tests` каждого запроса:

```javascript
// Проверка времени ответа
pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

// Проверка структуры ответа
pm.test("Response has required fields", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    pm.expect(jsonData).to.have.property('name');
});
```

## 📈 Мониторинг производительности

### Время ответа
- **Отлично**: < 200ms
- **Хорошо**: 200-500ms
- **Приемлемо**: 500-1000ms
- **Медленно**: > 1000ms

### Нагрузочное тестирование
Для нагрузочного тестирования увеличьте количество итераций:
- **Iterations**: 10-50
- **Delay**: 100-500ms

## 🔄 Повторный запуск тестов

### Очистка данных (для локальной разработки)
```bash
# Только для локальной разработки!
cd postman_collection
bash clear_db.sh
```

### Для продакшн среды
Данные в продакшн автоматически управляются через безопасные команды Django, которые не создают дубликатов.

## 📋 Чек-лист успешного тестирования

- [ ] ✅ Postman установлен и настроен
- [ ] ✅ Коллекция импортирована
- [ ] ✅ Базовый URL изменён на продакшн
- [ ] ✅ Среда `Foodgram Production` создана и активирована
- [ ] ✅ Продакшн сервер доступен
- [ ] ✅ Данные загружены на сервере
- [ ] ✅ Все тесты регистрации прошли успешно
- [ ] ✅ Аутентификация работает
- [ ] ✅ CRUD операции с рецептами работают
- [ ] ✅ Подписки и избранное функционируют
- [ ] ✅ Загрузка списка покупок работает
- [ ] ✅ Время ответа приемлемое (< 2000ms)

## 🆘 Получение помощи

### Логи сервера
```bash
# На продакшн сервере
sudo docker logs foodgram-backend
sudo docker logs foodgram-nginx
```

### Проверка состояния сервисов
```bash
# На продакшн сервере
sudo docker ps
sudo docker compose -f infra/docker-compose.yml ps
```

### Контакты для поддержки
- 📧 Проверьте логи в `/app/sent_emails/` в backend контейнере
- 🔧 Используйте диагностические скрипты в `scripts/deploy/`

---

**🎯 Цель тестирования**: Убедиться, что все API endpoints работают корректно в продакшн среде и готовы для использования фронтенд приложением. 