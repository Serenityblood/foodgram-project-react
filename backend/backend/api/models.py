from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=10,
        unique=True,
        blank=False
    )
    color = models.CharField(
        max_length=7,
        default='#ffffff',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        max_length=10,
        unique=True,
        blank=False
    )


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        blank=False
    )
    amount = models.IntegerField()
    measurement_unit = models.CharField(max_length=10)


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=False, 
        default=None,
        blank=False
        )
    name = models.CharField(
        max_length=200,
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False
    )
    text = models.TextField(
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, message=('Не может быть меньше 1'))],
        blank=False
    )


# class Follow(models.Model):
#    user = models.ForeignKey(
#        User, on_delete=models.CASCADE, related_name='follower'
#    )
#    following = models.ForeignKey(
#        User, on_delete=models.CASCADE, related_name='following'
#    )

#    class Meta:
#        constraints = [
#            models.UniqueConstraint(
#                fields=['user', 'following'],
#                name='unique_follow',
#            ),
#            models.CheckConstraint(
#                name='prevent_self_follow',
#                check=~models.Q(user=models.F('following'))
#            )
#        ]