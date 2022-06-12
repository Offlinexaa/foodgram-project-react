from django.contrib.admin import register, ModelAdmin

from .models import Ingredient, IngredientAmount, Recipe, Tag

EMPTY_VAL_PLACEHOLDER = 'Не указано'

@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_VAL_PLACEHOLDER
    save_on_top = True


@register(IngredientAdmin)
class IngredientAmounAdmin(ModelAdmin):
    pass


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ('name', 'author', 'getimage',)
    
