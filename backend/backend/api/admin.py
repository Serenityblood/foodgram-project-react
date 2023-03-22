from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    Favorite, Ingredient, ShoppingCart, Recipe, RecipeIngredient, Tag
)


class IngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInLine, ]
    list_display = ('name', 'author', 'get_ingredients', 'get_favorite_count')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')

    def get_ingredients(self, obj):
        return (
            ', '.join(
                [ingredient.__str__() for ingredient in obj.ingredients.all()]
            )
        )

    def get_favorite_count(self, obj):
        return obj.favorite.count()

    get_favorite_count.short_description = 'Количество избранных'
    get_ingredients.short_description = 'Ингредиенты'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
admin.site.unregister(Group)
