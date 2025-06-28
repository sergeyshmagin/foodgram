"""Custom storage backends for Django."""
import os

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class MinIOMediaStorage(S3Boto3Storage):
    """Кастомное хранилище для медиа файлов в MinIO."""

    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = settings.AWS_LOCATION
    file_overwrite = settings.AWS_S3_FILE_OVERWRITE
    default_acl = settings.AWS_DEFAULT_ACL
    querystring_auth = settings.AWS_QUERYSTRING_AUTH

    def __init__(self, *args, **kwargs):
        # Для загрузки файлов используем внутренний endpoint
        self.endpoint_url = settings.AWS_S3_ENDPOINT_URL
        super().__init__(*args, **kwargs)

    def url(self, name):
        """
        Возвращает публичный URL для файла.
        Автоматически определяет окружение (development/production).
        """
        # Убираем префикс 'media/' если он есть в имени
        if name.startswith("media/"):
            name = name[6:]

        # Определяем окружение
        is_development = getattr(settings, "DEBUG", False)

        if is_development:
            # Development: прямой доступ к MinIO
            minio_host = os.environ.get("MINIO_HOST", "localhost")
            return f"http://{minio_host}:9000/foodgram/media/{name}"
        else:
            # Production: через nginx proxy с публичным доменом
            domain = os.environ.get(
                "DOMAIN_NAME", "foodgram.freedynamicdns.net"
            )
            return f"https://{domain}/media/{name}"
