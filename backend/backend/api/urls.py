from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    APIFavorite, APIShoppingCard, APISubscribe,
    IngredientViewSet, login,
    logout, RecipeViewSet,
    ListSubscriptions, TagViewSet, UserViewSet
)


app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(
    'users/subscriptions', ListSubscriptions, basename='subscriptions'
)

auth_patterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout')
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(router.urls)),
    path(
        'users/<int:id>/subscribe/', APISubscribe.as_view(), name='subscribe'
    ),
    path('recipes/<int:id>/shopping_cart/', APIShoppingCard.as_view()),
    path('recipes/<int:id>/favorite/', APIFavorite.as_view()),
]
