from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, views
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from .paginators import CustomPaginator
from .permissions import AuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer, FavoriteRecipeSerializer,
    FavoriteSerializer, IngredientSerializer,
    ShoppingCartSerializer, SubscriptionsSerializer,
    TagSerializer, ViewRecipeSerializer
)
from .utils import get_shopping_list
from users.models import Subscribe, User


class RecipeViewSet(viewsets.ModelViewSet):
    """ Обрабатывает запросы к рецептам"""
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = CustomPaginator
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    filterset_field = ('tags', 'author')
    ordering_field = ('pub_date',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewRecipeSerializer
        return CreateRecipeSerializer

    def post_req(self, request, id, model, serializer):
        user = request.user
        serializer = serializer(data={'user': user.id, 'recipe': id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            FavoriteRecipeSerializer(
                get_object_or_404(Recipe, id=id), context={'request': request}
            ).data, status=status.HTTP_201_CREATED
        )

    def delete_req(self, request, id, model):
        get_object_or_404(
            model, user=request.user, recipe=get_object_or_404(Recipe, id=id)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], permission_classes=(AllowAny,), detail=False)
    def download_shopping_cart(self, request):
        user = request.user
        shopping_list = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount')).order_by()
        return get_shopping_list(self, shopping_list)

    @action(methods=['POST'], detail=True)
    def favorite(self, request, pk):
        return self.post_req(request, pk, Favorite, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_req(request, pk, Favorite)

    @action(methods=['POST'], detail=True)
    def shopping_cart(self, request, pk):
        return self.post_req(request, pk, ShoppingCart, ShoppingCartSerializer)

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
    pagination_class = CustomPaginator

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(subscribing__user=user)


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
