"""User models for Foodgram project."""

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from foodgram.constants import (
    MAX_EMAIL_LENGTH,
    MAX_FIRST_NAME_LENGTH,
    MAX_LAST_NAME_LENGTH,
    MAX_USERNAME_LENGTH,
)


def validate_not_me(value):
    """Валидатор, запрещающий использование username='me'."""
    if value.lower() == "me":
        raise ValidationError(
            'Имя пользователя "me" зарезервировано и не может '
            "быть использовано."
        )


class TimeStampedModel(models.Model):
    """Абстрактная модель с полем даты создания."""

    created = models.DateTimeField(
        "Дата создания", auto_now_add=True, help_text="Дата создания записи"
    )

    class Meta:
        abstract = True


class User(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    email = models.EmailField(
        "Электронная почта",
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        help_text="Электронная почта пользователя",
    )
    username = models.CharField(
        "Имя пользователя",
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[\w.@+-]+$",
                message=(
                    "Имя пользователя может содержать только "
                    "буквы, цифры и символы @/./+/-/_"
                ),
            ),
            validate_not_me,
        ],
        help_text=(
            f"Обязательное поле. Максимум {MAX_USERNAME_LENGTH} символов. "
            "Только буквы, цифры и @/./+/-/_"
        ),
    )
    first_name = models.CharField(
        "Имя",
        max_length=MAX_FIRST_NAME_LENGTH,
        help_text=(
            f"Обязательное поле. Максимум {MAX_FIRST_NAME_LENGTH} символов."
        ),
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=MAX_LAST_NAME_LENGTH,
        help_text=(
            f"Обязательное поле. Максимум {MAX_LAST_NAME_LENGTH} символов."
        ),
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        default="",
        help_text="Загрузите аватар пользователя",
    )

    class Meta:
        """Метаданные модели User."""

        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        """Строковое представление пользователя."""
        return self.username

    def validate_username(self):
        """Проверяет, что username не равен 'me' или 'ME'."""
        if self.username.lower() == "me":
            raise ValidationError(
                "Нельзя использовать 'me' в качестве имени пользователя."
            )


class Subscription(TimeStampedModel):
    """Модель подписок на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        """Метаданные модели Subscription."""

        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        ordering = ["-created"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_user_author_subscription",
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="prevent_self_subscription",
            ),
        ]

    def __str__(self):
        """Строковое представление подписки."""
        return f"{self.user.username} подписан на {self.author.username}"
