from base64 import b64encode
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import Favorite, RecipeIngredient, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscribe, User


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
        if not request.user:
            return serializers.DjangoValidationError('Не авторизован')
        user = request.user
        return user.subscriber.filter(author=author).exists()


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
        if not request.user:
            return serializers.DjangoValidationError('Не авторизован')
        user = request.user
        if Favorite.objects.filter(user=user, recipe=obj).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user:
            return serializers.DjangoValidationError('Не авторизован')
        user = request.user
        if ShoppingCart.objects.filter(user=user, recipe=obj).exists():
            return True
        return False


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
        if not request.user:
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
        return value

    def validate_ingredients(self, data):
        if len(data) < 1:
            return serializers.ValidationError(
                'Должен быть хотя бы 1 игредиент'
            )
        for ingredient in data:
            if ingredient['amount'] < 1:
                return serializers.ValidationError(
                    'Количество должно быть больше 1'
                )
        return data

    def validate_cooking_time(self, value):
        if value < 1:
            return serializers.ValidationError(
                'Время готовки должно быть больше 1'
            )
        return value
    
    def to_representation(self, instance):
        ingredients = []
        for obj in instance.recipeingredient_set.all():
            ingredients.append({
                'id': obj.ingredient.id,
                'name': obj.ingredient.name,
                'measurement_unit': obj.ingredient.measurement_unit,
                'amount': obj.amount
            })
        tags = []
        for tag in instance.tags.all():
            tags.append(tag.id)
        return {
            'name': instance.name,
            'ingredients': ingredients,
            'tags': tags,
            'text': instance.text,
            'cooking_time': instance.cooking_time,
            'image': instance.image
        }


class FavoriteSerializer(serializers.ModelSerializer):

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
        serializer = FavoriteSerializer(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, author):
        request = self.context.get('request')
        if not request.user:
            return serializers.DjangoValidationError('Не авторизован')
        user = request.user
        if Subscribe.objects.filter(
            author=author, user=user
        ).exists():
            return True
        return False

    def get_recipes_count(self, author):
        return author.recipes.count()
