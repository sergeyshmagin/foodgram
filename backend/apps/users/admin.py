"""Admin configuration for users app."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Кастомный админ для модели User."""
    
    list_display = (
        'id', 
        'username', 
        'email', 
        'first_name', 
        'last_name',
        'avatar_preview',
        'is_active',
        'date_joined'
    )
    list_display_links = ('id', 'username', 'email')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'avatar_preview')
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'avatar_preview')
        }),
        ('Права доступа', {
            'fields': (
                'is_active',
                'is_staff', 
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        ('Важные даты', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 
                'email',
                'first_name',
                'last_name', 
                'password1', 
                'password2'
            ),
        }),
    )
    
    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        """Предварительный просмотр аватара."""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="50" height="50" '
                f'style="border-radius: 50%;" />'
            )
        return '—'
