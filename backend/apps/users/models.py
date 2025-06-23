"""User models for Foodgram project."""
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from foodgram.constants import (MAX_EMAIL_LENGTH, MAX_FIRST_NAME_LENGTH,
                                MAX_LAST_NAME_LENGTH, MAX_USERNAME_LENGTH)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    email = models.EmailField(
        "Email",
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        help_text="Обязательное поле. Максимум 254 символа.",
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
            )
        ],
        help_text=(
            "Обязательное поле. Максимум 150 символов. "
            "Только буквы, цифры и @/./+/-/_"
        ),
    )
    first_name = models.CharField(
        "Имя",
        max_length=MAX_FIRST_NAME_LENGTH,
        help_text="Обязательное поле. Максимум 150 символов.",
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=MAX_LAST_NAME_LENGTH,
        help_text="Обязательное поле. Максимум 150 символов.",
    )
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
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
