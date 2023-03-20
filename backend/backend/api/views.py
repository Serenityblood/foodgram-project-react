from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, views
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .filters import IngredientSearchFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCard, Tag
from .permissions import AuthorOrReadOnly
from .serializers import (
    CreateRecipeSerializer, FavoriteSerializer, IngredientSerializer,
    LoginSerizlizer,
    MeSerializer, PasswordResetSerializer, SubcriptionsSerializer,
    TagSerializer, UserSerializer, ViewRecipeSerializer
)
from .utils import get_shopping_list
from users.models import Subscribe


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(methods=['GET', 'PATCH'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        """Обрабатывает запросы к users/me."""
        user = request.user
        if request.method == "GET":
            serializer = UserSerializer(user)
            return Response(serializer.data)
        serializer = MeSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['POST'], detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """ Смена пароля"""
        user = get_object_or_404(User, username=request.user)
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user.check_password(serializer.validated_data['current_password']):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class RecipeViewSet(viewsets.ModelViewSet):
    """ Обрабатывает запросы к рецептам"""
    queryset = Recipe.objects.all()
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    filterset_field = ('tags', 'author')
    ordering_field = ('id')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ViewRecipeSerializer
        return CreateRecipeSerializer

    @action(methods=['GET'], permission_classes=(AllowAny,), detail=False)
    def download_shopping_cart(self, request):
        return get_shopping_list(self, request)


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
    filter_backends = (IngredientSearchFilter,)
    serach_fields = ('^name')


@api_view(['POST'],)
def login(request):
    serializer = LoginSerizlizer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        email=serializer.validated_data['email'],
    )
    if user.check_password(serializer.validated_data['password']):
        token = AccessToken.for_user(user)
        return Response(
            {'auth_token': f'{token}'}, status=status.HTTP_201_CREATED
        )
    return Response({'error': 'Incorrect password'})


@api_view(['POST'],)
def logout(request):
    token = RefreshToken.for_user(request.user)
    token.blacklist()
    return Response(status=status.HTTP_201_CREATED)


class ListSubscriptions(viewsets.ModelViewSet):
    serializer_class = SubcriptionsSerializer

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


def delete(request, id, model):
    user = request.user
    recipe = get_object_or_404(Recipe, id=id)
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
        return post(request, id, Subscribe)

    def delete(self, request, id):
        return delete(request, id, Subscribe)


class APIShoppingCard(views.APIView):
    def post(self, request, id):
        return post(request, id, ShoppingCard)

    def delete(self, request, id):
        return delete(request, id, ShoppingCard)


class APIFavorite(views.APIView):
    def post(self, request, id):
        return post(request, id, Favorite)

    def delete(self, request, id):
        return delete(request, id, Favorite)
