# Generated by Django 3.2.16 on 2025-06-27 12:40

import apps.users.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_move_subscription_model"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                default="",
                help_text="Загрузите аватар пользователя",
                upload_to="avatars/",
                verbose_name="Аватар",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                help_text="Обязательное поле. Максимум 254 символов.",
                max_length=254,
                unique=True,
                verbose_name="Email",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                help_text="Обязательное поле. Максимум 150 символов. Только буквы, цифры и @/./+/-/_",
                max_length=150,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        message="Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_",
                        regex="^[\\w.@+-]+$",
                    ),
                    apps.users.models.validate_not_me,
                ],
                verbose_name="Имя пользователя",
            ),
        ),
    ]
