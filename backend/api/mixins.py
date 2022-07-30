"""Модуль описания миксинов."""
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED)


class AddDelViewMixin:
    """
    Миксин содержит методы добавления/удаления объекта связи типа
    "многие-ко-многим".
    """

    add_serializer = None

    def add_del_obj(self, obj_id, manager):
        """
        Добавляет/удаляет связь через менеджер "модель.имя_поля_связи".
        """
        user = self.request.user
        if user.is_anonymous:
            return Response(status=HTTP_401_UNAUTHORIZED)

        MANAGERS = {
            'subscribe': user.subscription,
            'favorite': user.favorites,
            'shopping_cart': user.in_cart,
        }

        manager = MANAGERS[manager]

        obj = get_object_or_404(self.queryset, id=obj_id)
        serializer = self.add_serializer(
            obj,
            context={'request': self.request}
        )
        exists = manager.filter(id=obj_id).exists()

        if not exists and self.request.method in ('GET', 'POST', ):
            manager.add(obj)
            return Response(serializer.data, status=HTTP_201_CREATED)

        if exists and self.request.method in ('DELETE', ):
            manager.remove(obj)
            return Response(status=HTTP_204_NO_CONTENT)

        return Response(status=HTTP_400_BAD_REQUEST)
