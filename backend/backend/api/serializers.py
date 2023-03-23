from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (
    Favorite, RecipeIngredient, Ingredient, Recipe, ShoppingCart, Tag
)
from users.models import User


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
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.subscriber.filter(
                author=author
            ).exists()
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class ViewRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True)
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set', many=True
    )
    is_favorited = serializers.SerializerMethodField()
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
            'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
            request
            and self.context.get('request').user.is_authenticated
            and self.context.get('request').user.favorite.filter(
                recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.shopping_cart.filter(
                recipe=obj
            ).exists()
        )


class AddIngForRecSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = AddIngForRecSerializer(many=True)
    image = Base64ImageField(represent_in_base64=True)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'ingredients',
            'cooking_time',
            'image',
            'name',
            'text'
        )

    def create_ingredients(self, ingredients, recipe):
        objs = [
            RecipeIngredient(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        request = self.context.get('request')
        if not request.user.is_authenticated:
            return serializers.DjangoValidationError('Не авторизован')
        user = request.user
        author = user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data, author=author)
        self.create_ingredients(ingredients, recipe)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def update(self, recipe, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            recipe.ingredients.clear()
            self.create_ingredients(ingredients, recipe)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            recipe.tags.set(tags_data)
        return super().update(recipe, validated_data)

    def validate_tag(self, value):
        if len(value) < 1:
            return serializers.ValidationError('Должен быть хотя бы один тэг')
        if len(value) > len(set(value)):
            return serializers.ValidationError('Тэги должны быть уникальными')
        return value

    def validate_ingredients(self, data):
        if len(data) < 1:
            return serializers.ValidationError(
                'Должен быть хотя бы 1 игредиент'
            )
        check_ingredients = []
        for ingredient in data:
            check_ingredients.append(ingredient['id'])
            if ingredient['amount'] < 1:
                return serializers.ValidationError(
                    'Количество должно быть больше 1'
                )
        if len(check_ingredients) > len(set(check_ingredients)):
            return serializers.ValidationError(
                'Ингредиенты должны быть уникальными'
            )
        return data

    def validate_cooking_time(self, value):
        if value < 1:
            return serializers.ValidationError(
                'Время готовки должно быть больше 1'
            )
        return value

    def to_representation(self, instance):
        return ViewRecipeSerializer(instance).data


class FavoriteRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionsSerializer(serializers.ModelSerializer):
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
        recipes = author.recipes.all()
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        limit = request.query_params.get('limit')
        if limit:
            recipes = recipes[:int(limit)]
        return FavoriteRecipeSerializer(recipes, many=True).data

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.subscriber.filter(
                author=author
            ).exists()
        )

    def get_recipes_count(self, author):
        return author.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.favorite.filter(recipe=recipe).exists():
            return serializers.ValidationError('Уже есть')
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        user = data['user']
        recipe = data['recipe']
        if user.shopping_cart.filter(recipe=recipe).exists():
            return serializers.ValidationError('Уже есть')
        return data
