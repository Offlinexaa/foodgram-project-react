"""Модуль описания вспомогательных функций."""
import csv
from datetime import datetime as dt

from django.http.response import HttpResponse

from recipe.models import IngredientAmount


def recipe_amount_ingredients_set(recipe, ingredients):
    """
    Создаёт объект IngredientAmount связывающий объекты Recipe и
    Ingredient с указанием количества ("amount") конкретного ингридиента.
    """
    for ingredient in ingredients:
        IngredientAmount.objects.get_or_create(
            recipe=recipe,
            ingredients=ingredient['ingredient'],
            amount=ingredient['amount'],
        )


def prepare_file(user, ingredients, filename='shopping_list.csv'):
    """
    Формирует объект типа HttpResponse, содержащий файл формата *.csv со
    списком и количеством ингредиентов, которые нужно купить.
    """
    filename = 'shopping_list.csv'
    create_time = dt.now().strftime('%d.%m.%Y %H:%M')

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename={filename}'

    writer = csv.writer(response)
    writer.writerow([f'Список покупок пользователя: {user.first_name}', ])
    writer.writerow([f'{create_time}', ])
    writer.writerow(['', ])
    writer.writerow(['Ингредиент', 'Количество', 'Единицы измерения'])
    for ingredient in ingredients:
        writer.writerow(
            [
                ingredient['ingredient'],
                ingredient['sum_amount'],
                ingredient['measure']
            ]
        )
    writer.writerow(['', ])
    writer.writerow(['Сформировано в продуктовом помощнике Foodgram', ])
    
    return response
