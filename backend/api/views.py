from datetime import datetime as dt
from urllib.parse import unquote

from django.contrib.auth import get_user_model
from django.db.models import F, Sum
from django.http.response import HttpResponse

from djoser.views import UserViewSet as DjoserUserViewSet

from recipe.models import Ingredient, IngredientAmount, Recipe, Tag

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .mixins import AddDelViewMixin
from .paginators import PageLimitPagination
from .permissions import AdminOrReadOnly, AuthorAdminOrReadOnly
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
        """
        Создаёт/удалет связь между пользователями.
        """
        return self.add_del_obj(id, 'subscribe')

    @action(methods=('GET', ), detail=False)
    def subscriptions(self, request):
        """
        Список подписок пользоваетеля.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Response(status=HTTP_401_UNAUTHORIZED)
        authors = user.followers.all()
        pages = self.paginate_queryset(authors)
        serializer = UserFollowsSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(ReadOnlyModelViewSet):
    """
    Вьюсет для работы с тэгами.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly, )


class IngredientViewSet(ReadOnlyModelViewSet):
    """
    Вьюсет для работы с ингредиентами.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )

    def get_queryset(self):
        """
        Получает список пользователей в соответствии с параметрами поиска.
        Поиск объектов по совпадению в начале строки или по содержанию
        подстроки в имени.
        """
        name = self.request.query_params.get('name')
        queryset = self.queryset
        if name:
            if name[0] == '%':
                name = unquote(name)
            name = name.lower()
            queryset_startswith = list(queryset.filter(name__startswith=name))
            queryset_contains = list(queryset.filter(name__contains=name))
            queryset_startswith.extend(
                [i for i in queryset_contains if i not in queryset_startswith]
            )
            queryset = queryset_startswith
        return queryset


class RecipeViewSet(ModelViewSet, AddDelViewMixin):
    """
    Вьюсет для работы с рецептами.
    """
    queryset = Recipe.objects.select_related('author')
    serializer_class = RecipeSerializer
    add_serializer = RecipeSmallSerializer
    permission_classes = (AuthorAdminOrReadOnly, )
    pagination_class = PageLimitPagination

    def get_queryset(self):
        queryset = self.queryset

        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(
                tags__slug__in=tags).distinct()

        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author=author)

        user = self.request.user
        if not user.is_authenticated:
            return queryset

        if self.request.query_params.get('is_in_shopping_cart'):
            queryset = queryset.filter(shopping_cart=user.id)
        else:
            queryset = queryset.exclude(shopping_cart=user.id)

        if self.request.query_params.get('is_favorited'):
            queryset = queryset.filter(favorite=user.id)
        else:
            queryset = queryset.exclude(favorite=user.id)

        return queryset

    @action(methods=('GET', 'POST', 'DELETE', ), detail=True)
    def favorite(self, request, pk):
        """
        Добавляет/удалет рецепт в избранное.
        """
        return self.add_del_obj(pk, 'favorite')

    @action(methods=('GET', 'POST', 'DELETE', ), detail=True)
    def shopping_cart(self, request, pk):
        """
        Добавляет/удалет рецепт в список покупок.
        """
        return self.add_del_obj(pk, 'shopping_cart')

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        """
        Загружает файл *.csv со списком покупок.
        Считает сумму ингредиентов в рецептах выбранных для покупки.
        Возвращает csv файл со списком ингредиентов.
        """
        user = self.request.user
        if not user.in_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)
        ingredients = IngredientAmount.objects.filter(
            recipe__in=user.in_cart.values('id')
        ).values(
            ingredient=F('ingredients__name'),
            measure=F('ingredients__measurement_unit')
        ).annotate(
            amount=Sum('amount')
        )

        filename = 'shopping_list.csv'
        create_time = dt.now().strftime('%d.%m.%Y %H:%M')

        shopping_list = (
            f'Список покупок пользователя: {user.first_name}\n'
            f'{create_time}\n\n'
        )
        shopping_list += ('"Ингредиент", "Количество", "Единицы измерения"\n')
        for ingredient in ingredients:
            shopping_list += str.format(
                '"{0}", "{1}", "{2}"\n',
                ingredient['ingredient'],
                ingredient['amount'],
                ingredient['measure']
            )

        shopping_list += '\nСформировано в продуктовом помощнике Foodgram'

        response = HttpResponse(
            shopping_list, content_type='text.csv; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
