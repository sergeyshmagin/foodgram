"""Development settings for Foodgram project."""
import os
import sys

from .base import *  # noqa: F403, F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-dev-key-change-in-production"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0"
).split(",")

# Database for development - можно использовать SQLite или PostgreSQL
USE_SQLITE = os.environ.get("USE_SQLITE", "True") == "True"

if USE_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("POSTGRES_DB", "foodgram_dev"),
            "USER": os.environ.get("POSTGRES_USER", "foodgram_user"),
            "PASSWORD": os.environ.get(
                "POSTGRES_PASSWORD", "foodgram_password"
            ),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

# Development apps
# INSTALLED_APPS += [
#     'django_extensions',
# ]

# Email backend - файловая система для тестирования
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND", "django.core.mail.backends.filebased.EmailBackend"
)
EMAIL_FILE_PATH = os.environ.get(
    "EMAIL_FILE_PATH", str(BASE_DIR / "sent_emails")  # noqa: F405
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "admin@foodgram.ru")

# Создаем папку для писем если не существует
os.makedirs(EMAIL_FILE_PATH, exist_ok=True)

# Cache for development - можно использовать Redis или локальную память
USE_REDIS = os.environ.get("USE_REDIS", "False") == "True"

if USE_REDIS:
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
    REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
    REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

    if REDIS_PASSWORD:
        REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1"
    else:
        REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# MinIO configuration for development
# По умолчанию False для тестов в CI, можно включить локально
USE_MINIO = os.environ.get("USE_MINIO", "False") == "True"

# Отключаем MinIO при запуске тестов
if "pytest" in sys.modules or "test" in sys.argv:
    USE_MINIO = False

if USE_MINIO:
    # MinIO настройки для разработки
    MINIO_ENDPOINT = f"{os.environ.get('MINIO_HOST', 'localhost')}:9000"
    MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minio_access_key")
    MINIO_SECRET_KEY = os.environ.get(
        "MINIO_SECRET_KEY", "minio_secret_key_123"
    )
    MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME", "foodgram")
    MINIO_USE_HTTPS = os.environ.get("MINIO_USE_HTTPS", "False") == "True"

    # AWS S3 settings for MinIO
    AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
    AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
    AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = f"http://{MINIO_ENDPOINT}"
    AWS_S3_USE_SSL = MINIO_USE_HTTPS
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    AWS_LOCATION = "media"
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False

    # File storage settings
    DEFAULT_FILE_STORAGE = "foodgram.storage.MinIOMediaStorage"

    # ВАЖНО: MEDIA_URL для разработки (доступ через localhost:9000)
    MEDIA_URL = f"http://{MINIO_ENDPOINT}/foodgram/media/"
else:
    # Стандартное файловое хранилище для разработки
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_URL = "/media/"
