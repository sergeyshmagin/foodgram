"""Утилиты для API приложения."""
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum

from apps.recipes.models import IngredientInRecipe


def generate_shopping_list(user):
    """Генерирует текст списка покупок для пользователя."""
    # Получаем агрегированный список ингредиентов из корзины покупок
    ingredients = (
        IngredientInRecipe.objects.filter(recipe__shoppingcart_set__user=user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(total_amount=Sum("amount"))
        .order_by("ingredient__name")
    )

    # Формируем текст файла
    shopping_list = ["Список покупок от Foodgram:", ""]
    if not ingredients.exists():
        shopping_list.append(
            "Ваша корзина пуста.\n"
            "Добавьте рецепты в корзину, чтобы создать список покупок.\n"
        )
    else:
        for ingredient in ingredients:
            shopping_list.append(
                f"• {ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['total_amount']}"
            )

    shopping_list.extend(
        ["", "Приятного аппетита!", "", "---", "Создано с помощью Foodgram"]
    )

    return "\n".join(shopping_list)


def send_recipe_notification(user_email, recipe_title):
    """
    Отправляет уведомление о новом рецепте подписанным пользователям.

    Args:
        user_email: Email получателя
        recipe_title: Название рецепта
    """
    subject = "Новый рецепт от автора, на которого вы подписаны!"
    message = f"Был добавлен новый рецепт: {recipe_title}"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )
