"""Management команда для полной настройки Foodgram с тестовыми данными."""
import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings

from apps.recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class Command(BaseCommand):
    """Команда для полной настройки Foodgram."""

    help = "Создает администратора и загружает тестовые данные"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить все данные"
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Настройка Foodgram")
        )

        if options["clear"]:
            self.clear_data()

        with transaction.atomic():
            self.create_admin()
            self.create_tags()
            self.create_users()
            self.create_ingredients()
            self.setup_minio()
            self.create_recipes()

        self.print_summary()

    def clear_data(self):
        """Очистка данных."""
        self.stdout.write("🧹 Очистка данных...")
        Recipe.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.all().delete()

    def create_admin(self):
        """Создание администратора."""
        self.stdout.write("👤 Создание администратора...")

        admin, created = User.objects.get_or_create(
            email="admin@foodgram.ru",
            defaults={
                "username": "admin",
                "first_name": "Администратор",
                "last_name": "Foodgram",
                "is_staff": True,
                "is_superuser": True,
            }
        )

        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("✅ Администратор создан")
        else:
            self.stdout.write("ℹ️ Администратор уже существует")

    def create_tags(self):
        """Создание тегов."""
        self.stdout.write("🏷️ Создание тегов...")

        tags_data = [
            {"name": "Завтрак", "color": "#E26C2D", "slug": "breakfast"},
            {"name": "Обед", "color": "#49B64E", "slug": "lunch"},
            {"name": "Ужин", "color": "#8775D2", "slug": "dinner"},
            {"name": "Десерт", "color": "#F44336", "slug": "dessert"},
        ]

        for tag_data in tags_data:
            Tag.objects.get_or_create(
                slug=tag_data["slug"],
                defaults=tag_data
            )
            self.stdout.write(f"✅ {tag_data['name']}")

    def create_users(self):
        """Создание пользователей."""
        self.stdout.write("👥 Создание пользователей...")

        users_data = [
            {
                "email": "chef@foodgram.ru",
                "username": "chef_master",
                "first_name": "Шеф",
                "last_name": "Поваров",
            },
            {
                "email": "test@foodgram.ru",
                "username": "testuser",
                "first_name": "Тест",
                "last_name": "Пользователь",
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults=user_data
            )
            if created:
                user.set_password("testpass123")
                user.save()
                self.stdout.write(f"✅ {user.username}")

    def create_ingredients(self):
        """Создание ингредиентов."""
        self.stdout.write("🥕 Создание ингредиентов...")

        ingredients = [
            ("Мука", "г"), ("Сахар", "г"), ("Яйца", "шт"),
            ("Молоко", "мл"), ("Масло", "г"), ("Соль", "г")
        ]

        for name, unit in ingredients:
            Ingredient.objects.get_or_create(
                name=name, measurement_unit=unit
            )

    def setup_minio(self):
        """Настройка MinIO bucket."""
        self.stdout.write("🗂️ Настройка MinIO...")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Получаем настройки из settings
            minio_config = getattr(settings, 'AWS_S3_ENDPOINT_URL', None)
            access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
            secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
            bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'foodgram-static')
            
            if not all([minio_config, access_key, secret_key]):
                self.stdout.write("⚠️ MinIO настройки не найдены, пропускаем")
                return
            
            # Создаем клиент S3 для MinIO
            s3_client = boto3.client(
                's3',
                endpoint_url=minio_config,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                region_name='us-east-1'
            )
            
            # Проверяем существует ли bucket
            try:
                s3_client.head_bucket(Bucket=bucket_name)
                self.stdout.write(f"✅ Bucket {bucket_name} уже существует")
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    # Bucket не существует, создаем его
                    try:
                        s3_client.create_bucket(Bucket=bucket_name)
                        self.stdout.write(f"✅ Bucket {bucket_name} создан")
                    except ClientError as create_error:
                        self.stdout.write(f"❌ Ошибка создания bucket: {create_error}")
                else:
                    self.stdout.write(f"❌ Ошибка проверки bucket: {e}")
                    
        except ImportError:
            self.stdout.write("⚠️ boto3 не установлен, пропускаем настройку MinIO")
        except Exception as e:
            self.stdout.write(f"⚠️ Ошибка настройки MinIO: {e}")

    def create_recipes(self):
        """Создание рецептов."""
        self.stdout.write("🍳 Создание рецептов...")

        users = User.objects.filter(is_superuser=False)
        tags = Tag.objects.all()

        if not users.exists():
            return

        recipes_data = [
            {
                "name": "Блинчики",
                "text": "Вкусные блинчики на завтрак",
                "cooking_time": 30,
                "tag_slug": "breakfast"
            },
            {
                "name": "Борщ",
                "text": "Традиционный борщ",
                "cooking_time": 120,
                "tag_slug": "lunch"
            }
        ]

        for recipe_data in recipes_data:
            author = random.choice(list(users))

            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data["name"],
                defaults={
                    "author": author,
                    "text": recipe_data["text"],
                    "cooking_time": recipe_data["cooking_time"],
                }
            )

            if created:
                # Добавляем тег
                tag = tags.filter(slug=recipe_data["tag_slug"]).first()
                if tag:
                    recipe.tags.add(tag)

                self.stdout.write(f"✅ {recipe.name}")

    def print_summary(self):
        """Вывод сводки."""
        self.stdout.write("\n📊 Результат:")
        self.stdout.write(f"👤 Пользователи: {User.objects.count()}")
        self.stdout.write(f"🏷️ Теги: {Tag.objects.count()}")
        self.stdout.write(f"🥕 Ингредиенты: {Ingredient.objects.count()}")
        self.stdout.write(f"🍳 Рецепты: {Recipe.objects.count()}")

        self.stdout.write("\n🔑 Доступ:")
        self.stdout.write("Админ: admin@foodgram.ru / admin123")
        self.stdout.write("Тест: test@foodgram.ru / testpass123")
