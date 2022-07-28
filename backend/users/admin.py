"""Модуль содержит настройки админки для приложения usesr."""
from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser


@register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name'
    )
    fieldsets = (
        (
            None, {
                'fields': (
                    ('username', 'email'),
                    ('first_name', 'last_name'),
                    ('date_joined', ),
                    ('password', ),
                ),
            }
        ),
        (
            'Права доступа', {
                'classes': ('collapse', ),
                'fields': (
                    'is_active',
                    'is_superuser',
                    'is_staff',
                ),
            }
        ),
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'username',
        'first_name',
        'email',
    )
    save_on_top = True
