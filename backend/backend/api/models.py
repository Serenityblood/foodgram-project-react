from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.NAME_SIZE,
        unique=True,
        blank=False
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        default='#ffffff',
        unique=True,
        blank=False
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.NAME_SIZE,
        unique=True,
        blank=False
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} - {self.slug}'


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.NAME_SIZE,
        blank=False
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=10,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unqiue_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    image = models.ImageField(
        'Фото',
        upload_to='recipe/images/',
        null=False,
        default=None,
        blank=False
        )
    name = models.CharField(
        'Название',
        max_length=settings.NAME_SIZE,
        blank=False,
    )
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        verbose_name='Тэги'
    )
    text = models.TextField(
        'Описание',
        blank=False
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время готовки',
        validators=[MinValueValidator(1, message=('Не может быть меньше 1'))],
        blank=False
    )
    pub_date = models.DateField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1, message=('Не может быть меньше 1'))],
        blank=False
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'

    def __str__(self):
        return f'{self.ingredient} - {self.recipe}'


class FavoriteShoppingCartModel(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('recipe',)

    def __str__(self) -> str:
        return f'{self.user} - {self.recipe}'


class Favorite(FavoriteShoppingCartModel):
    class Meta(FavoriteShoppingCartModel.Meta):
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorite'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unqiue_favorite'
            )
        ]


class ShoppingCart(FavoriteShoppingCartModel):
    class Meta(FavoriteShoppingCartModel.Meta):
        verbose_name = 'Лист покупок'
        verbose_name_plural = 'Листы покупок'
        default_related_name = 'shopping_cart'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
