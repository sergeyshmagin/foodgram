 Аутентификация и UserAdmin
Не используйте admin.ModelAdmin для User; вместо этого:

python
Копировать
Редактировать
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    ...
Используйте @admin.display(description="Читаемое имя") для методов в list_display.

Удаляйте из админки ненужные модели:

python
Копировать
Редактировать
from django.contrib.auth.models import Group
admin.site.unregister(Group)
🧱 Модели
🔁 Повторяющиеся поля
Вынесите поля created_at, is_published в абстрактную модель:

python
Копировать
Редактировать
class TimeStampedPublishedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        abstract = True
📍 Location
Поле location должно иметь blank=True, null=True.

🔢 Магические числа
Все значения вроде 10, 5 и т.п. выносите в constants.py.

🛠 Админка
Используйте InlineModelAdmin для вложенного редактирования (например, постов в категории).

Для регистрации моделей используйте @admin.register вместо admin.site.register.

📦 Импорты (PEP8)
Строго следуйте порядку:

Стандартные библиотеки

Сторонние библиотеки

Модули проекта

Между группами — пустая строка.

Автоматизация: isort.

🔍 QuerySet и Manager
Используйте кастомные QuerySet/Manager:

Для фильтрации — PostQuerySet(BaseQuerySet) с методом .published()

Применяйте .as_manager() в модели

Пример:

python
Копировать
Редактировать
class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

class Post(models.Model):
    ...
    objects = PostQuerySet.as_manager()
✅ Тесты (pytest / UnitTest)
🧪 Pytest
Все reverse() выносите в conftest.py как фикстуры.

@pytest.mark.parametrize — использовать везде, где повторяются входные данные.

Фикстура с autouse=True для доступа к БД:

python
Копировать
Редактировать
@pytest.fixture(autouse=True)
def enable_db_access(db):
    pass
Везде используйте constants.py, даже в тестах (COMMENTS_LIMIT, NEWS_COUNT_ON_HOME_PAGE и т.д.)

Используйте фикстуры с bulk-созданием:

python
Копировать
Редактировать
@pytest.fixture
def many_news():
    return [News(..., pub_date=timezone.now() - timedelta(days=i)) for i in range(COMMENTS_LIMIT)]
🧪 UnitTest
Используйте базовый класс BaseTestCase(TestCase) в common.py

Все общие данные в setUpTestData()

Все URL — через reverse() и как константы

🧾 Сериализаторы и ViewSets
Не переопределяйте create() в Serializer, если можно обойтись стандартным.

Используйте PrimaryKeyRelatedField с queryset= и validators=[UniqueTogetherValidator(...)]

Поля с отношениями: read_only=True или queryset=...

Валидацию по полям делайте через validate_<field>()

Используйте to_representation() вместо create()/update() для изменения формата ответа

🔐 Permissions
Все permissions — в permissions.py

IsAdminOrReadOnly, IsAuthorOrReadOnly, IsSuperAdmin не должны включать is_authenticated

Используйте IsAuthenticated отдельно

📊 Фильтрация и аннотация
Используйте annotate() вместо SerializerMethodField для вычисляемых полей

Используйте кастомные фильтры через django_filters.FilterSet

Все фильтры — в filters.py

⚙️ API
Версионируйте API (/api/v1/)

ViewSet для категорий и жанров — через базовый класс с миксинами и общими настройками

🧾 README.md
Обязательно наличие:

Описание проекта

Установка

Примеры API-запросов

Лицензия (если применимо)

⚙️ CI/CD
CI setup:

Кэшируйте зависимости: https://github.blog/changelog/2021-11-23-github-actions-setup-python-now-supports-dependency-caching/

Вынесите зависимости в requirements/

requirements.txt в backend/ — для платформы

🔍 Разное
Используйте кавычки одного типа (одинарные или двойные) во всём проекте

Удаляйте пустые классы/методы или ... если есть docstring

Все ошибки — через конкретные исключения (например, TypeError, ValidationError)

Не логируйте ошибки в нижнем уровне — прокидывайте их наверх

Логгируйте все пропущенные значения (а не first failed)

Пустые сериализаторы .save() без логики — бессмысленны