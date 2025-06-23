"""Management команда для загрузки демонстрационных данных."""
import random
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

try:
    from PIL import Image
except ImportError:
    Image = None

from apps.recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingCart,
    Subscription,
    Tag,
)

User = get_user_model()


class Command(BaseCommand):
    """Команда для загрузки демонстрационных данных."""

    help = "Загружает демонстрационные данные с рецептами и пользователями"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить все данные перед загрузкой",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("🚀 Загрузка демонстрационных данных")
        )

        if options["clear"]:
            self.clear_data()

        with transaction.atomic():
            self.create_admin()
            self.create_tags()
            self.create_users()
            self.create_ingredients()
            self.create_recipes()
            self.create_interactions()

        self.print_summary()

    def clear_data(self):
        """Очищает все данные."""
        self.stdout.write("🧹 Очистка данных...")
        Subscription.objects.all().delete()
        ShoppingCart.objects.all().delete()
        Favorite.objects.all().delete()
        IngredientInRecipe.objects.all().delete()
        Recipe.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.all().delete()

    def create_admin(self):
        """Создает администратора."""
        self.stdout.write("👤 Создание администратора...")

        admin, created = User.objects.get_or_create(
            email="admin@foodgram.ru",
            defaults={
                "username": "admin",
                "first_name": "Администратор",
                "last_name": "Foodgram",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("✅ Администратор создан")
        else:
            self.stdout.write("ℹ️ Администратор уже существует")

    def create_tags(self):
        """Создает теги."""
        self.stdout.write("🏷️ Создание тегов...")

        tags_data = [
            {"name": "Завтрак", "color": "#E26C2D", "slug": "breakfast"},
            {"name": "Обед", "color": "#49B64E", "slug": "lunch"},
            {"name": "Ужин", "color": "#8775D2", "slug": "dinner"},
            {"name": "Десерт", "color": "#F44336", "slug": "dessert"},
            {"name": "Быстро", "color": "#FF9800", "slug": "fast"},
            {"name": "Здоровое", "color": "#4CAF50", "slug": "healthy"},
        ]

        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data["slug"], defaults=tag_data
            )
            status = "✅" if created else "ℹ️"
            self.stdout.write(f"{status} {tag.name}")

    def create_users(self):
        """Создает тестовых пользователей."""
        self.stdout.write("👥 Создание пользователей...")

        users_data = [
            {
                "email": "chef@foodgram.ru",
                "username": "chef_master",
                "first_name": "Шеф",
                "last_name": "Поваров",
            },
            {
                "email": "maria@foodgram.ru",
                "username": "maria_cook",
                "first_name": "Мария",
                "last_name": "Кулинарова",
            },
            {
                "email": "test@foodgram.ru",
                "username": "testuser",
                "first_name": "Тест",
                "last_name": "Пользователь",
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"], defaults=user_data
            )
            if created:
                user.set_password("testpass123")
                user.save()
                self.stdout.write(f"✅ {user.username}")

    def create_ingredients(self):
        """Проверяет наличие базовых ингредиентов для рецептов."""
        self.stdout.write("🥕 Проверка ингредиентов для рецептов...")

        # Основные ингредиенты для демо-рецептов
        required_ingredients = [
            ("мука пшеничная", "г"),
            ("сахар", "г"),
            ("яйца куриные", "шт"),
            ("молоко", "мл"),
            ("масло сливочное", "г"),
            ("соль", "г"),
            ("помидоры", "шт"),
            ("лук репчатый", "шт"),
            ("морковь", "шт"),
            ("картофель", "шт"),
            ("говядина", "г"),
            ("курица", "г"),
        ]

        for name, unit in required_ingredients:
            ingredient, created = Ingredient.objects.get_or_create(
                name=name, measurement_unit=unit
            )
            status = "✅" if created else "ℹ️"
            self.stdout.write(f"{status} {name}")

        total_count = Ingredient.objects.count()
        self.stdout.write(f"📊 Всего ингредиентов в базе: {total_count}")

    def create_recipes(self):
        """Создает тестовые рецепты."""
        self.stdout.write("🍳 Создание рецептов...")

        users = list(User.objects.filter(is_superuser=False))
        tags = list(Tag.objects.all())

        if not users:
            self.stdout.write("⚠️ Нет пользователей для создания рецептов")
            return

        recipes_data = [
            {
                "name": "Классические блинчики",
                "text": (
                    "Традиционные русские блинчики на молоке. "
                    "Идеальный завтрак для всей семьи."
                ),
                "cooking_time": 30,
                "tags": ["breakfast"],
                "ingredients": [
                    ("Мука пшеничная", 200),
                    ("Молоко", 500),
                    ("Яйца куриные", 2),
                    ("Сахар", 50),
                ],
            },
            {
                "name": "Борщ украинский",
                "text": (
                    "Наваристый борщ с говядиной и овощами. "
                    "Классический рецепт с богатым вкусом."
                ),
                "cooking_time": 120,
                "tags": ["lunch", "healthy"],
                "ingredients": [
                    ("Говядина", 500),
                    ("Картофель", 3),
                    ("Морковь", 2),
                    ("Лук репчатый", 1),
                    ("Помидоры", 2),
                ],
            },
            {
                "name": "Куриные котлеты",
                "text": (
                    "Сочные куриные котлеты с луком. "
                    "Прекрасное блюдо для семейного обеда."
                ),
                "cooking_time": 45,
                "tags": ["lunch", "dinner"],
                "ingredients": [
                    ("Курица", 500),
                    ("Лук репчатый", 1),
                    ("Яйца куриные", 1),
                    ("Мука пшеничная", 50),
                ],
            },
        ]

        for recipe_data in recipes_data:
            author = random.choice(users)

            recipe, created = Recipe.objects.get_or_create(
                name=recipe_data["name"],
                defaults={
                    "author": author,
                    "text": recipe_data["text"],
                    "cooking_time": recipe_data["cooking_time"],
                    "image": self.create_recipe_image(recipe_data["name"]),
                },
            )

            if created:
                # Добавляем теги
                recipe_tags = [
                    tag for tag in tags if tag.slug in recipe_data["tags"]
                ]
                recipe.tags.set(recipe_tags)

                # Добавляем ингредиенты
                for ingredient_name, amount in recipe_data["ingredients"]:
                    try:
                        # Ищем ингредиент по точному имени или похожему
                        ingredient = Ingredient.objects.filter(
                            name__iexact=ingredient_name
                        ).first()

                        if not ingredient:
                            # Если не нашли, ищем по частичному совпадению
                            ingredient = Ingredient.objects.filter(
                                name__icontains=ingredient_name.lower()
                            ).first()

                        if ingredient:
                            IngredientInRecipe.objects.create(
                                recipe=recipe,
                                ingredient=ingredient,
                                amount=amount,
                            )
                        else:
                            self.stdout.write(
                                f"⚠️ Ингредиент '{ingredient_name}' не найден"
                            )
                    except Exception as e:
                        self.stdout.write(
                            f"❌ Ошибка добавления ингредиента: {e}"
                        )

                self.stdout.write(f"✅ {recipe.name}")

    def create_recipe_image(self, recipe_name):
        """Создает простое изображение для рецепта."""
        try:
            if Image is None:
                return None

            # Создаем простое изображение-заглушку
            img = Image.new("RGB", (300, 200), color="lightgray")

            # Сохраняем в BytesIO
            img_io = BytesIO()
            img.save(img_io, format="JPEG")
            img_io.seek(0)

            # Создаем Django File
            safe_name = recipe_name.lower().replace(" ", "_")[:20]
            filename = f"recipe_{safe_name}.jpg"
            return ContentFile(img_io.getvalue(), name=filename)
        except Exception as e:
            self.stdout.write(
                f"⚠️ Ошибка создания изображения для {recipe_name}: {e}"
            )
            return None

    def create_interactions(self):
        """Создает взаимодействия: подписки, избранное."""
        self.stdout.write("❤️ Создание взаимодействий...")

        users = list(User.objects.filter(is_superuser=False))
        recipes = list(Recipe.objects.all())

        if len(users) < 2 or not recipes:
            self.stdout.write("⚠️ Недостаточно данных")
            return

        interactions_count = 0

        # Создаем подписки
        for user in users[:2]:
            for author in users[-1:]:
                if user != author:
                    _, created = Subscription.objects.get_or_create(
                        user=user, author=author
                    )
                    if created:
                        interactions_count += 1

        # Добавляем рецепты в избранное
        for user in users:
            favorite_recipes = random.sample(recipes, min(2, len(recipes)))
            for recipe in favorite_recipes:
                _, created = Favorite.objects.get_or_create(
                    user=user, recipe=recipe
                )
                if created:
                    interactions_count += 1

        self.stdout.write(f"✅ Создано {interactions_count} взаимодействий")

    def print_summary(self):
        """Выводит сводку по созданным данным."""
        self.stdout.write("\n📊 Сводка:")
        self.stdout.write(f"👤 Пользователи: {User.objects.count()}")
        self.stdout.write(f"🏷️ Теги: {Tag.objects.count()}")
        self.stdout.write(f"🥕 Ингредиенты: {Ingredient.objects.count()}")
        self.stdout.write(f"🍳 Рецепты: {Recipe.objects.count()}")
        self.stdout.write(f"❤️ Избранное: {Favorite.objects.count()}")
        self.stdout.write(f"👥 Подписки: {Subscription.objects.count()}")

        self.stdout.write("\n🔑 Доступ:")
        self.stdout.write("👨‍💻 Админ: admin@foodgram.ru / admin123")
        self.stdout.write("👤 Тест: test@foodgram.ru / testpass123")
