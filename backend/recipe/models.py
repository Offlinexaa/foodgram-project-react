"""Модуль содержит модели и их настройки для приложения recipe."""
from django.contrib.auth import get_user_model
from django.db.models import (Model, ForeignKey, CASCADE, ManyToManyField,
                              PositiveIntegerField,)
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipe(Model):
    author = ForeignKey(
        to=User,
        on_delete=CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',        
    )
    by_list = ManyToManyField(
        to=User,
        verbose_name='Список покупок',
        related_name='by_lists',
    )
    cooking_time = PositiveIntegerField(
        verbose_name='Время приготовдения',
        default=0,
    )


class Ingredient:
    pass


class IngredientAmount:
    pass


class Tag:
    pass
