"""Management команда для создания суперпользователя."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Команда для создания суперпользователя."""

    help = "Создает суперпользователя"

    def handle(self, *args, **options):
        """Основная логика команды."""
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(
                self.style.WARNING("Суперпользователь уже существует!")
            )
            return

        admin = User.objects.create_superuser(
            username="admin",
            email="admin@foodgram.ru",
            password="admin123",
            first_name="Admin",
            last_name="User",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Суперпользователь создан: {admin.username} ({admin.email})"
            )
        )
