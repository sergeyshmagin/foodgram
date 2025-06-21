 Модели Django для проекта Foodgram
1. User (расширение AbstractUser)
python
Копировать
Редактировать
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username
Особенности:

Email как логин (USERNAME_FIELD)

Поддержка аватара

2. Tag
python
Копировать
Редактировать
class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)  # hex-код
    slug = models.SlugField(max_length=200, unique=True)

    def __str__(self):
        return self.name
3. Ingredient
python
Копировать
Редактировать
class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=50)

    class Meta:
        unique_together = ('name', 'measurement_unit')
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'
4. Recipe
python
Копировать
Редактировать
class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='recipes/images/')
    text = models.TextField()
    cooking_time = models.PositiveIntegerField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe'
    )
    tags = models.ManyToManyField(Tag, related_name='recipes')
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.name
5. IngredientInRecipe (промежуточная таблица)
python
Копировать
Редактировать
class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredient_list')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ('recipe', 'ingredient')
6. Favorite
python
Копировать
Редактировать
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ('user', 'recipe')
7. ShoppingCart
python
Копировать
Редактировать
class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'recipe')
8. Subscription
python
Копировать
Редактировать
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
📌 Примечания к реализации:
Все unique_together будут проверяться в сериализаторах.

При создании рецепта: теги и ингредиенты передаются списками, потребуются вложенные сериализаторы.

cooking_time должен быть ≥ 1.

В админке можно вывести количество добавлений в Favorite с помощью annotate и admin_display.