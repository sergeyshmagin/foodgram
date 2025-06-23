"""Management команда для загрузки базовых данных в продакшн."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.recipes.models import Tag

User = get_user_model()


class Command(BaseCommand):
    """Команда для загрузки базовых данных в продакшн."""

    help = "Создаёт администратора и базовые теги для продакшна"

    def handle(self, *args, **options):
        """Основная логика команды."""
        self.stdout.write(
            self.style.SUCCESS("🚀 Настройка базовых данных для продакшна")
        )

        with transaction.atomic():
            self._create_admin()
            self._create_tags()

        self.stdout.write(
            self.style.SUCCESS("✅ Базовые данные успешно загружены!")
        )

    def _create_admin(self):
        """Создание администратора."""
        self.stdout.write("👤 Создание администратора...")

        admin, created = User.objects.get_or_create(
            email="admin@foodgram.local",
            defaults={
                "username": "admin",
                "first_name": "Администратор",
                "last_name": "Foodgram",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        # Всегда обновляем пароль для безопасности
        admin.set_password("admin123")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        if created:
            self.stdout.write("✅ Администратор создан")
        else:
            self.stdout.write("✅ Администратор обновлён")

    def _create_tags(self):
        """Создание базовых тегов."""
        self.stdout.write("🏷️ Создание тегов...")

        tags_data = [
            {"name": "Завтрак", "color": "#E26C2D", "slug": "zavtrak"},
            {"name": "Обед", "color": "#49B64E", "slug": "obed"},
            {"name": "Ужин", "color": "#8775D2", "slug": "uzhin"},
            {"name": "Десерт", "color": "#F46EBD", "slug": "desert"},
        ]

        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data["slug"], defaults=tag_data
            )
            if created:
                self.stdout.write(f"✅ Создан тег: {tag_data['name']}")
            else:
                self.stdout.write(f"ℹ️ Тег уже существует: {tag_data['name']}") 