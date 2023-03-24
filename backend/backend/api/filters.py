from django_filters import AllValuesMultipleFilter, CharFilter, FilterSet
from django_filters import rest_framework as filters
from django_filters.widgets import BooleanWidget

from .models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart', widget=BooleanWidget()
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited', widget=BooleanWidget()
    )
    tags = AllValuesMultipleFilter(field_name='tags__slug')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorite__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = [
            'tags__slug', 'is_favorited', 'is_in_shopping_cart', 'author'
        ]


class IngredientFilter(FilterSet):
    name = CharFilter(
        label='name',
        field_name='name',
        lookup_expr='incontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
