from django.contrib import admin

from .models import Favorite, Ingredient, IngForRec, ShoppingCard, Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author', 'tags')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Tag)
admin.site.register(IngForRec)
admin.site.register(ShoppingCard)
admin.site.register(Favorite)
