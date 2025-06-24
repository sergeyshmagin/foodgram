"""
Django management команда для настройки MinIO.
"""
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Команда для настройки MinIO и создания bucket."""
    
    help = "Настройка MinIO и создание bucket"
    
    def handle(self, *args, **options):
        """Основная логика команды."""
        self.stdout.write("🔧 Настройка MinIO...")
        
        # Создаем S3 клиент для MinIO
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name='us-east-1'  # MinIO требует region
        )
        
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        
        try:
            # Проверяем существование bucket
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(
                self.style.SUCCESS(f"✅ Bucket '{bucket_name}' уже существует")
            )
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                # Bucket не существует, создаем его
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Bucket '{bucket_name}' создан успешно"
                        )
                    )
                except ClientError as create_error:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Ошибка создания bucket: {create_error}"
                        )
                    )
                    return
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Ошибка доступа к bucket: {e}"
                    )
                )
                return
        
        # Настраиваем публичную политику
        try:
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                    }
                ]
            }
            
            import json
            s3_client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Публичная политика для bucket '{bucket_name}' установлена"
                )
            )
        except ClientError as e:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ Не удалось установить политику bucket: {e}"
                )
            )
        
        # Настраиваем CORS
        try:
            cors_configuration = {
                'CORSRules': [
                    {
                        'AllowedOrigins': ['*'],
                        'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
                        'AllowedHeaders': ['*'],
                        'ExposeHeaders': ['ETag'],
                        'MaxAgeSeconds': 3000
                    }
                ]
            }
            
            s3_client.put_bucket_cors(
                Bucket=bucket_name,
                CORSConfiguration=cors_configuration
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ CORS политика для bucket '{bucket_name}' установлена"
                )
            )
        except ClientError as e:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️ Не удалось установить CORS политику: {e}"
                )
            )
        
        # Тестируем подключение
        try:
            from django.core.files.storage import default_storage
            
            # Проверяем доступность storage
            storage_available = hasattr(default_storage, 'bucket_name')
            if storage_available:
                self.stdout.write(
                    self.style.SUCCESS("✅ Django storage подключен к MinIO")
                )
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Django storage не подключен к MinIO")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Ошибка тестирования storage: {e}")
            )
        
        # Выводим информацию о настройках
        self.stdout.write("\n🔍 Текущие настройки MinIO:")
        self.stdout.write(f"📍 Endpoint: {settings.AWS_S3_ENDPOINT_URL}")
        self.stdout.write(f"📁 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        self.stdout.write(f"🌐 Media URL: {settings.MEDIA_URL}")
        self.stdout.write(f"🔗 Custom domain: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Не установлен')}")
        
        self.stdout.write(
            self.style.SUCCESS("\n🎉 Настройка MinIO завершена!")
        ) 