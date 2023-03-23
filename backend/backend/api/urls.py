from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APISubscribe,
    IngredientViewSet, RecipeViewSet,
    ListSubscriptions, TagViewSet
)


app_name = 'api'

router = DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'users/<int:id>/subscribe/', APISubscribe.as_view(), name='subscribe'
    ),
    path(
        'users/subscriptions/',
        ListSubscriptions.as_view(),
        name='subscriptions'
    )
]
