# 🏆 Лучшие практики разработки Foodgram

## 📋 Общие принципы

### 1. Архитектура кода
- **DRY** (Don't Repeat Yourself) - избегаем дублирования кода
- **SOLID** - следуем принципам объектно-ориентированного программирования
- **Clean Code** - пишем понятный и читаемый код
- **Separation of Concerns** - разделяем ответственность между модулями

### 2. Структура проекта
- Один файл ≤ 500 строк. При превышении — рефакторим по модулям
- Логическое разделение на Django-приложения
- Общий код выносим в `utils/`, `constants/`, `settings.py`
- Используем blueprint pattern для организации кода

## 🐍 Django Best Practices

### 🔧 Импорты (PEP8)
Строго следуйте порядку импортов:
```python
# ✅ Правильный порядок импортов
# 1. Стандартные библиотеки
import os
from datetime import datetime

# 2. Сторонние библиотеки  
from django.db import models
from rest_framework import serializers

# 3. Модули проекта
from apps.users.models import User
from .constants import MAX_LENGTH
```

**Автоматизация**: используйте `isort` для автоматической сортировки импортов.

### 🔢 Константы и магические числа
```python
# ✅ Хорошо - все в constants.py
# constants.py
MAX_NAME_LENGTH = 200
MIN_COOKING_TIME = 1
COMMENTS_LIMIT = 10
NEWS_COUNT_ON_HOME_PAGE = 5

# models.py  
from .constants import MAX_NAME_LENGTH, MIN_COOKING_TIME

class Recipe(models.Model):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(MIN_COOKING_TIME)]
    )

# ❌ Плохо
class Recipe(models.Model):
    name = models.CharField(max_length=200)  # магическое число
    cooking_time = models.PositiveIntegerField()
```

### 📦 Абстрактные модели для повторяющихся полей
```python
# ✅ Хорошо - выносим общие поля в абстрактную модель
class TimeStampedPublishedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        abstract = True

class Recipe(TimeStampedPublishedModel):
    name = models.CharField(max_length=200)
    # created_at и is_published уже унаследованы
```

### 🔍 Кастомные QuerySet и Manager
```python
# ✅ Хорошо - используем кастомные QuerySet
class RecipeQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)
    
    def by_author(self, author):
        return self.filter(author=author)

class Recipe(models.Model):
    # ... поля модели
    objects = RecipeQuerySet.as_manager()

# Использование:
published_recipes = Recipe.objects.published()
user_recipes = Recipe.objects.by_author(user).published()
```

### 1. Модели
```python
# ✅ Хорошо
class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )
    
    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.name

# ❌ Плохо
class Recipe(models.Model):
    name = models.CharField(max_length=200)
    cooking_time = models.IntegerField()  # может быть отрицательным
```

### 2. Сериализаторы
```python
# ✅ Хорошо
class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_list',
        many=True
    )
    
    class Meta:
        model = Recipe
        fields = '__all__'
    
    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return value

# ❌ Плохо
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'
    # Нет валидации
```

### 3. ViewSets
```python
# ✅ Хорошо
class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    
    def get_queryset(self):
        return Recipe.objects.select_related('author').prefetch_related(
            'ingredients', 'tags'
        )

# ❌ Плохо
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()  # N+1 queries
    serializer_class = RecipeSerializer
    # Нет проверки прав доступа
```

### 4. Оптимизация запросов
```python
# ✅ Хорошо - используем select_related и prefetch_related
recipes = Recipe.objects.select_related('author').prefetch_related(
    'ingredients', 'tags', 'favorited_by'
)

# ✅ Хорошо - используем annotate для подсчета
recipes = Recipe.objects.annotate(
    favorites_count=Count('favorited_by')
)

# ❌ Плохо - N+1 queries
for recipe in Recipe.objects.all():
    print(recipe.author.username)  # Запрос на каждой итерации
```

## 🔐 Безопасность

### 1. Переменные окружения
```python
# ✅ Хорошо
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ❌ Плохо
SECRET_KEY = 'my-secret-key-123'  # Хардкод в коде
DEBUG = True  # В продакшене
```

### 2. Права доступа
```python
# ✅ Хорошо
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )

# ❌ Плохо
permission_classes = []  # Нет проверки прав
```

### 3. Валидация данных
```python
# ✅ Хорошо
def validate_ingredients(self, value):
    if not value:
        raise serializers.ValidationError(
            'Список ингредиентов не может быть пустым'
        )
    
    ingredient_ids = [item['id'] for item in value]
    if len(ingredient_ids) != len(set(ingredient_ids)):
        raise serializers.ValidationError(
            'Ингредиенты не должны повторяться'
        )
    
    return value

# ❌ Плохо
# Нет валидации входных данных
```

### 🛠 Админка (Django Admin)

#### 1. Правильная регистрация моделей
```python
# ✅ Хорошо - используйте @admin.register
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'cooking_time', 'favorites_count']
    list_filter = ['tags', 'pub_date']
    search_fields = ['name', 'text']
    
    @admin.display(description='Количество в избранном')
    def favorites_count(self, obj):
        return obj.favorited_by.count()

# ❌ Плохо
admin.site.register(Recipe)  # без настроек
```

#### 2. Кастомный UserAdmin
```python
# ✅ Хорошо - для кастомной модели User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

# Удаляем ненужные модели из админки
admin.site.unregister(Group)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'is_staff']
    search_fields = ['email', 'username']
    ordering = ['email']
```

#### 3. Inline редактирование
```python
# ✅ Хорошо - для связанных моделей
class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInRecipeInline]
```

## 🧪 Тестирование

### 🧪 Pytest Best Practices
```python
# ✅ Хорошо - используйте фикстуры в conftest.py
# conftest.py
@pytest.fixture(autouse=True)
def enable_db_access(db):
    """Автоматический доступ к БД во всех тестах."""
    pass

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture  
def recipe_url():
    return reverse('recipe-list')

# ✅ Хорошо - bulk создание данных
@pytest.fixture
def many_recipes():
    recipes = []
    for i in range(RECIPES_LIMIT):
        recipes.append(Recipe(
            name=f'Recipe {i}',
            cooking_time=30,
            pub_date=timezone.now() - timedelta(days=i)
        ))
    return Recipe.objects.bulk_create(recipes)
```

### 📊 Параметризованные тесты
```python
# ✅ Хорошо - используйте @pytest.mark.parametrize
@pytest.mark.parametrize(
    'cooking_time,expected_status',
    [
        (0, 400),      # невалидное значение
        (1, 201),      # минимальное валидное
        (60, 201),     # нормальное значение
        (-5, 400),     # отрицательное
    ]
)
def test_recipe_cooking_time_validation(
    api_client, user, cooking_time, expected_status
):
    api_client.force_authenticate(user=user)
    data = {
        'name': 'Test Recipe',
        'cooking_time': cooking_time,
        'text': 'Description'
    }
    response = api_client.post('/api/recipes/', data)
    assert response.status_code == expected_status
```

### 🧾 Базовый класс для тестов
```python
# ✅ Хорошо - создайте базовый класс
# tests/common.py
class BaseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        cls.recipe_url = reverse('recipe-list')
        cls.login_url = reverse('login')
    
    def authenticate_user(self):
        self.client.force_authenticate(user=self.user)

# tests/test_recipes.py
class RecipeTestCase(BaseTestCase):
    def test_create_recipe(self):
        self.authenticate_user()
        # тест логики
```

## 🧾 Сериализаторы Best Practices

### 1. Не переопределяйте create() без необходимости
```python
# ✅ Хорошо - используйте стандартный create()
class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'
    
    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return value

# ❌ Плохо - пустой create() без логики
def create(self, validated_data):
    return super().create(validated_data)  # бессмысленно
```

### 2. Правильная работа с отношениями
```python
# ✅ Хорошо - используйте PrimaryKeyRelatedField с queryset
class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Recipe
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=['author', 'name']
            )
        ]
```

### 3. Используйте to_representation() для изменения формата ответа
```python
# ✅ Хорошо - to_representation() вместо create()/update()
class RecipeSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['favorites_count'] = instance.favorited_by.count()
        return representation
```

### 1. Структура тестов
```python
# ✅ Хорошо
class RecipeViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            name='Test Recipe',
            cooking_time=30
        )
    
    def test_get_recipe_list_success(self):
        """Тест получения списка рецептов."""
        response = self.client.get('/api/recipes/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_recipe_unauthorized(self):
        """Тест создания рецепта неавторизованным пользователем."""
        response = self.client.post('/api/recipes/', {})
        self.assertEqual(response.status_code, 401)
```

### 2. Фикстуры
```python
# ✅ Хорошо - используем фикстуры pytest
@pytest.fixture
def user():
    return User.objects.create_user(
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def recipe(user):
    return Recipe.objects.create(
        author=user,
        name='Test Recipe',
        cooking_time=30
    )
```

### 3. Моки
```python
# ✅ Хорошо - мокаем внешние сервисы
@patch('recipes.services.minio_client.put_object')
def test_upload_image(self, mock_put_object):
    mock_put_object.return_value = True
    # Тест логики без реального обращения к MinIO
```

## 🚀 Асинхронность

### 1. Async Views
```python
# ✅ Хорошо
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@method_decorator(cache_page(60 * 15), name='list')
class RecipeViewSet(viewsets.ModelViewSet):
    # Кешируем список рецептов на 15 минут
    pass
```

### 2. Celery для тяжелых задач
```python
# ✅ Хорошо
@shared_task
def generate_shopping_cart_pdf(user_id):
    """Асинхронная генерация PDF списка покупок."""
    user = User.objects.get(id=user_id)
    # Генерация PDF
    return pdf_path
```

## 📊 Мониторинг и логирование

### 1. Логирование
```python
# ✅ Хорошо
import logging

logger = logging.getLogger(__name__)

def create_recipe(request):
    try:
        # Логика создания рецепта
        logger.info(f'Recipe created by user {request.user.id}')
    except Exception as e:
        logger.error(f'Error creating recipe: {e}')
        raise
```

### 2. Метрики
```python
# ✅ Хорошо - используем Django Debug Toolbar для профилирования
INSTALLED_APPS = [
    'debug_toolbar',
    # ...
]

# Настройка для отслеживания медленных запросов
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

### 📊 Фильтрация и аннотация
```python
# ✅ Хорошо - используйте annotate() вместо SerializerMethodField
class RecipeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Recipe.objects.annotate(
            favorites_count=Count('favorited_by'),
            is_favorited=Exists(
                Favorite.objects.filter(
                    user=self.request.user,
                    recipe=OuterRef('pk')
                )
            )
        )

# ❌ Плохо - SerializerMethodField создает N+1 queries
class RecipeSerializer(serializers.ModelSerializer):
    favorites_count = serializers.SerializerMethodField()
    
    def get_favorites_count(self, obj):
        return obj.favorited_by.count()  # запрос на каждом объекте
```

### 🔍 Кастомные фильтры
```python
# filters.py - все фильтры в отдельном файле
class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    
    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated and value:
            return queryset.filter(favorited_by=self.request.user)
        return queryset
    
    class Meta:
        model = Recipe
        fields = ['author', 'tags']
```

### ⚙️ API версионирование
```python
# ✅ Хорошо - версионируйте API
# urls.py
urlpatterns = [
    path('api/v1/', include('api.v1.urls')),
]

# ViewSet с базовым классом для категорий и жанров
class BaseListViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """Базовый класс для категорий и жанров."""
    pass

class TagViewSet(BaseListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
```

### 🔒 Permissions Best Practices
```python
# permissions.py - все permissions в отдельном файле
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешает редактирование только владельцу объекта.
    НЕ включает is_authenticated - используется отдельно.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )

class IsAdminOrReadOnly(permissions.BasePermission):
    """Только админ может создавать/редактировать."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_staff
        )

# ✅ Хорошо - используйте permissions отдельно
class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
# ❌ Плохо - IsAdminOrReadOnly не должен включать is_authenticated
```

## 🔄 CI/CD

### 📦 Requirements структура
```python
# ✅ Хорошо - разделяйте зависимости
requirements/
├── base.txt          # Основные зависимости
├── development.txt   # Для разработки  
└── production.txt    # Для продакшена

# base.txt
Django==3.2.16
djangorestframework==3.12.4
djoser==2.1.0

# development.txt
-r base.txt
pytest==7.1.2
pytest-django==4.5.2
flake8==4.0.1

# production.txt  
-r base.txt
gunicorn==20.1.0
```

### 🔍 Pre-commit hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

### 🧹 Качество кода
```python
# ✅ Хорошо - следуйте принципам
# 1. Используйте кавычки одного типа во всём проекте (одинарные или двойные)
GOOD_STRING = 'Используйте одинарные кавычки везде'
BAD_STRING = "Смешанные 'кавычки' плохо"

# 2. Удаляйте пустые классы/методы или добавляйте docstring
class EmptyView:
    """Пустой view для будущей реализации."""
    pass

# 3. Конкретные исключения
def validate_data(data):
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")
    if 'name' not in data:
        raise ValidationError("Name is required")

# 4. Не логируйте ошибки в нижнем уровне - прокидывайте наверх
def low_level_function():
    try:
        # какая-то логика
        pass
    except DatabaseError:
        # НЕ логируем здесь, прокидываем выше
        raise

def high_level_function():
    try:
        low_level_function()
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        # обрабатываем
```

### 📝 README.md обязательные разделы
```markdown
# Проект Foodgram

## 📖 Описание проекта
Краткое описание того, что делает проект.

## 🚀 Установка и запуск
\```bash
# Клонирование репозитория
git clone https://github.com/user/foodgram.git

# Запуск в Docker
docker-compose up -d
\```

## 📡 Примеры API-запросов
\```bash
# Получение списка рецептов
curl -X GET http://localhost/api/recipes/

# Создание рецепта
curl -X POST http://localhost/api/recipes/ \
  -H "Authorization: Token your-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Recipe", "cooking_time": 30}'
\```

## 🔗 Полезные ссылки
- API документация: http://localhost/api/docs/
- Админ панель: http://localhost/admin/

## 📄 Лицензия
MIT License (если применимо)
```

### 2. GitHub Actions
```yaml
# .github/workflows/main.yml
name: Foodgram workflow

on: [push]

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Test with pytest
        run: |
          pytest --cov=. --cov-report=xml
```

## 🏭 Продакшен

### 1. Настройки для продакшена
```python
# settings/production.py
DEBUG = False
ALLOWED_HOSTS = ['192.168.0.10', 'foodgram.example.com']

# Безопасность
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Статические файлы
STATIC_ROOT = '/app/static/'
MEDIA_ROOT = '/app/media/'
```

### 2. Docker best practices
```dockerfile
# ✅ Хорошо
FROM python:3.8-slim

# Создаем пользователя (не root)
RUN useradd --create-home --shell /bin/bash app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . /app
WORKDIR /app

# Переключаемся на пользователя app
USER app

# ❌ Плохо
FROM python:3.8
COPY . /app
RUN pip install -r requirements.txt
# Запуск от root пользователя
```

## 📈 Производительность

### 1. Кеширование
```python
# ✅ Хорошо
from django.core.cache import cache

def get_popular_recipes():
    cache_key = 'popular_recipes'
    recipes = cache.get(cache_key)
    
    if recipes is None:
        recipes = Recipe.objects.annotate(
            favorites_count=Count('favorited_by')
        ).order_by('-favorites_count')[:10]
        cache.set(cache_key, recipes, 60 * 15)  # 15 минут
    
    return recipes
```

### 2. Пагинация
```python
# ✅ Хорошо
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100
```

## 🔧 Конфигурация

### 1. Settings структура
```
settings/
├── __init__.py
├── base.py       # Общие настройки
├── development.py # Для разработки
├── production.py  # Для продакшена
└── testing.py     # Для тестов
```

### 2. Environment variables
```bash
# .env
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379/0
MINIO_ACCESS_KEY=access_key
MINIO_SECRET_KEY=secret_key
```

Эти практики помогут создать качественный, безопасный и масштабируемый проект! 🚀 