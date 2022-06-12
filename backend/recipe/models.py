"""Модуль содержит модели и их настройки для приложения recipe."""
from django.contrib.auth import get_user_model
from django.db.models import (Model, ForeignKey, CASCADE, ManyToManyField,
                              PositiveIntegerField, ImageField, DateTimeField,
                              TextField, CharField)
from django.core.validators import MinValueValidator

User = get_user_model()


class Ingredient:
    pass


class IngredientAmount:
    pass


class Tag:
    pass


class Recipe(Model):
    author = ForeignKey(
        to=User,
        on_delete=CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )
    cooking_time = PositiveIntegerField(
        verbose_name='Время приготовдения',
        default=0,
        validators=(
            MinValueValidator(1, 'Блюдо не может готовиться менее 1 минуты.'),
        )
    )
    favorite = ManyToManyField(
        to=User,
        verbose_name='Избранные рецепты',
        related_name='favorites',
    )
    ingredients = ManyToManyField(
        to=Ingredient,
        through=IngredientAmount,
        verbose_name='Список ингредиентов',
        related_name='recipe'
    )
    image = ImageField(
        verbose_name='Изображение',
        upload_to='recipe_images/',
    )
    name = CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    pub_date = DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )
    shopping_cart = ManyToManyField(
        to=User,
        verbose_name='Список покупок',
        related_name='in_cart',
    )
    tags = ManyToManyField(
        to=Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    text = TextField(
        verbose_name='Описание рецепта',
    )
