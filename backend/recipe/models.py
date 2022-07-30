"""Модуль описания моделей и их настроек для приложения recipe."""
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (CASCADE, CharField, DateTimeField, ForeignKey,
                              ImageField, ManyToManyField, Model,
                              PositiveIntegerField, SlugField, TextField,
                              UniqueConstraint)

User = get_user_model()


class Ingredient(Model):
    """Модель ингредиента."""
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
        related_name='ingredient',
        verbose_name='Рецепты, содержащие ингредиенты',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)
        constraints = (
            UniqueConstraint(
                name='Unique_ingredient_in_recipe',
                fields=('ingredients', 'recipe'),
            ),
        )


class Tag(Model):
    """Модель тега."""
    color = CharField(
        verbose_name='Код цвета',
        max_length=7,
        default='#ffffff',
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
    """Модель рецепта."""
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
        related_name='recipes'
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
    
    def _get_count_added_to_favorite(self):
        return self.favorites.count()

    _get_count_added_to_favorite.short_description = 'Добавлено в избранное, раз'

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = (
            UniqueConstraint(
                name='unique_per_author',
                fields=('name', 'author'),
            ),
        )
