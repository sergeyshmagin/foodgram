"""
Безопасная команда для создания суперпользователя в продакшене.
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Команда для безопасного создания суперпользователя."""

    help = "Создает суперпользователя с использованием переменных окружения"

    def add_arguments(self, parser):
        """Добавляет аргументы команды."""
        parser.add_argument(
            "--email",
            type=str,
            help=(
                "Email суперпользователя " "(можно задать через ADMIN_EMAIL)"
            ),
        )
        parser.add_argument(
            "--password",
            type=str,
            help=(
                "Пароль суперпользователя "
                "(можно задать через ADMIN_PASSWORD)"
            ),
        )
        parser.add_argument(
            "--username",
            type=str,
            help=("Имя пользователя " "(можно задать через ADMIN_USERNAME)"),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Перезаписать существующего пользователя",
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        User = get_user_model()

        # Получаем данные из аргументов или переменных окружения
        email = options.get("email") or os.getenv("ADMIN_EMAIL")
        password = options.get("password") or os.getenv("ADMIN_PASSWORD")
        username = options.get("username") or os.getenv("ADMIN_USERNAME")
        force = options.get("force", False)

        # Валидация обязательных полей
        if not email:
            raise CommandError(
                "Email обязателен. Укажите --email или установите "
                "переменную окружения ADMIN_EMAIL"
            )

        if not password:
            raise CommandError(
                "Пароль обязателен. Укажите --password или установите "
                "переменную окружения ADMIN_PASSWORD"
            )

        # Устанавливаем username по умолчанию
        if not username:
            username = email.split("@")[0]

        # Проверяем минимальную длину пароля
        if len(password) < 8:
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Пароль слишком короткий. "
                    "Рекомендуется минимум 8 символов."
                )
            )

        # Проверяем существование пользователя
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if not force:
                self.stdout.write(
                    self.style.WARNING(
                        f"✅ Суперпользователь с email {email} уже существует. "
                        f"Используйте --force для перезаписи."
                    )
                )
                return
            else:
                # Обновляем существующего пользователя
                existing_user.set_password(password)
                existing_user.is_staff = True
                existing_user.is_superuser = True
                existing_user.username = username
                existing_user.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ Суперпользователь {email} успешно обновлен!"
                    )
                )
                return

        try:
            # Создаем нового суперпользователя
            User.objects.create_superuser(
                email=email,
                username=username,
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Суперпользователь {email} успешно создан!"
                )
            )

        except Exception as e:
            raise CommandError(f"❌ Ошибка при создании суперпользователя: {e}")

        # Проверка безопасности пароля
        self._check_password_security(password)

    def _check_password_security(self, password):
        """Проверяет безопасность пароля и выводит рекомендации."""
        warnings = []

        if len(password) < 12:
            warnings.append("Пароль короче 12 символов")

        if password.lower() in ["admin", "password", "123456", "admin123"]:
            warnings.append("Пароль слишком простой")

        if not any(c.isupper() for c in password):
            warnings.append("Нет заглавных букв")

        if not any(c.islower() for c in password):
            warnings.append("Нет строчных букв")

        if not any(c.isdigit() for c in password):
            warnings.append("Нет цифр")

        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            warnings.append("Нет специальных символов")

        if warnings:
            self.stdout.write(
                self.style.WARNING("⚠️  Рекомендации по безопасности пароля:")
            )
            for warning in warnings:
                self.stdout.write(f"   - {warning}")
            self.stdout.write("💡 Используйте сложный пароль для продакшена!")
