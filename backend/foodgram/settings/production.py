"""Production settings for Foodgram project."""
import os
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-in-production-immediately')

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '192.168.0.10',  # Production server IP
    'foodgram.local',
    os.environ.get('DOMAIN_NAME', ''),
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'foodgram'),
        'USER': os.environ.get('POSTGRES_USER', 'foodgram_user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'foodgram_password'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis configuration
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# MinIO configuration for file storage
MINIO_ENDPOINT = os.environ.get('MINIO_HOST', 'minio') + ':9000'
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'foodgram_minio')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', 'foodgram_minio_password')
MINIO_BUCKET_NAME = os.environ.get('MINIO_BUCKET_NAME', 'foodgram')
MINIO_USE_HTTPS = os.environ.get('MINIO_USE_HTTPS', 'False') == 'True'

# File storage settings
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'

# S3/MinIO settings
AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
AWS_S3_ENDPOINT_URL = f"http://{MINIO_ENDPOINT}"
AWS_S3_USE_SSL = MINIO_USE_HTTPS
AWS_S3_VERIFY = False
AWS_DEFAULT_ACL = None
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'us-east-1'

# Custom domain for file URLs (optional)
if os.environ.get('MINIO_EXTERNAL_ENDPOINT'):
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('MINIO_EXTERNAL_ENDPOINT')

# Media files configuration
MEDIA_URL = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET_NAME}/media/"
if os.environ.get('MINIO_EXTERNAL_ENDPOINT'):
    MEDIA_URL = f"http://{os.environ.get('MINIO_EXTERNAL_ENDPOINT')}/{MINIO_BUCKET_NAME}/media/"

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = '/app/staticfiles'

# Security settings for production
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False') == 'True'

# CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://localhost",
    "http://localhost:80", 
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    "http://127.0.0.1:3000",
    "http://192.168.0.10",
    "http://foodgram.local",
]

# Additional CORS settings for frontend integration
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email configuration (for production)
if os.environ.get('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@foodgram.ru')

# Celery settings
CELERY_BROKER_URL = (
    f"redis://{os.environ.get('REDIS_HOST', 'redis')}:"
    f"{os.environ.get('REDIS_PORT', '6379')}/0"
)
CELERY_RESULT_BACKEND = (
    f"redis://{os.environ.get('REDIS_HOST', 'redis')}:"
    f"{os.environ.get('REDIS_PORT', '6379')}/0"
) 