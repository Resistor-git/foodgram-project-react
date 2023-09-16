import base64
import sys

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import F
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from users.models import (
    CustomUser,
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


User = get_user_model()  # оно подхватывает кастомную модель CustomUser?


class CustomUserCreateSerializer(UserCreateSerializer):
    """Custom serializer to create a user.
    In default serializer not all fields are obligatory."""
    # указывается в settings.py
    # https://www.youtube.com/watch?v=lFD5uoCcvSA&t=105s

    class Meta:
        # model = CustomUser
        model = User  # надо ли указывать кастомную модель?
        fields = (
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
        return Subscription.objects.filter(user=current_user, author=obj).exists()


# class CustomUserPasswordSerializer(UserSerializer):
#     new_password = serializers.CharField()
#     current_password = serializers.CharField()
#     class Meta:
#         model = User
#         fields = (
#             'new_password',
#             'current_password'
#         )


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


# этот для создания пробовал
class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Returns id, name,  measurement unit of ingredient from Ingredient model,
    and amount from RecipeIngredient model"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)  # read_only нельзя добавлять, а то ломается
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  'ingredients', 'tags', 'cooking_time',)

    def create(self, validated_data):
        print(f'!!!attempt to create recipe!!!', flush=True)
        # print(f'!!!validated data: {validated_data}', flush=True)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        # print(f'!!!ingredients: {ingredients}!!!', flush=True)
        # print('!!!validated_data after pop:', validated_data, flush=True)
        # recipe_created = super().create(validated_data)
        recipe_created = Recipe.objects.create(**validated_data)
        # print('!!!recipe_created отработал!!!', flush=True)
        self.add_ingredients(recipe_created, ingredients)
        # print('!!!add_ingredients отработал!!!', flush=True)
        self.add_tags(recipe_created, tags)
        return recipe_created

    def update(self, instance, validated_data):
        """Updates the recipe.
        Partial update is possible."""
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        ingredients = validated_data.pop('ingredients', None)
        # print(f'!!!ingredients: {ingredients}!!!', flush=True)
        tags = validated_data.pop('tags', None)
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.add_ingredients(instance, ingredients)
        if tags:
            self.add_tags(instance, tags)
        return super().update(instance, validated_data)

    def add_ingredients(self, recipe, ingredients):
        """Used by create method to add ingredients and amounts to recipe"""
        # print('!!!recipe:', recipe, flush=True)
        # print('!!!ingredients(again):', ingredients, flush=True)
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
        # print('!!!!', instance, flush=True)
        return RecipeListRetrieveSerializer(instance, context=context).data

    def validate(self, data):
        all_ingredients = data.get('ingredients')
        # print('!!!!all_ingredients:', all_ingredients, flush=True)
        unique_ingredients= []
        for ingredient in all_ingredients:
            print('!!!!ingredient:', ingredient, flush=True)
            unique_ingredients.append(ingredient['id'])
        # print('!!!!unique_ingredients:', unique_ingredients, flush=True)
        if len(all_ingredients) > len(set(unique_ingredients)):
            raise serializers.ValidationError("Ingredients must be unique")
        return data


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    author = CustomUserRetrieveSerializer(read_only=True)  # read_only надо ли?
    ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipeingredient_set')
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)  # написать метод

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image', 'ingredients',
                  'tags', 'cooking_time', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        current_user = self.context.get('request').user
        return Favorite.objects.filter(user=current_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        current_user = self.context.get('request').user
        return ShoppingCart.objects.filter(user=current_user, recipe=obj).exists()


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
        recipes_limit = request.GET.get('recipes_limit', 1)  #todo убрать дефолтное магическое число
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

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeShortListRetrieveSerializer(instance['recipe'], context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = ('id', 'user', 'recipe')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeShortListRetrieveSerializer(instance['recipe'], context=context).data


# class ShoppingCartDownloadSerializer(serializers.ModelSerializer):
#     ingredients = RecipeIngredientSerializer(many=True, read_only=True, source='recipeingredient_set')
#
#     class Meta:
#         model = ShoppingCart
#         # fields = ('name', 'measurement_unit', ' amount')
#         fields = ('ingredients',)