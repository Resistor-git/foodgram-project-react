import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
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
)


User = get_user_model()  # оно подхватывает кастомную модель CustomUser?


# создать отдельный сериализатор для отображения инфы о пользователе?
# весь огород с кастомными пользователями нужен чтобы показывать подписки... вроде бы
# class UserCreateSerializer(UserCreateSerializer):
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


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # это чтобы можно было добавить к рецепту ингридиенты и их количество, хз правильно ли
    # id брать ингридиента или связи RecipeIngredient?
    # id = serializers.PrimaryKeyRelatedField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')  # в RecipeIngredient есть поле ingredient, оно ссылается на модель Ingredient у которой есть name
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    # amount пишут через какой-то F'чотатам__amount' или типа того. что за F?

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, read_only=True)  # хз правильно ли эту модель использовать
    tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # так на вебинаре советовали 1:19
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  'ingredients', 'tags', 'cooking_time',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe_created = super().create(validated_data)
        self.get_ingredients(recipe_created, ingredients)
        return recipe_created

    def get_ingredients(self, recipe, ingredients):
        """Used by create method to add ingredients and amounts to recipe"""
        # RecipeIngredient.objects.bulk_create(
        #     RecipeIngredient(
        #         recipe=recipe,
        #         ingredient=Ingredient.objects.get(pk=ingredient['id']),
        #         amount=ingredient['amount']
        #     ) for ingredient in ingredients
        # )
        for ingredient in ingredients:
            RecipeIngredient.objects.bulk_create(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(pk=ingredient['id']),
                    amount=ingredient['amount']
                )
            )

    # def create(self, validated_data):  # практически копипаст из вебинара 1:20
    #     # при создании рецепта создаётся запись связывающая рецепт и ингредиенты
    #     ingredients = validated_data.pop('ingredients')
    #     for ingredient in ingredients:
    #         RecipeIngredient(recipe=self.instance, ingredient=ingredient['id'], amount=ingredient['amount'])  # хз
    #     super().create(validated_data)
    #
    # def update(self, instance, validated_data):
    #     # ???
    #     self.ingredients.all().delete()
    #     ingredients = validated_data.pop('ingredients')
    #     for ingredient in ingredients:
    #         RecipeIngredient(recipe=self.instance, ingredient=ingredient['id'], amount=ingredient['amount'])  # хз
    #     super().validated_data()


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    author = CustomUserRetrieveSerializer(read_only=True)  # read_only надо ли?
    ingredients = RecipeIngredientSerializer(many=True, read_only=True) # хз правильно ли эту модель использовать, нужно количество ингридиентов
    # tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # так на вебинаре советовали
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    # is_favorited = serializers.SerializerMethodField(read_only=True)  # написать метод
    # is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)  # написать метод

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  'ingredients', 'tags', 'cooking_time')

    # def get_ingredients(self, recipe):
    #     ingredients = recipe.ingredients.values(
    #         'id',
    #         'name',
    #         'measurement_unit',
    #     )


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
