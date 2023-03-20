from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Favorite, IngForRec, Ingredient, Recipe, ShoppingCard, Tag
from .utils import Base64ImageField
from users.models import Subscribe

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        user = self.context['request'].user
        if (user.is_authenticated and Subscribe.objects.filter(
                user=user,
                author=author).exists()):
            return True
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngForRecSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit")

    class Meta:
        model = IngForRec
        fields = ("id", "name", "measurement_unit", "amount")


class ViewRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngForRecSerializer(source='ing_for_rec', many=True)
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'cooking_time',
            'image',
            'name',
            'text',
            'is_favorite',
            'is_in_shopping_cart'
        )

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, recipe=obj).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if ShoppingCard.objects.filter(user=user, recipe=obj).exists():
            return True
        return False


class AddIngForRecSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = IngForRec
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, ingredient):
        return ingredient.ingredient.name

    def get_measurement_unit(self, ingredient):
        return ingredient.ingredient.measurement_unit


class CreateRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AddIngForRecSerializer(source='ing_for_rec', many=True)
    image = Base64ImageField()
    is_favorite = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'tags',
            'ingredients',
            'cooking_time',
            'image',
            'name',
            'text'
        )

    def create_ingredients(self, ingredients, recipe):
        for ing in ingredients:
            current_ing = ing['id']
            IngForRec.objects.create(
                ingredient=current_ing,
                recipe=recipe,
                amount=ing['amount']
            )

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ing_for_rec')
        recipe = Recipe.objects.create(**validated_data, author=author)
        self.create_ingredients(ingredients, recipe)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, recipe, validated_data):
        if 'ing_for_rec' in validated_data:
            ingredients = validated_data.pop('ing_for_rec')
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        if Favorite.objects.filter(user=user, recipe=obj).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if ShoppingCard.objects.filter(user=user, recipe=obj).exists():
            return True
        return False


class LoginSerizlizer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=settings.EMAIL_SIZE,
    )
    password = serializers.CharField(
        max_length=150
    )


class MeSerializer(UserSerializer):
    """Сериализатор для users/me."""

    class Meta(UserSerializer.Meta):
        fields = '__all__'


class PasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubcriptionsSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username',
            'email', 'first_name',
            'last_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )

    def get_recipes(self, author):
        return author.recipes.all()

    def get_is_subscribed(self, author):
        if Subscribe.objects.filter(
            author=author, user=self.context['request'].user
        ).exists():
            return True
        return False

    def get_recipes_count(self, author):
        return author.recipes.count()
