# Исправление отображения изображений MinIO

## Проблема
Изображения рецептов и аватары пользователей не отображались на сайте из-за неправильной конфигурации MinIO.

## Корневые причины
1. **Неправильный MEDIA_URL** - использовались прямые ссылки на MinIO вместо nginx proxy
2. **Отсутствие CORS политик** в MinIO
3. **Неправильная nginx конфигурация** для проксирования к MinIO
4. **Отсутствие автоматической настройки** bucket и публичных политик

## Исправления

### 1. Django Settings (`backend/foodgram/settings/production.py`)
```python
# Изменено: используем nginx proxy вместо прямых ссылок
MEDIA_URL = "/media/"  # Было: f"http://{MINIO_PUBLIC_ENDPOINT}/foodgram/media/"

# Удалены неиспользуемые настройки:
# - MINIO_PUBLIC_ENDPOINT
# - AWS_S3_CUSTOM_DOMAIN
```

### 2. Docker Compose (`infra/docker-compose.yml`)
```yaml
# Добавлены CORS настройки для MinIO
environment:
  MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
  MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
  # Новые настройки:
  MINIO_API_CORS_ALLOW_ORIGIN: "*"
  MINIO_BROWSER_REDIRECT_URL: "https://foodgram.freedynamicdns.net/minio"
```

### 3. Nginx Configuration (`infra/nginx.conf`)
```nginx
# Улучшена конфигурация для MinIO
location /media/ {
    proxy_pass http://minio:9000/foodgram/media/;
    
    # Новые заголовки для MinIO
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header Authorization "";
    
    # Улучшенные CORS заголовки
    add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization" always;
    
    # Правильная обработка preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin "*";
        add_header Access-Control-Allow-Methods "GET, HEAD, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization";
        return 204;
    }
}
```

### 4. Автоматическая настройка MinIO (`.github/workflows/deploy.yml`)
```bash
# Добавлен автоматический этап настройки MinIO после деплоя:
# 1. Установка MinIO Client
# 2. Создание bucket 'foodgram'
# 3. Настройка публичной политики для /media/*
# 4. Настройка CORS политик
```

### 5. Скрипт настройки (`scripts/deploy/setup_minio.sh`)
Создан универсальный скрипт для ручной настройки MinIO с:
- Установкой MinIO Client
- Созданием bucket
- Настройкой публичных политик
- Настройкой CORS

## Результат

### До исправления:
- ❌ Изображения не загружались (CORS ошибки)
- ❌ 404 ошибки при обращении к медиа файлам
- ❌ Неправильные URL в Django

### После исправления:
- ✅ Изображения загружаются через nginx proxy
- ✅ Правильные CORS заголовки
- ✅ Автоматическая настройка при деплое
- ✅ Публичный доступ к медиа файлам

## Архитектура

```
Браузер -> HTTPS (443) -> Nginx -> /media/ -> MinIO (9000) -> Bucket foodgram/media/
```

### Endpoints:
- **Веб-сайт**: `https://foodgram.freedynamicdns.net/`
- **Медиа файлы**: `https://foodgram.freedynamicdns.net/media/`
- **MinIO Console**: `https://foodgram.freedynamicdns.net/minio/`
- **API**: `https://foodgram.freedynamicdns.net/api/`

## Деплой
Все исправления применятся автоматически при следующем деплое через GitHub Actions:

1. Коммит изменений в main
2. GitHub Actions автоматически:
   - Запустит тесты
   - Задеплоит на продакшн
   - Настроит MinIO
   - Проверит работоспособность

## Проверка работы

После деплоя проверить:
1. Открыть любой рецепт - изображение должно загружаться
2. Загрузить аватар в профиле - должен отображаться
3. Проверить в DevTools отсутствие CORS ошибок
4. Убедиться что URL медиа файлов начинаются с `/media/` 