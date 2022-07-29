"""Модуль описания пермишенов."""
from rest_framework.permissions import (BasePermission,
                                        IsAuthenticatedOrReadOnly)


class AuthorAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    """Автору и администраторам разрешено всё, остальным только чтение."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET', )
            or (
                request.user.is_authenticated
                and (
                    request.user.is_superuser
                    or request.user == obj.author
                )
            )
        )


class AdminOrReadOnly(BasePermission):
    """Админу можно всё, остальным только чтение."""
    def has_permission(self, request, view):
        return (
            request.method in ('GET', )
            or (
                request.user.is_authenticated
                and request.user.is_superuser
            )
        )


class AdminOwnerOrReadOnly(IsAuthenticatedOrReadOnly):
    """Владельцу учётки и админу можно всё, остальным только чтение."""
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET', )
            or (
                request.user.is_authenticated
                and (
                    request.user.is_superuser
                    or request.user == obj
                )
            )
        )
