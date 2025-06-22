FROM python:3.9-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя для безопасности
RUN useradd --create-home --shell /bin/bash app

# Установка рабочей директории
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/production.txt

# Копирование кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p staticfiles media logs

# Создание entrypoint скрипта
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Ожидание готовности базы данных\n\
echo "Waiting for database..."\n\
while ! python manage.py check --database default; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
\n\
# Выполнение миграций\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Сбор статических файлов\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
# Создание бакета MinIO (если необходимо)\n\
echo "Setting up MinIO bucket..."\n\
python manage.py setup_minio || echo "MinIO setup failed, continuing..."\n\
\n\
# Запуск сервера\n\
echo "Starting server..."\n\
exec "$@"' > /app/entrypoint.sh

# Делаем entrypoint исполняемым
RUN chmod +x /app/entrypoint.sh

# Изменение владельца файлов
RUN chown -R app:app /app

# Переключение на непривилегированного пользователя
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Entrypoint и команда по умолчанию
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "foodgram.wsgi:application"]

EXPOSE 8000 