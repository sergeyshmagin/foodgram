"""Management команда для загрузки полных тестовых данных."""
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
            self.create_ingredients()
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

    def create_ingredients(self):
        """Создает базовые ингредиенты."""
        self.stdout.write("🥕 Создаю ингредиенты...")
        
        ingredients_data = [
            ("Мука пшеничная", "г"),
            ("Сахар", "г"),
            ("Яйца куриные", "шт"),
            ("Молоко", "мл"),
            ("Масло сливочное", "г"),
            ("Соль", "г"),
            ("Помидоры", "шт"),
            ("Лук репчатый", "шт"),
            ("Морковь", "шт"),
            ("Картофель", "шт"),
            ("Говядина", "г"),
            ("Свинина", "г"),
            ("Курица", "г"),
            ("Рис", "г"),
            ("Макароны", "г"),
            ("Сыр твердый", "г"),
            ("Чеснок", "зубчик"),
            ("Перец черный", "г"),
            ("Растительное масло", "мл"),
            ("Сметана", "г"),
            ("Огурцы", "шт"),
            ("Капуста", "г"),
            ("Свекла", "шт"),
            ("Зелень", "г"),
            ("Мед", "г"),
        ]
        
        for name, unit in ingredients_data:
            ingredient, created = Ingredient.objects.get_or_create(
                name=name, 
                measurement_unit=unit
            )
            status = "✅" if created else "ℹ️"
            self.stdout.write(f"  {status} {name}")

    def create_recipes(self):
        """Создает тестовые рецепты."""
        self.stdout.write("🍳 Создаю тестовые рецепты...")
        
        users = list(User.objects.filter(is_superuser=False))
        tags = list(Tag.objects.all())
        
        if not users:
            self.stdout.write("  ⚠️  Нет пользователей для создания рецептов")
            return
        
        recipes_data = [
            {
                "name": "Классические блинчики",
                "text": "Традиционные русские блинчики на молоке. Идеальный завтрак для всей семьи. Смешайте все ингредиенты, жарьте на сковороде до золотистого цвета. Подавать с медом, сметаной или вареньем.",
                "cooking_time": 30,
                "tags": ["breakfast"],
                "ingredients": [
                    ("Мука пшеничная", 200),
                    ("Молоко", 500),
                    ("Яйца куриные", 2),
                    ("Сахар", 50),
                    ("Соль", 5),
                    ("Растительное масло", 30),
                ]
            },
            {
                "name": "Борщ украинский",
                "text": "Наваристый борщ с говядиной и свежими овощами. Классический рецепт с богатым вкусом и ароматом. Варите бульон 1 час, добавьте овощи, тушите до готовности.",
                "cooking_time": 120,
                "tags": ["lunch", "healthy"],
                "ingredients": [
                    ("Говядина", 500),
                    ("Картофель", 3),
                    ("Морковь", 2),
                    ("Лук репчатый", 1),
                    ("Помидоры", 2),
                    ("Свекла", 1),
                    ("Капуста", 200),
                    ("Зелень", 50),
                ]
            },
            {
                "name": "Паста карбонара",
                "text": "Итальянская паста с беконом, яйцом и сыром пармезан. Нежная и сливочная текстура. Готовится быстро - идеально для ужина.",
                "cooking_time": 25,
                "tags": ["dinner", "fast"],
                "ingredients": [
                    ("Макароны", 300),
                    ("Яйца куриные", 2),
                    ("Сыр твердый", 100),
                    ("Свинина", 150),
                    ("Чеснок", 2),
                    ("Перец черный", 5),
                ]
            },
            {
                "name": "Шоколадный торт",
                "text": "Влажный шоколадный торт с глазурью. Идеальный десерт для праздника. Выпекайте в духовке при 180°С.",
                "cooking_time": 90,
                "tags": ["dessert", "holiday"],
                "ingredients": [
                    ("Мука пшеничная", 250),
                    ("Сахар", 200),
                    ("Яйца куриные", 3),
                    ("Масло сливочное", 100),
                    ("Молоко", 200),
                ]
            },
            {
                "name": "Овощной салат",
                "text": "Свежий салат из сезонных овощей с растительным маслом. Легкий и полезный вариант для любого времени года.",
                "cooking_time": 15,
                "tags": ["healthy", "vegan", "fast"],
                "ingredients": [
                    ("Помидоры", 2),
                    ("Огурцы", 2),
                    ("Лук репчатый", 1),
                    ("Зелень", 30),
                    ("Растительное масло", 20),
                    ("Соль", 5),
                ]
            },
            {
                "name": "Плов узбекский",
                "text": "Ароматный плов с бараниной и специями. Готовится в казане по традиционному рецепту. Томите на медленном огне 2 часа.",
                "cooking_time": 180,
                "tags": ["lunch", "dinner"],
                "ingredients": [
                    ("Рис", 500),
                    ("Говядина", 700),
                    ("Морковь", 3),
                    ("Лук репчатый", 2),
                    ("Чеснок", 1),
                    ("Растительное масло", 100),
                ]
            },
            {
                "name": "Куриные котлеты",
                "text": "Сочные куриные котлеты с луком. Прекрасное блюдо для семейного обеда или ужина.",
                "cooking_time": 45,
                "tags": ["lunch", "dinner"],
                "ingredients": [
                    ("Курица", 500),
                    ("Лук репчатый", 1),
                    ("Яйца куриные", 1),
                    ("Мука пшеничная", 50),
                    ("Соль", 10),
                    ("Перец черный", 5),
                ]
            },
            {
                "name": "Медовый торт",
                "text": "Классический медовый торт со сметанным кремом. Любимый десерт многих поколений.",
                "cooking_time": 120,
                "tags": ["dessert", "holiday"],
                "ingredients": [
                    ("Мука пшеничная", 300),
                    ("Мед", 100),
                    ("Сахар", 150),
                    ("Яйца куриные", 2),
                    ("Сметана", 400),
                    ("Масло сливочное", 50),
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
                        self.stdout.write(f"    ⚠️  Ингредиент не найден: {ingredient_name}")
                
                self.stdout.write(f"  ✅ {recipe.name} (автор: {author.username})")
            else:
                self.stdout.write(f"  ℹ️  {recipe.name} уже существует")

    def create_recipe_image(self, recipe_name):
        """Создает простое изображение для рецепта."""
        if Image is None:
            return None
            
        # Создаем простое изображение-заглушку
        img = Image.new('RGB', (300, 200), color='lightgray')
        
        # Сохраняем в BytesIO
        img_io = BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        # Создаем Django File
        filename = f"recipe_{recipe_name.lower().replace(' ', '_')[:20]}.jpg"
        return ContentFile(img_io.getvalue(), name=filename)

    def create_interactions(self):
        """Создает взаимодействия: подписки, избранное, корзины."""
        self.stdout.write("❤️  Создаю взаимодействия...")
        
        users = list(User.objects.filter(is_superuser=False))
        recipes = list(Recipe.objects.all())
        
        if len(users) < 2 or not recipes:
            self.stdout.write("  ⚠️  Недостаточно данных для создания взаимодействий")
            return
        
        interactions_count = 0
        
        # Создаем подписки
        for user in users[:3]:
            for author in users[-2:]:
                if user != author:
                    _, created = Subscription.objects.get_or_create(
                        user=user, 
                        author=author
                    )
                    if created:
                        interactions_count += 1
        
        # Добавляем рецепты в избранное
        for user in users:
            favorite_recipes = random.sample(recipes, min(3, len(recipes)))
            for recipe in favorite_recipes:
                _, created = Favorite.objects.get_or_create(
                    user=user,
                    recipe=recipe
                )
                if created:
                    interactions_count += 1
        
        # Добавляем рецепты в корзину
        for user in users[:3]:
            cart_recipes = random.sample(recipes, min(2, len(recipes)))
            for recipe in cart_recipes:
                _, created = ShoppingCart.objects.get_or_create(
                    user=user,
                    recipe=recipe
                )
                if created:
                    interactions_count += 1
        
        self.stdout.write(f"  ✅ Создано {interactions_count} взаимодействий")

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
        self.stdout.write("     • chef@foodgram.ru (chef_master)")
        self.stdout.write("     • maria@foodgram.ru (maria_cook)")
        self.stdout.write("     • ivan@foodgram.ru (ivan_food)")
        self.stdout.write("     • anna@foodgram.ru (anna_baker)")
        self.stdout.write("     • test@foodgram.ru (testuser)") 