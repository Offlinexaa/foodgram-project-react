from string import hexdigits

from rest_framework.serializers import ValidationError


def class_obj_validate(value: str, klass: object = None) -> object:
    """
    Проверка корректности переданного значения.

    Если передан класс, проверяет существует ли объект с переданным id.
    При нахождении объекта создаётся Queryset[] из которого
    для дальнейшей работы возвращается первое значение.
    """
    if not str(value).isdecimal():
        raise ValidationError(
            f'Строка {value} должна содержать число.'
        )
    if klass:
        obj = klass.objects.filter(id=value)
        if not obj:
            raise ValidationError(
                f'Обекта {type(klass)} с ID={value} не существует.'
            )
        return obj[0]


def hex_color_validate(value: str) -> None:
    """
    Проверка соответствия переданного числа шестнадцатиричному формату цвета.
    """
    if len(value) not in (3, 6):
        raise ValidationError(
            f'Длинна {value} не кратна 3.'
        )
    if not set(value).issubset(hexdigits):
        raise ValidationError(
            f'{value} не шестнадцатиричное.'
        )
