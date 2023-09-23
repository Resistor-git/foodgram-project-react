import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import (
    Subscription,
)
from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    RecipeIngredient,
    Favorite,
    ShoppingCart
)

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Custom serializer to create a user.
    In default serializer not all fields are obligatory."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'email',
            'first_name',
            'last_name',
        )


class CustomUserRetrieveSerializer(UserSerializer):
    """Shows the info about the user."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        current_user = self.context.get('request').user
        return Subscription.objects.filter(
            user=current_user,
            author=obj
        ).exists()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Returns id, name,  measurement unit of ingredient from Ingredient model,
    and amount from RecipeIngredient model"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  'ingredients', 'tags', 'cooking_time',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe_created = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe_created, ingredients)
        self.add_tags(recipe_created, tags)
        return recipe_created

    def update(self, instance, validated_data):
        """Updates the recipe.
        Partial update is possible."""
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.add_ingredients(instance, ingredients)
        if tags:
            self.add_tags(instance, tags)
        return super().update(instance, validated_data)

    def add_ingredients(self, recipe, ingredients):
        """Used by create method to add ingredients and amounts to recipe"""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                amount=ingredient['amount'],
            ) for ingredient in ingredients
        )

    def add_tags(self, recipe, tags):
        recipe.tags.set(tags)

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeListRetrieveSerializer(instance, context=context).data

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(
                'Ingredients should not be empty'
            )
        unique_ingredients = []
        for ingredient in value:
            unique_ingredients.append(ingredient['id'])
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    'Amount of ingredient can not be less than 1'
                )
            if not Ingredient.objects.filter(pk=ingredient['id']).exists():
                raise serializers.ValidationError(
                    f'Ingredient with id {ingredient["id"]} does not exist'
                )
        if len(value) > len(set(unique_ingredients)):
            raise serializers.ValidationError('Ingredients must be unique')
        return value

    def validate_tags(self, value):
        unique_tags = set(value)
        if len(value) > len(unique_tags):
            raise serializers.ValidationError('Tags must be unique')
        return value


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    author = CustomUserRetrieveSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipeingredient_set'
    )
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author',
                  'image', 'ingredients', 'tags', 'cooking_time',
                  'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        current_user = self.context.get('request').user
        return Favorite.objects.filter(user=current_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        current_user = self.context.get('request').user
        return ShoppingCart.objects.filter(
            user=current_user,
            recipe=obj
        ).exists()


class RecipeShortListRetrieveSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(CustomUserRetrieveSerializer):
    """Provides information about the author and their recipes"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name',
                            'last_name', 'is_subscribed')

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        recipes_limit = request.GET.get('recipes_limit', 3)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
            return RecipeShortListRetrieveSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeShortListRetrieveSerializer(
            instance['recipe'], context=context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeShortListRetrieveSerializer(
            instance['recipe'], context=context
        ).data

    def validate_recipe(self, value):
        if not Recipe.objects.filter(pk=value.id).exists():
            raise serializers.ValidationError(
                f'Ingredient with id {value.id} does not exist'
            )
        return value
