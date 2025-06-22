#!/usr/bin/env python
"""
Скрипт для создания демонстрационных данных в Foodgram.
Добавляет тестовые рецепты, пользователей и взаимодействия.
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.recipes.models import Recipe, Tag, Ingredient, IngredientInRecipe, Favorite, ShoppingCart
from django.core.files.base import ContentFile
import base64

User = get_user_model()

# Простое тестовое изображение в base64
SAMPLE_IMAGE_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==
""".strip()

def create_sample_image():
    """Создает простое тестовое изображение."""
    image_data = base64.b64decode(SAMPLE_IMAGE_BASE64)
    return ContentFile(image_data, name='sample_recipe.png')

def create_demo_users():
    """Создает демонстрационных пользователей."""
    print("🧑‍🍳 Создание демонстрационных пользователей...")
    
    users_data = [
        {
            'email': 'chef@foodgram.com',
            'username': 'chef_mario',
            'first_name': 'Марио',
            'last_name': 'Баттали',
            'password': 'chef123'
        },
        {
            'email': 'baker@foodgram.com', 
            'username': 'baker_anna',
            'first_name': 'Анна',
            'last_name': 'Олсон',
            'password': 'baker123'
        },
        {
            'email': 'cook@foodgram.com',
            'username': 'home_cook',
            'first_name': 'Дмитрий',
            'last_name': 'Петров',
            'password': 'cook123'
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"  ✅ Создан пользователь: {user.email}")
        else:
            print(f"  ℹ️  Пользователь уже существует: {user.email}")
        
        created_users.append(user)
    
    return created_users

def create_demo_recipes(users):
    """Создает демонстрационные рецепты."""
    print("\n🍳 Создание демонстрационных рецептов...")
    
    # Получаем теги и ингредиенты
    breakfast_tag = Tag.objects.filter(slug='breakfast').first()
    lunch_tag = Tag.objects.filter(slug='lunch').first()
    dinner_tag = Tag.objects.filter(slug='dinner').first()
    
    # Несколько популярных ингредиентов
    flour = Ingredient.objects.filter(name__icontains='мука').first()
    milk = Ingredient.objects.filter(name__icontains='молоко').first()
    eggs = Ingredient.objects.filter(name__icontains='яйцо').first()
    sugar = Ingredient.objects.filter(name__icontains='сахар').first()
    
    recipes_data = [
        {
            'name': 'Идеальные панкейки',
            'text': '''Классические американские панкейки - идеальный завтрак для всей семьи.
            
Эти пушистые, нежные панкейки станут прекрасным началом дня. Подавайте с медом, кленовым сиропом или свежими ягодами.

Секрет успеха - не перемешивать тесто слишком долго, небольшие комочки муки только добавят пышности!''',
            'cooking_time': 15,
            'author': users[0],
            'tags': [breakfast_tag] if breakfast_tag else [],
            'ingredients': [
                {'ingredient': flour, 'amount': 200} if flour else None,
                {'ingredient': milk, 'amount': 250} if milk else None,
                {'ingredient': eggs, 'amount': 2} if eggs else None,
                {'ingredient': sugar, 'amount': 30} if sugar else None,
            ]
        },
        {
            'name': 'Домашняя паста карбонара',
            'text': '''Настоящая итальянская карбонара - это искусство в простоте.
            
Всего несколько ингредиентов, но какой результат! Главное - правильно соединить горячую пасту с яичной смесью, чтобы получился кремовый соус без комочков.

Никакого сливочного масла или сливок - только яйца, сыр и немного крахмальной воды от пасты.''',
            'cooking_time': 20,
            'author': users[1],
            'tags': [lunch_tag, dinner_tag] if lunch_tag and dinner_tag else [],
            'ingredients': [
                {'ingredient': eggs, 'amount': 3} if eggs else None,
            ]
        },
        {
            'name': 'Борщ по-домашнему',
            'text': '''Традиционный украинский борщ - визитная карточка славянской кухни.
            
Этот рецепт передается из поколения в поколение. Насыщенный, ароматный, с кислинкой от свеклы и томатов. 

Секрет яркого цвета - правильно приготовленная зажарка со свеклой. Подавать обязательно со сметаной и чесночными пампушками!''',
            'cooking_time': 120,
            'author': users[2],
            'tags': [lunch_tag, dinner_tag] if lunch_tag and dinner_tag else [],
            'ingredients': []
        }
    ]
    
    created_recipes = []
    for recipe_data in recipes_data:
        recipe, created = Recipe.objects.get_or_create(
            name=recipe_data['name'],
            defaults={
                'text': recipe_data['text'],
                'cooking_time': recipe_data['cooking_time'],
                'author': recipe_data['author'],
                'image': create_sample_image()
            }
        )
        
        if created:
            # Добавляем теги
            if recipe_data['tags']:
                recipe.tags.set(recipe_data['tags'])
            
            # Добавляем ингредиенты
            for ing_data in recipe_data['ingredients']:
                if ing_data and ing_data['ingredient']:
                    IngredientInRecipe.objects.create(
                        recipe=recipe,
                        ingredient=ing_data['ingredient'],
                        amount=ing_data['amount']
                    )
            
            print(f"  ✅ Создан рецепт: {recipe.name}")
        else:
            print(f"  ℹ️  Рецепт уже существует: {recipe.name}")
        
        created_recipes.append(recipe)
    
    return created_recipes

def create_demo_interactions(users, recipes):
    """Создает демонстрационные взаимодействия (избранное, корзина)."""
    print("\n❤️ Создание демонстрационных взаимодействий...")
    
    # Пользователи добавляют рецепты в избранное
    for i, user in enumerate(users):
        for j, recipe in enumerate(recipes):
            # Каждый пользователь добавляет разные рецепты в избранное
            if (i + j) % 2 == 0:
                favorite, created = Favorite.objects.get_or_create(
                    user=user, recipe=recipe
                )
                if created:
                    print(f"  ✅ {user.first_name} добавил в избранное: {recipe.name}")
    
    # Некоторые рецепты добавляем в корзину покупок
    for i, user in enumerate(users):
        for j, recipe in enumerate(recipes):
            if j == i:  # Каждый пользователь добавляет один рецепт в корзину
                cart_item, created = ShoppingCart.objects.get_or_create(
                    user=user, recipe=recipe
                )
                if created:
                    print(f"  🛒 {user.first_name} добавил в корзину: {recipe.name}")

def main():
    """Основная функция создания демонстрационных данных."""
    print("🎨 Создание демонстрационных данных для Foodgram")
    print("=" * 50)
    
    # Создаем пользователей
    users = create_demo_users()
    
    # Создаем рецепты
    recipes = create_demo_recipes(users)
    
    # Создаем взаимодействия
    create_demo_interactions(users, recipes)
    
    print("\n" + "=" * 50)
    print("🎉 Демонстрационные данные созданы!")
    print("\n📊 Статистика:")
    print(f"  👥 Пользователей: {User.objects.count()}")
    print(f"  🍳 Рецептов: {Recipe.objects.count()}")
    print(f"  ❤️ В избранном: {Favorite.objects.count()}")
    print(f"  🛒 В корзине: {ShoppingCart.objects.count()}")
    
    print("\n🔗 Тестовые аккаунты:")
    for user in users:
        print(f"  • {user.email} (пароль: chef123/baker123/cook123)")
    
    print("\n🌐 API доступен по адресу: http://localhost:8000/api/")
    print("🔧 Админка: http://localhost:8000/admin/")

if __name__ == "__main__":
    main() 