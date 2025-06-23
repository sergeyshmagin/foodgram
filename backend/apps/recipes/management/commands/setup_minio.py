"""Management command for setting up MinIO bucket."""
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Command to setup MinIO bucket for file storage."""

    help = "Setup MinIO bucket for file storage"

    def handle(self, *args, **options):
        """Handle the command execution."""
        try:
            # Создаем клиент S3 для MinIO
            s3_client = boto3.client(
                "s3",
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
            )

            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # Проверяем существование бакета
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Bucket "{bucket_name}" already exists'
                    )
                )
            except ClientError as e:
                error_code = e.response["Error"]["Code"]

                if error_code == "404":
                    # Бакет не существует, создаем его
                    try:
                        s3_client.create_bucket(Bucket=bucket_name)
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Successfully created bucket "{bucket_name}"'
                            )
                        )
                    except ClientError as create_error:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Failed to create bucket: {create_error}"
                            )
                        )
                        raise
                else:
                    self.stdout.write(
                        self.style.ERROR(f"Error accessing bucket: {e}")
                    )
                    raise

            # Устанавливаем политику доступа для публичного чтения изображений
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/media/*",
                    }
                ],
            }

            try:
                import json

                s3_client.put_bucket_policy(
                    Bucket=bucket_name, Policy=json.dumps(bucket_policy)
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        "Successfully set bucket policy for public "
                        "media access"
                    )
                )
            except ClientError as policy_error:
                self.stdout.write(
                    self.style.WARNING(
                        f"Failed to set bucket policy: {policy_error}"
                    )
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"MinIO setup failed: {e}"))
            # Не поднимаем исключение, чтобы не прерывать запуск приложения
            return

        self.stdout.write(
            self.style.SUCCESS("MinIO setup completed successfully!")
        )
