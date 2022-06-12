"""Модуль содержит модели и их настройки для приложения recipe."""
from django.contrib.auth import get_user_model
from django.db.models import (Model, ForeignKey, CASCADE, ManyToManyField,
                              PositiveIntegerField, ImageField, DateTimeField,
                              TextField, CharField, SlugField,
                              UniqueConstraint)
from django.core.validators import MinValueValidator


User = get_user_model()


class Ingredient(Model):
    """
    Модель, содержащая ингредиенты.
    """
    measurement_unit = CharField(
        verbose_name='Единицы измерения',
        max_length=200,
    )
    name = CharField(
        verbose_name='Ингредиент',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = (
            UniqueConstraint(
                name='Unique_measure_for_ingredient',
                fields=('name', 'measurement_unit'),
            ),
        )


class IngredientAmount(Model):
    """
    Модель связывающая ингредиенты с рецептом.
    Так же хранит количество ингредиента в рецепте.
    """
    amount = PositiveIntegerField(
        verbose_name='Количество',
        default=0,
        validators=(
            MinValueValidator(1, 'Не может быть меньше 1.'),
        ),
    )
    ingredients = ForeignKey(
        to=Ingredient,
        on_delete=CASCADE,
        related_name='recipe',
        verbose_name='Ингредиенты, связанные с рецептом',
    )
    recipe = ForeignKey(
        to='Recipe',
        on_delete=CASCADE,
        related_name='ingredients',
        verbose_name='Рецепты, содержащие ингредиенты',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            UniqueConstraint(
                name='Unique_ingredient_in_recipe',
                fields=('ingredient', 'recipe'),
            ),
        )


class Tag(Model):
    """
    Модель, описывающая теги для рецептов.
    """
    color = CharField(
        verbose_name='Код цвета',
        max_length=6,
        default='ff',
    )
    name = CharField(
        verbose_name='Тег',
        max_length=200,
        unique=True,
    )
    slug = SlugField(
        verbose_name='Slug для тега',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)


class Recipe(Model):
    """
    Модель, описывающая рецепт.
    """
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        oredering = ('-pub_date',)
        constraints = (
            UniqueConstraint(
                name='unique_per_author',
                fields=('name', 'author'),
            ),
        )
