from re import match

from django.contrib.auth import get_user_model
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)

from recipe.models import Ingredient, Recipe, Tag
from api.validators import class_obj_validate, hex_color_validate
from api.utils import recipe_amount_ingredients_set


User = get_user_model()


class UserSerializer(ModelSerializer):
    """
    Сериализатор для модели FoodgramUser.
    """
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = 'is_subscribed',

    def get_is_subscribed(self, obj: object) -> bool:
        """
        Проверка подписки текущего пользователя на просматриваемого.
        """
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False
        return user.subscribe.filter(id=obj.id).exists()

    def create(self, validated_data: dict) -> object:
        """
        Создаёт нового пользователя.
        """
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
        """
        Проверяет введённый юзернейм.
        """
        if len(username) < 3:
            raise ValidationError(
                'Длина username допустима от 3 до 150'
            )
        if not match(pattern=r'^[\w.@+-]+$', string=username):
            raise ValidationError(
                'В username допустимы только буквы.'
            )
        return username.lower()


class RecipeSmallSerializer(ModelSerializer):
    """
    Сериализатор для модели Recipe с сокращённым списком полей.
    """
    class Meta:
        model = Recipe
        fields = 'id', 'name', 'image', 'cooking_time'
        read_only_fields = '__all__',


class UserFollowsSerializer(UserSerializer):
    """
    Сериализатор для вывода авторов на которых подписан текущий пользователь.
    """
    recipes = RecipeSmallSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

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
            'is_subscribed',
        )
        read_only_fields = '__all__',

    def get_recipes_count(self, obj: object) -> int:
        """
        Показывает суммарное количество рецептов у каждого автора.
        """
        return obj.recipes.count()

    def get_is_subscribed(*args) -> bool:
        """
        Проверка подписки текущего пользователя на просматриваемого.
        Переопределяем метод для сокращения нагрузки, так как всегда
        возвращает `True`.
        """
        return True


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор для модели Ingredients.
    """
    class Meta:
        model = Ingredient
        fields = ('__all__', )
        read_only_fields = ('__all__', )


class TagSerializer(ModelSerializer):
    """
    Сериализатор для модели TAg.
    """
    class Meta:
        model = Tag
        fields = ('__all__', )
        read_only_fields = ('__all__', )

    def validate_color(self, color: str) -> str:
        color = str(color).strip(' #')
        hex_color_validate(color)
        return f'#{color}'
