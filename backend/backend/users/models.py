from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    email = models.CharField(
        'Почта',
        max_length=settings.EMAIL_SIZE,
        unique=True,
    )
    username = models.CharField(
        'Никнейм',
        max_length=settings.USERNAME_SIZE,
        unique=True,
        validators=[validate_username]
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.USERNAME_SIZE
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USERNAME_SIZE
    )
    USERNAME_FIELD = ('email')
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    def __str__(self):
        return f'{self.username}'

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscribe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriber',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribing',
        verbose_name='Автор'
    )

    def __str__(self) -> str:
        return f'{self.user} on {self.author}'

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
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
