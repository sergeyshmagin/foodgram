# Скрипты загрузки данных в продакшн

Этот каталог содержит скрипты для загрузки различных типов данных в продакшн.

## 🚀 GitHub Actions Workflow

### Автоматическая загрузка через GitHub Actions

Используйте workflow **"Load Data to Production"** в GitHub Actions:

1. Перейдите в раздел **Actions** вашего GitHub репозитория
2. Найдите workflow **"Load Data to Production"**
3. Нажмите **"Run workflow"**
4. Выберите параметры:
   - **confirm**: обязательно введите `yes` для подтверждения
   - **load_type**: выберите тип данных для загрузки:
     - `basic` - только базовые данные (администратор, теги, ингредиенты)
     - `demo` - только демо-данные (рецепты)
     - `full` - все данные (базовые + демо)

### Типы загрузки данных

#### `basic` - Базовые данные
- 👤 Администратор: `admin@foodgram.local / admin123`
- 🏷️ Базовые теги: Завтрак, Обед, Ужин, Десерт
- 🥕 2186+ ингредиентов из CSV файла

#### `demo` - Демо-данные
- 🍽️ Примеры рецептов
- 👥 Тестовые пользователи
- ❤️ Примеры избранного и корзины

#### `full` - Полные данные
- Все базовые данные
- Все демо-данные

## 🛠️ Ручная загрузка

### Локальный скрипт

Для ручной загрузки данных используйте скрипт:

```bash
# Из корня проекта
./scripts/deploy/load_production_data.sh [basic|demo|full]
```

Примеры:
```bash
# Загрузить только базовые данные
./scripts/deploy/load_production_data.sh basic

# Загрузить все данные
./scripts/deploy/load_production_data.sh full
```

### 🧪 Тестирование загрузки ингредиентов

Если у вас проблемы с загрузкой ингредиентов, используйте диагностический скрипт:

```bash
# Тестировать загрузку ингредиентов
./scripts/deploy/test_ingredients_loading.sh
```

Этот скрипт:
- ✅ Проверит наличие файла ингредиентов в контейнере
- 📊 Покажет количество ингредиентов в файле и базе данных
- 🔄 Попробует загрузить ингредиенты
- 📈 Покажет результат загрузки

### Отдельные команды Django

Вы также можете запускать команды Django по отдельности:

```bash
# Базовые данные (администратор и теги)
sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py setup_production

# Ингредиенты
sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py load_ingredients --file data/ingredients.csv

# Демо-данные (если есть)
sudo docker compose -f infra/docker-compose.yml exec -T backend python manage.py load_demo_data
```

## 📋 После загрузки

### Аккаунты для входа

После успешной загрузки базовых данных:

- **👤 Администратор**: `admin@foodgram.local / admin123`

### Ссылки

- 🌐 **Сайт**: https://foodgram.freedynamicdns.net/
- 🛠️ **Admin панель**: https://foodgram.freedynamicdns.net/admin/

### Проверка данных

1. Войдите в админ-панель под учетной записью администратора
2. Проверьте разделы:
   - **Теги** - должно быть 4 базовых тега
   - **Ингредиенты** - должно быть 2000+ ингредиентов
   - **Пользователи** - должен быть администратор

## ⚠️ Важные замечания

1. **Безопасность**: Пароль администратора всегда обновляется при загрузке
2. **Данные**: Команды не удаляют существующие данные, только добавляют новые
3. **Ингредиенты**: Загружаются без дублирования (проверка по имени + единица измерения)
4. **Подтверждение**: Всегда требуется явное подтверждение для запуска в продакшн

## 🔧 Устранение неполадок

### Команда не найдена
```
⚠️ Команда load_demo_data не найдена, пропускаем
```
Это нормально - команда демо-данных опциональная.

### Файл не найден
```
❌ Файл не найден: data/ingredients.csv
```
**Решение:**
1. Убедитесь, что файл `data/ingredients.csv` существует в корне проекта
2. Перезапустите контейнеры для обновления монтирования томов:
   ```bash
   sudo docker compose -f infra/docker-compose.yml down
   sudo docker compose -f infra/docker-compose.yml up -d
   ```
3. Запустите диагностический скрипт: `./scripts/deploy/test_ingredients_loading.sh`

### Контейнеры не запущены
```
❌ Backend контейнер не найден
```
Запустите контейнеры: `sudo docker compose -f infra/docker-compose.yml up -d`

## 📁 Структура файлов

```
scripts/deploy/
├── README.md                    # Эта документация
├── load_production_data.sh      # Скрипт ручной загрузки
└── test_ingredients_loading.sh  # Тестирование ингредиентов

.github/workflows/
└── setup-test-data.yml          # GitHub Actions workflow

backend/apps/recipes/management/commands/
├── setup_production.py          # Команда базовых данных (админ + теги)
├── load_ingredients.py          # Команда загрузки ингредиентов из CSV
└── load_demo_data.py            # Команда демо-данных (рецепты)
``` 