"""Management команда для создания тестовых данных."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.recipes.models import Tag

User = get_user_model()


class Command(BaseCommand):
    """Команда для создания тестовых данных."""
    
    help = 'Создает тестовые данные: теги и пользователей'
    
    def add_arguments(self, parser):
        """Добавляет аргументы командной строки."""
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить данные перед созданием'
        )
    
    def handle(self, *args, **options):
        """Основная логика команды."""
        if options['clear']:
            self.stdout.write(
                self.style.WARNING('Очищаю тестовые данные...')
            )
            Tag.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        
        # Создаем теги
        self.stdout.write('Создаю теги...')
        tags_data = [
            {'name': 'Завтрак', 'color': '#E26C2D', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#49B64E', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#8775D2', 'slug': 'dinner'},
        ]
        
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(
                slug=tag_data['slug'],
                defaults=tag_data
            )
            if created:
                self.stdout.write(f'  ✓ Создан тег: {tag.name}')
            else:
                self.stdout.write(f'  → Тег уже существует: {tag.name}')
        
        # Создаем тестовых пользователей
        self.stdout.write('Создаю тестовых пользователей...')
        users_data = [
            {
                'email': 'user1@example.com',
                'username': 'user1',
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'password': 'testpass123'
            },
            {
                'email': 'user2@example.com', 
                'username': 'user2',
                'first_name': 'Мария',
                'last_name': 'Петрова',
                'password': 'testpass123'
            },
        ]
        
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
                self.stdout.write(f'  ✓ Создан пользователь: {user.username}')
            else:
                self.stdout.write(f'  → Пользователь уже существует: {user.username}')
        
        self.stdout.write(
            self.style.SUCCESS('Тестовые данные созданы!')
        ) 