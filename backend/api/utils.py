"""Модуль вспомогательных функций."""
from recipe.models import IngredientAmount


def recipe_amount_ingredients_set(recipe, ingredients):
    """
    Создаёт объект IngredientAmount связывающий объекты Recipe и
    Ingredient с указанием количества(`amount`) конкретного ингридиента.

    recipe - экземпляр объекта Recipe.
    ingredients - список словарей с ключами
        ingredient - ID объекта Ingredient
        amount - количество
    """
    for ingredient in ingredients:
        IngredientAmount.objects.get_or_create(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount'],
        )
