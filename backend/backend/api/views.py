from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from .permissions import AuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer, FavoriteSerializer, IngredientSerializer,
    SubscriptionsSerializer,
    TagSerializer, UserSerializer, ViewRecipeSerializer
)
from .utils import get_shopping_list
from users.models import Subscribe, User


class RecipeViewSet(viewsets.ModelViewSet):
    """ Обрабатывает запросы к рецептам"""
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    filterset_field = ('tags', 'author')
    ordering_field = ('pub_date',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewRecipeSerializer
        return CreateRecipeSerializer

    def post_req(self, request, id, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.get_or_create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_req(self, request, id, model):
        get_object_or_404(
           model, user=request.user, recipe=get_object_or_404(Recipe, id=id)
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], permission_classes=(AllowAny,), detail=False)
    def download_shopping_cart(self, request):
        return get_shopping_list(self, request)

    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk):
        return self.post_req(request, pk, Favorite)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_req(request, pk, Favorite)

    @action(methods=['POST'], detail=True)
    def shopping_cart(self, request, pk):
        return self.post_req(request, pk, ShoppingCart)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_req(request, pk, ShoppingCart)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    http_method_names = ['get']


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny,)
    http_method_names = ['get']
    serach_fields = ('^name')


class ListSubscriptions(viewsets.ModelViewSet):
    serializer_class = SubscriptionsSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(subscribing__user=user)


def delete(request, id, model):
    user = request.user
    recipe = get_object_or_404(model, id=id)
    obj = get_object_or_404(model, user=user, recipe=recipe)
    obj.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def post(request, id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
    model.objects.get_or_create(user=user, recipe=recipe)
    serializer = FavoriteSerializer(recipe, context={'request': request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class APISubscribe(views.APIView):
    def post(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        Subscribe.objects.get_or_create(user=user, author=author)
        serializer = SubscriptionsSerializer(author, context={'request':
                                                              request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        get_object_or_404(
           Subscribe, user=request.user, author=get_object_or_404(User, id=id)
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class APIShoppingCard(views.APIView):
    def post(self, request, id):
        return post(request, id, ShoppingCart)

    def delete(self, request, id):
        return delete(request, id, ShoppingCart)

