from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    email = models.CharField(
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        max_length=settings.USERNAME_SIZE,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField(
        max_length=settings.USERNAME_SIZE
    )
    last_name = models.CharField(
        max_length=settings.USERNAME_SIZE
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscribe',
            ),
            models.CheckConstraint(
                name='prevent_self_subscribe',
                check=~models.Q(user=models.F('author'))
            )
        ]
