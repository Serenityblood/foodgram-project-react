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
        through='IngForRec'
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


class IngForRec(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='ing_for_rec'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ing_for_rec'
    )
    amount = models.IntegerField(blank=False)


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorite'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unqiue_favorite'
            )
        ]


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_card'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_card'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_card'
            )
        ]
