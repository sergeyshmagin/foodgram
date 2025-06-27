"""Тесты для команд управления администраторами."""
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError

User = get_user_model()


@pytest.mark.django_db
class TestCreateAdminSafeCommand:
    """Тесты для команды create_admin_safe."""

    def test_create_admin_with_args(self):
        """Тест создания админа через аргументы."""
        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "admin@test.com",
            "--password",
            "StrongPassword123!",
            "--username",
            "testadmin",
            stdout=out,
        )

        # Проверяем, что пользователь создан
        user = User.objects.get(email="admin@test.com")
        assert user.is_superuser
        assert user.is_staff
        assert user.username == "testadmin"
        assert user.check_password("StrongPassword123!")
        assert "успешно создан" in out.getvalue()

    def test_create_admin_with_env_vars(self, monkeypatch):
        """Тест создания админа через переменные окружения."""
        # Устанавливаем переменные окружения
        monkeypatch.setenv("ADMIN_EMAIL", "env@test.com")
        monkeypatch.setenv("ADMIN_PASSWORD", "EnvPassword123!")
        monkeypatch.setenv("ADMIN_USERNAME", "envadmin")

        out = StringIO()
        call_command("create_admin_safe", stdout=out)

        # Проверяем, что пользователь создан
        user = User.objects.get(email="env@test.com")
        assert user.is_superuser
        assert user.is_staff
        assert user.username == "envadmin"
        assert user.check_password("EnvPassword123!")

    def test_admin_already_exists(self):
        """Тест когда админ уже существует."""
        # Создаем пользователя
        User.objects.create_superuser(
            email="existing@test.com",
            username="existing",
            password="OldPassword123!",
        )

        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "existing@test.com",
            "--password",
            "NewPassword123!",
            stdout=out,
        )

        # Проверяем, что пользователь не изменился
        user = User.objects.get(email="existing@test.com")
        assert user.check_password("OldPassword123!")  # Старый пароль
        assert "уже существует" in out.getvalue()

    def test_update_existing_admin_with_force(self):
        """Тест обновления существующего админа с флагом --force."""
        # Создаем пользователя
        User.objects.create_superuser(
            email="update@test.com",
            username="old_username",
            password="OldPassword123!",
        )

        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "update@test.com",
            "--password",
            "NewPassword123!",
            "--username",
            "new_username",
            "--force",
            stdout=out,
        )

        # Проверяем, что пользователь обновился
        user = User.objects.get(email="update@test.com")
        assert user.check_password("NewPassword123!")  # Новый пароль
        assert user.username == "new_username"  # Новое имя
        assert "успешно обновлен" in out.getvalue()

    def test_missing_email(self):
        """Тест ошибки при отсутствии email."""
        with pytest.raises(CommandError) as exc_info:
            call_command(
                "create_admin_safe", "--password", "StrongPassword123!"
            )
        assert "Email обязателен" in str(exc_info.value)

    def test_missing_password(self):
        """Тест ошибки при отсутствии пароля."""
        with pytest.raises(CommandError) as exc_info:
            call_command("create_admin_safe", "--email", "admin@test.com")
        assert "Пароль обязателен" in str(exc_info.value)

    def test_short_password_warning(self):
        """Тест предупреждения о коротком пароле."""
        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "short@test.com",
            "--password",
            "short1",
            "--username",
            "shortpass",
            stdout=out,
        )

        # Проверяем предупреждение
        output = out.getvalue()
        assert "Пароль слишком короткий" in output

    def test_weak_password_warnings(self):
        """Тест предупреждений о слабом пароле."""
        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "weak@test.com",
            "--password",
            "admin123",  # Слабый пароль
            "--username",
            "weakpass",
            stdout=out,
        )

        # Проверяем предупреждения о безопасности
        output = out.getvalue()
        assert "Рекомендации по безопасности" in output

    def test_strong_password_no_warnings(self):
        """Тест что сильный пароль не вызывает предупреждений."""
        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "strong@test.com",
            "--password",
            "VeryStrongP@ssw0rd123!",
            "--username",
            "strongpass",
            stdout=out,
        )

        # Проверяем отсутствие предупреждений
        output = out.getvalue()
        assert "Рекомендации по безопасности" not in output
        assert "успешно создан" in output

    def test_default_username_from_email(self):
        """Тест автоматического создания username из email."""
        out = StringIO()
        call_command(
            "create_admin_safe",
            "--email",
            "testuser@example.com",
            "--password",
            "StrongPassword123!",
            stdout=out,
        )

        # Проверяем, что username создался из email
        user = User.objects.get(email="testuser@example.com")
        assert user.username == "testuser"

    def test_creation_error_handling(self, monkeypatch):
        """Тест обработки ошибок при создании пользователя."""

        # Мокаем User.objects.create_superuser чтобы вызвать исключение
        def mock_create_superuser(*args, **kwargs):
            raise Exception("Database error")

        monkeypatch.setattr(
            "django.contrib.auth.models.UserManager.create_superuser",
            mock_create_superuser,
        )

        with pytest.raises(CommandError) as exc_info:
            call_command(
                "create_admin_safe",
                "--email",
                "error@test.com",
                "--password",
                "StrongPassword123!",
            )
        assert "Ошибка при создании суперпользователя" in str(exc_info.value)
