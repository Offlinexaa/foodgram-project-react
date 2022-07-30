"""Модуль описания вьюсетов."""
import csv
from datetime import datetime as dt

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http.response import HttpResponse
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilter
from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import AdminOrReadOnly, AuthorAdminOrReadOnly
from recipe.models import Ingredient, IngredientAmount, Recipe, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSmallSerializer, TagSerializer,
                          UserFollowsSerializer)

User = get_user_model()


class UserViewSet(DjoserUserViewSet, AddDelViewMixin):
    """
    ViewSet для работы с пользователми.
    Авторизованные пользователи имеют возможность подписаться на автора
    рецепта.
    """
    pagination_class = PageLimitPagination
    add_serializer = UserFollowsSerializer

    @action(methods=('GET', 'POST', 'DELETE', ), detail=True)
    def subscribe(self, request, id):
        """Создаёт/удалет подписку текущего пользователя на автора рецепта."""
        return self.add_del_obj(id, 'subscribe')

    @action(methods=('GET', ), detail=False)
    def subscriptions(self, request):
        """Список подписок текущего пользоваетеля."""
        user = self.request.user
        if not user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = User.objects.filter(followers=user)
        pages = self.paginate_queryset(authors)
        serializer = UserFollowsSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с тэгами."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """Вьюсет для работы с рецептами."""
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    add_serializer = RecipeSmallSerializer
    permission_classes = (AuthorAdminOrReadOnly, )
    pagination_class = PageLimitPagination
    filterset_class = RecipeFilter

    @action(methods=('GET', 'POST', 'DELETE', ), detail=True)
    def favorite(self, request, pk):
        """Добавляет/удалет рецепт в избранное текущему пользователю."""
        return self.add_del_obj(pk, 'favorite')

    @action(methods=('GET', 'POST', 'DELETE', ), detail=True)
    def shopping_cart(self, request, pk):
        """Добавляет/удалет рецепт в список покупок текущего пользователя."""
        return self.add_del_obj(pk, 'shopping_cart')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        """Загружает файл shopping_list.csv со списком ингредиентов."""
        user = self.request.user
        if not user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        if not user.in_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__in=user.in_cart.values('id')
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).order_by(
            'ingredient'
        ).annotate(
            sum_amount=Sum('amount')
        )

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
