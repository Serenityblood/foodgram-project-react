import re

from django.conf import settings
from django.core import exceptions


def validate_username(value):
    if value == 'me':
        raise exceptions.ValidationError('Нельзя использовать me')
    prog = re.sub(settings.ALLOWED_SYMBOLS, repl='', string=value)
    if prog:
        string_val = ', '.join(set(prog))
        raise exceptions.ValidationError(f'Запрещённые символы: {string_val}')
    return value
