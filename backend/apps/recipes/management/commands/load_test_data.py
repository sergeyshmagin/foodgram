"""Management команда для загрузки полных тестовых данных."""
import os
import random
from io import BytesIO

import requests
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image

from apps.recipes.models import (Ingredient, IngredientInRecipe, Recipe, Tag,
                                 Favorite, ShoppingCart, Subscription)

User = get_user_model()


class Command(BaseCommand):
    """Команда для загрузки комплексных тестовых данных."""

    help = "Загружает полные тестовые данные: админ, пользователи, теги, рецепты"

    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Очистить все данные перед загрузкой",
        )
        parser.add_argument(
            "--admin-only",
            action="store_true",
            help="Создать только администратора",
        )

    def handle(self, *args, **options):
        """Основная логика команды."""
        self.stdout.write(
            self.style.SUCCESS("🚀 Загрузка тестовых данных для Foodgram")
        )

        if options["clear"]:
            self.clear_data()

        if options["admin_only"]:
            self.create_admin()
            return

        with transaction.atomic():
            self.create_admin()
            self.create_tags()
            self.create_users()
            self.create_recipes()
            self.create_interactions()

        self.stdout.write(
            self.style.SUCCESS("\n✅ Все тестовые данные загружены!")
        )
        self.print_summary()

    def clear_data(self):
        """Очищает все данные."""
        self.stdout.write(self.style.WARNING("🧹 Очищаю данные..."))
        
        # Очищаем в правильном порядке из-за внешних ключей
        Subscription.objects.all().delete()
        ShoppingCart.objects.all().delete()
        Favorite.objects.all().delete()
        IngredientInRecipe.objects.all().delete()
        Recipe.objects.all().delete()
        Tag.objects.all().delete()
        User.objects.all().delete()
        
        self.stdout.write("  ✓ Данные очищены")

    def create_admin(self):
        """Создает администратора."""
        self.stdout.write("👤 Создаю администратора...")
        
        admin, created = User.objects.get_or_create(
            email="admin@foodgram.ru",
            defaults={
                "username": "admin",
                "first_name": "Админ",
                "last_name": "Админов",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("  ✅ Администратор создан")
            self.stdout.write(f"     Email: {admin.email}")
            self.stdout.write(f"     Пароль: admin123")
        else:
            self.stdout.write("  ℹ️  Администратор уже существует")

    def create_tags(self):
        """Создает теги."""
        self.stdout.write("🏷️  Создаю теги...")
        
        tags_data = [
            {"name": "Завтрак", "color": "#E26C2D", "slug": "breakfast"},
            {"name": "Обед", "color": "#49B64E", "slug": "lunch"},
            {"name": "Ужин", "color": "#8775D2", "slug": "dinner"},
            {"name": "Десерт", "color": "#F44336", "slug": "dessert"},
            {"name": "Быстро", "color": "#FF9800", "slug": "fast"},
            {"name": "Здоровое", "color": "#4CAF50", "slug": "healthy"},
            {"name": "Веганское", "color": "#2196F3", "slug": "vegan"},
            {"name": "Праздничное", "color": "#9C27B0", "slug": "holiday"},
        ]

        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data["slug"], 
                defaults=tag_data
            )
            status = "✅" if created else "ℹ️"
            self.stdout.write(f"  {status} {tag.name}")

    def create_users(self):
        """Создает тестовых пользователей."""
        self.stdout.write("👥 Создаю тестовых пользователей...")
        
        users_data = [
            {
                "email": "chef@foodgram.ru",
                "username": "chef_master",
                "first_name": "Шеф",
                "last_name": "Поваров",
                "password": "testpass123",
            },
            {
                "email": "maria@foodgram.ru", 
                "username": "maria_cook",
                "first_name": "Мария",
                "last_name": "Кулинарова",
                "password": "testpass123",
            },
            {
                "email": "ivan@foodgram.ru",
                "username": "ivan_food",
                "first_name": "Иван",
                "last_name": "Гурманов",
                "password": "testpass123",
            },
            {
                "email": "anna@foodgram.ru",
                "username": "anna_baker",
                "first_name": "Анна",
                "last_name": "Пекарева",
                "password": "testpass123",
            },
            {
                "email": "test@foodgram.ru",
                "username": "testuser",
                "first_name": "Тест",
                "last_name": "Пользователь",
                "password": "testpass123",
            },
        ]

        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "username": user_data["username"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                }
            )
            if created:
                user.set_password(user_data["password"])
                user.save()
                self.stdout.write(f"  ✅ {user.username} ({user.email})")
            else:
                self.stdout.write(f"  ℹ️  {user.username} уже существует")

    def create_recipes(self):
        """Создает тестовые рецепты."""
        self.stdout.write("🍳 Создаю тестовые рецепты...")
        
        # Получаем пользователей и теги
        users = list(User.objects.filter(is_superuser=False))
        tags = list(Tag.objects.all())
        
        if not users:
            self.stdout.write("  ⚠️  Нет пользователей для создания рецептов")
            return
            
        # Создаем несколько базовых ингредиентов
        ingredients_data = [
            ("Мука", "г"),
            ("Сахар", "г"),
            ("Яйца", "шт"),
            ("Молоко", "мл"),
            ("Масло сливочное", "г"),
            ("Соль", "г"),
            ("Помидоры", "шт"),
            ("Лук", "шт"),
            ("Морковь", "шт"),
            ("Картофель", "шт"),
            ("Мясо", "г"),
            ("Рис", "г"),
            ("Макароны", "г"),
            ("Сыр", "г"),
            ("Чеснок", "зубчик"),
        ]
        
        for name, unit in ingredients_data:
            Ingredient.objects.get_or_create(
                name=name, 
                measurement_unit=unit
            )
        
        ingredients = list(Ingredient.objects.all())
        
        recipes_data = [
            {
                "name": "Классические блинчики",
                "text": "Традиционные русские блинчики на молоке. Идеальный завтрак для всей семьи. Подавать с медом, сметаной или вареньем.",
                "cooking_time": 30,
                "tags": ["breakfast"],
                "ingredients": [
                    ("Мука", 200),
                    ("Молоко", 500),
                    ("Яйца", 2),
                    ("Сахар", 50),
                    ("Соль", 5),
                ]
            },
            {
                "name": "Борщ украинский",
                "text": "Наваристый борщ с говядиной и свежими овощами. Классический рецепт с богатым вкусом и ароматом.",
                "cooking_time": 120,
                "tags": ["lunch", "healthy"],
                "ingredients": [
                    ("Мясо", 500),
                    ("Картофель", 3),
                    ("Морковь", 2),
                    ("Лук", 1),
                    ("Помидоры", 2),
                ]
            },
            {
                "name": "Паста карбонара",
                "text": "Итальянская паста с беконом, яйцом и сыром пармезан. Нежная и сливочная текстура.",
                "cooking_time": 25,
                "tags": ["dinner", "fast"],
                "ingredients": [
                    ("Макароны", 300),
                    ("Яйца", 2),
                    ("Сыр", 100),
                    ("Мясо", 150),
                ]
            },
            {
                "name": "Шоколадный торт",
                "text": "Влажный шоколадный торт с глазурью. Идеальный десерт для праздника.",
                "cooking_time": 90,
                "tags": ["dessert", "holiday"],
                "ingredients": [
                    ("Мука", 250),
                    ("Сахар", 200),
                    ("Яйца", 3),
                    ("Масло сливочное", 100),
                ]
            },
            {
                "name": "Овощной салат",
                "text": "Свежий салат из сезонных овощей с оливковым маслом. Легкий и полезный.",
                "cooking_time": 15,
                "tags": ["healthy", "vegan", "fast"],
                "ingredients": [
                    ("Помидоры", 2),
                    ("Лук", 1),
                    ("Морковь", 1),
                ]
            },
            {
                "name": "Плов узбекский",
                "text": "Ароматный плов с бараниной и специями. Готовится в казане по традиционному рецепту.",
                "cooking_time": 180,
                "tags": ["lunch", "dinner"],
                "ingredients": [
                    ("Рис", 500),
                    ("Мясо", 700),
                    ("Морковь", 3),
                    ("Лук", 2),
                    ("Чеснок", 5),
                ]
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
                }
            )
            
            if created:
                # Добавляем теги
                recipe_tags = [tag for tag in tags if tag.slug in recipe_data["tags"]]
                recipe.tags.set(recipe_tags)
                
                # Добавляем ингредиенты
                for ingredient_name, amount in recipe_data["ingredients"]:
                    try:
                        ingredient = Ingredient.objects.get(name=ingredient_name)
                        IngredientInRecipe.objects.create(
                            recipe=recipe,
                            ingredient=ingredient,
                            amount=amount
                        )
                    except Ingredient.DoesNotExist:
                        pass
                
                self.stdout.write(f"  ✅ {recipe.name} (автор: {author.username})")
            else:
                self.stdout.write(f"  ℹ️  {recipe.name} уже существует")

    def create_recipe_image(self, recipe_name):
        """Создает простое изображение для рецепта."""
        # Создаем простое изображение-заглушку
        img = Image.new('RGB', (300, 200), color='lightgray')
        
        # Сохраняем в BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Создаем Django File
        filename = f"recipe_{recipe_name.lower().replace(' ', '_')}.jpg"
        return ContentFile(img_io.getvalue(), name=filename)

    def create_interactions(self):
        """Создает взаимодействия: подписки, избранное, корзины."""
        self.stdout.write("❤️  Создаю взаимодействия...")
        
        users = list(User.objects.filter(is_superuser=False))
        recipes = list(Recipe.objects.all())
        
        if len(users) < 2 or not recipes:
            self.stdout.write("  ⚠️  Недостаточно данных для создания взаимодействий")
            return
        
        # Создаем подписки
        for user in users[:3]:
            for author in users[-2:]:
                if user != author:
                    Subscription.objects.get_or_create(
                        user=user, 
                        author=author
                    )
        
        # Добавляем рецепты в избранное
        for user in users:
            favorite_recipes = random.sample(recipes, min(3, len(recipes)))
            for recipe in favorite_recipes:
                Favorite.objects.get_or_create(
                    user=user,
                    recipe=recipe
                )
        
        # Добавляем рецепты в корзину
        for user in users[:3]:
            cart_recipes = random.sample(recipes, min(2, len(recipes)))
            for recipe in cart_recipes:
                ShoppingCart.objects.get_or_create(
                    user=user,
                    recipe=recipe
                )
        
        self.stdout.write("  ✅ Взаимодействия созданы")

    def print_summary(self):
        """Выводит сводку по созданным данным."""
        self.stdout.write("\n📊 Сводка по данным:")
        self.stdout.write(f"  👤 Пользователи: {User.objects.count()}")
        self.stdout.write(f"  🏷️  Теги: {Tag.objects.count()}")
        self.stdout.write(f"  🥕 Ингредиенты: {Ingredient.objects.count()}")
        self.stdout.write(f"  🍳 Рецепты: {Recipe.objects.count()}")
        self.stdout.write(f"  ❤️  Избранное: {Favorite.objects.count()}")
        self.stdout.write(f"  🛒 В корзине: {ShoppingCart.objects.count()}")
        self.stdout.write(f"  👥 Подписки: {Subscription.objects.count()}")
        
        self.stdout.write("\n🔑 Учетные данные:")
        self.stdout.write("  👨‍💻 Администратор:")
        self.stdout.write("     Email: admin@foodgram.ru")
        self.stdout.write("     Пароль: admin123")
        self.stdout.write("  👤 Тестовые пользователи:")
        self.stdout.write("     Пароль для всех: testpass123") 