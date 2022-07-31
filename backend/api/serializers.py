"""Модуль описания сериализаторов."""
from re import match
from typing import Any

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import F
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import Ingredient, Recipe, Tag
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)

from .utils import recipe_amount_ingredients_set
from .validators import class_obj_validate, hex_color_validate

User = get_user_model()


class UserSerializer(ModelSerializer):
    """
    Сериализатор для модели FoodgramUser.
    Поле "password" только для записи - используется при самостоятельной
    регистрации пользователя.
    """
    is_subscribed = SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed', )

    def get_is_subscribed(self, obj: object) -> bool:
        """Проверка подписки текущего пользователя на просматриваемого."""
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscription.filter(id=obj.id).exists()


class RecipeSmallSerializer(ModelSerializer):
    """Сериализатор для модели Recipe с сокращённым списком полей."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('__all__', )


class UserFollowsSerializer(UserSerializer):
    """
    Сериализатор для вывода авторов на которых подписан текущий пользователь.
    """
    # recipes = RecipeSmallSerializer(many=True, read_only=True)
    recipes = SerializerMethodField(method_name='paginated_recipes')
    recipes_count = SerializerMethodField(method_name='get_recipes_count')

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'recipes_count',
            'is_subscribed'
        )
        read_only_fields = ('__all__', )

    def get_recipes_count(self, obj: object) -> int:
        """Показывает суммарное количество рецептов у каждого автора."""
        return obj.recipes.count()

    def get_is_subscribed(*args) -> bool:
        """
        Проверка подписки текущего пользователя на просматриваемого.
        Переопределяем метод для сокращения нагрузки, так как всегда
        возвращает "True".
        """
        return True

    def paginated_recipes(self, obj):
        paginator = Paginator(
            obj.recipes.all(),
            self.context.get('request').query_params.get('recipes_limit', 3)
        )
        recipes = paginator.page(1)
        serializer = RecipeSmallSerializer(recipes, many=True)
        return serializer.data


class CreateUserSerializer(UserSerializer):
    """Сериализатор, применяемый при создании пользователей."""
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data: dict) -> object:
        """Создаёт нового пользователя."""
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, username: str):
        """Валидация введённого username."""
        if len(username) < 3:
            raise ValidationError(
                'Длина username допустима от 3 до 150'
            )
        if not match(pattern=r'^[\w.@+-]+$', string=username):
            raise ValidationError(
                'В username допустимы только буквы.'
            )
        return username.lower()


class IngredientSerializer(ModelSerializer):
    """Сериализатор для модели Ingredients."""
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('__all__', )


class TagSerializer(ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__', )

    def validate_color(self, color: str) -> str:
        """Валидация формата поля color."""
        color = str(color).strip(' #')
        hex_color_validate(color)
        return f'#{color}'


class RecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = SerializerMethodField(method_name='get_ingredients')
    is_favorited = SerializerMethodField(method_name='get_is_favorited')
    is_in_shopping_cart = SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart'
        )
        read_only_fields = (
            'is_favorite',
            'is_shopping_cart'
        )

    def get_ingredients(self, obj: object) -> Any:
        """Возвращает список ингридиентов для рецепта."""
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj: object) -> bool:
        """
        Возвращает "True" если переданный рецепт находится в избранном у
        текущего пользователя.
        """
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.favorites.filter(id=obj.id).exists())

    def get_is_in_shopping_cart(self, obj: object) -> bool:
        """
        Возвращает "True" если переданный рецепт находится в списке покупок у
        текущего пользователя.
        """
        user = self.context.get('request').user
        return (user.is_authenticated
                and user.in_cart.filter(id=obj.id).exists())

    def validate(self, data):
        """Проверка вводных данных при создании/редактировании рецепта."""
        name = str(data['name']).strip()
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')
        values_as_list = {'tags': tags, 'ingradients': ingredients}

        for key, value in values_as_list.items():
            if not isinstance(value, list):
                raise ValidationError(
                    f'Содержимое "{key}" должно быть списком./n'
                    f'{key}: {value}/n'
                    f'data: {data}'
                )

        for tag in tags:
            class_obj_validate(
                value=tag,
                klass=Tag
            )

        valid_ingredients = []
        valid_amounts = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in valid_ingredients:
                raise ValidationError('Ингредиенты не должны повторяться')
            valid_ingredients.append(ingredient)
            class_obj_validate(value=item['amount'])
            valid_amounts.append(item['amount'])
        valid_ingredients = [
            dict(ingredient=i, amount=a) for i, a in zip(
                valid_ingredients, valid_amounts
            )
        ]

        data['name'] = name.lower()
        data['tags'] = tags
        data['ingredients'] = valid_ingredients
        data['author'] = self.context.get('request').user
        return data

    def create(self, validated_data):
        """Создаёт новый объект модели Recipe."""
        image = validated_data.pop('image')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        recipe.tags.set(tags)
        recipe_amount_ingredients_set(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        """Обновляет объект Recipe."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        super().update(recipe, validated_data)

        if tags:
            recipe.tags.clear()
            recipe.tags.set(tags)

        if ingredients:
            recipe.ingredients.clear()
            recipe_amount_ingredients_set(recipe, ingredients)

        recipe.save()
        return recipe
