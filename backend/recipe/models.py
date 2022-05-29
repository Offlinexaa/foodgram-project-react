"""Модуль содержит модели и их настройки для приложения recipe."""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Recipe:
    pass


class Ingredient:
    pass


class IngredientAmount:
    pass


class Tag:
    pass
