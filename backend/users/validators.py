"""Модуль содержит валидаторы, применяемые в приложении users"""
from re import match

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class MinLengthValidator:
    """Проверяет длинну."""
    min_length = 0
    message = 'Значение слишком короткое.'

    def __init__(self, min_length: int = None, message: str = None) -> None:
        if min_length:
            self.min_length = min_length
        if message:
            self.message = message

    def __call__(self, value: str) -> None:
        if len(value) < self.min_length:
            raise ValidationError(self.message)


@deconstructible
class RegexValidator:
    """Проверяет на соответствие регулялярному выражению."""
    regex = r'^[\w.@+-]+\Z'
    message = ('Значение поля содержит недопустимые символы.')

    def __init__(self, regex: str = None, message: str = None) -> None:
        if regex:
            self.regex = regex
        if message:
            self.message = message

    def __call__(self, value: str) -> None:
        if not match(
            pattern=self.regex,
            string=value
        ):
            raise ValidationError(self.message)
