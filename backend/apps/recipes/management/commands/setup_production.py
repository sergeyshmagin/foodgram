"""Management команда для загрузки базовых данных в продакшн."""
from apps.recipes.models import Tag
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Команда для загрузки базовых данных в продакшн."""

    help = "Создаёт администратора и базовые теги для продакшна"

    def handle(self, *args, **options):
        """Основная логика команды."""
        self.stdout.write(
            self.style.SUCCESS("🚀 Настройка базовых данных для продакшна")
        )

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
            # Сначала проверяем по slug
            try:
                tag = Tag.objects.get(slug=tag_data["slug"])
                self.stdout.write(f"ℹ️ Тег уже существует: {tag.name}")

                # Обновляем поля если нужно
                updated = False
                if tag.name != tag_data["name"]:
                    tag.name = tag_data["name"]
                    updated = True
                if tag.color != tag_data["color"]:
                    tag.color = tag_data["color"]
                    updated = True
                if updated:
                    try:
                        tag.save()
                        self.stdout.write(f"🔄 Обновлён тег: {tag.name}")
                    except Exception as e:
                        self.stdout.write(
                            f"⚠️ Не удалось обновить тег {tag.name}: {e}"
                        )

            except Tag.DoesNotExist:
                # Проверяем по name, чтобы избежать дублирования
                existing_by_name = Tag.objects.filter(
                    name=tag_data["name"]
                ).first()
                if existing_by_name:
                    self.stdout.write(
                        f"ℹ️ Тег с именем '{tag_data['name']}' уже существует со slug '{existing_by_name.slug}'"
                    )
                    continue

                # Проверяем по color
                existing_by_color = Tag.objects.filter(
                    color=tag_data["color"]
                ).first()
                if existing_by_color:
                    self.stdout.write(
                        f"ℹ️ Тег с цветом '{tag_data['color']}' уже существует: {existing_by_color.name}"
                    )
                    continue

                # Если не найден ни по одному полю - создаём новый
                try:
                    tag = Tag.objects.create(**tag_data)
                    self.stdout.write(f"✅ Создан тег: {tag.name}")
                except Exception as e:
                    self.stdout.write(
                        f"⚠️ Не удалось создать тег '{tag_data['name']}': {e}"
                    )
