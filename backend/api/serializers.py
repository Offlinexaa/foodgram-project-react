from django.contrib.auth import get_user_model
from rest_framework.serializers import (ModelSerializer, SerializerMethodField,
                                        ValidationError)

from recipe.models import Ingredient, Recipe, Tag
from api.validators import class_obj_validate, hex_color_validate
from api.utils import recipe_amount_ingredients_set


User = get_user_model()


class UserSerializer(ModelSerializer):
    """Сериализатор для модели FoodgramUser.
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
        if not username.isalpha():
            raise ValidationError(
                'В username допустимы только буквы.'
            )
        return username.capitalize()
