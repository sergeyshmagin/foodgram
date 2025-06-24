"""Management команда для загрузки базовых данных в продакшн."""
from apps.recipes.models import Tag
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

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

        # Сначала ищем по username, если не найден - создаём
        try:
            admin = User.objects.get(username="admin")
            created = False
            self.stdout.write("ℹ️ Администратор найден по username")
        except User.DoesNotExist:
            # Пробуем найти по email
            try:
                admin = User.objects.get(email="admin@foodgram.local")
                created = False
                self.stdout.write("ℹ️ Администратор найден по email")
            except User.DoesNotExist:
                # Создаём нового администратора
                admin = User.objects.create_user(
                    username="admin",
                    email="admin@foodgram.local",
                    first_name="Администратор",
                    last_name="Foodgram",
                )
                created = True
                self.stdout.write("✅ Администратор создан")

        # Всегда обновляем права и пароль для безопасности
        admin.email = "admin@foodgram.local"
        admin.first_name = "Администратор"
        admin.last_name = "Foodgram"
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password("admin123")
        admin.save()

        if not created:
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
            try:
                # Сначала пытаемся получить тег
                Tag.objects.get(slug=tag_data["slug"])
                self.stdout.write(f"ℹ️ Тег уже существует: {tag_data['name']}")
            except Tag.DoesNotExist:
                # Если тега нет, создаём новый
                try:
                    Tag.objects.create(**tag_data)
                    self.stdout.write(f"✅ Создан тег: {tag_data['name']}")
                except IntegrityError:
                    # На случай race condition - пытаемся получить ещё раз
                    try:
                        Tag.objects.get(slug=tag_data["slug"])
                        self.stdout.write(
                            f"ℹ️ Тег уже существует: {tag_data['name']}"
                        )
                    except Tag.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"⚠️ Не удалось создать тег: "
                                f"{tag_data['name']}"
                            )
                        )
