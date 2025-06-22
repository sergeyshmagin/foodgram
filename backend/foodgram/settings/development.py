"""Development settings for Foodgram project."""
import os
from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-dev-key-change-in-production'
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development apps
# INSTALLED_APPS += [
#     'django_extensions',
# ]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache for development (можно использовать Redis или локальную память)
USE_REDIS = os.environ.get('USE_REDIS', 'False') == 'True'

if USE_REDIS:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': (
                f"redis://{os.environ.get('REDIS_HOST', 'redis')}:"
                f"{os.environ.get('REDIS_PORT', '6379')}/1"
            ),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True 