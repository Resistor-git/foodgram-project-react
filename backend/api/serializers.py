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


# почему у меня тут вообще такие поля???
# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     # это чтобы можно было добавить к рецепту ингридиенты и их количество, хз правильно ли
#     # id брать ингридиента или связи RecipeIngredient?
#     # id = serializers.PrimaryKeyRelatedField(source='ingredient.id', read_only=True)
#     # name = serializers.CharField(source='ingredient.name', read_only=True)  # в RecipeIngredient есть поле ingredient, оно ссылается на модель Ingredient у которой есть name
#     # measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)
#     # amount = serializers.IntegerField()
#     id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
#     # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all().values('id'))  # ?? или RecipeIngredient
#     name = serializers.CharField(source='ingredient.name', read_only=True)  # в RecipeIngredient есть поле ingredient, оно ссылается на модель Ingredient у которой есть name
#     measurement_unit = serializers.CharField(source='ingredient.measurement_unit', read_only=True)
#     amount = serializers.IntegerField()
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'name', 'measurement_unit', 'amount')

# этот для создания пробовал
class RecipeIngredientSerializer(serializers.ModelSerializer):
    # ХЗ ХЗ ХЗ
    # это чтобы можно было добавить к рецепту ингридиенты и их количество
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    # ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    ingredient = IngredientSerializer

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'ingredient', 'amount')


class IngredientAmountSerializer(serializers.ModelSerializer):
    # id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all().values_list('id', flat=True))  # id ингредиента
    # id = serializers.PrimaryKeyRelatedField(source='ingredient.id', read_only=True)
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')



# class RecipeIngredientAddSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(
#         source='ingredient.id',
#         queryset=Ingredient.objects.all()
#     )
#
#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount')


### хороший был бы код, если бы работал
class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)  # правильно ли этот сериализатор использовать или RecipeIngredient?
    # tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # так на вебинаре советовали 1:19 #  этой строкой в validated data нет тегов
    image = Base64ImageField()
    author = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  'ingredients', 'tags', 'cooking_time',)

    def create(self, validated_data):
        print(f'!!!attempt to create recipe!!!', flush=True)
        print(f'!!!validated data: {validated_data}', flush=True)
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        print(f'!!!ingredients: {ingredients}!!!', flush=True)
        print('!!!validated_data after pop:', validated_data, flush=True)
        # recipe_created = super().create(validated_data)
        recipe_created = Recipe.objects.create(**validated_data)
        print('!!!recipe_created отработал!!!', flush=True)
        self.add_ingredients(recipe_created, ingredients)
        # for ingredient in ingredients:
        #     ingredient_obj = Ingredient.objects.get(pk=1)  # хардкод
        #     RecipeIngredient.objects.create(
        #         recipe=recipe_created, ingredient=ingredient_obj, amount=1
        #     )
        print('!!!add_ingredients отработал!!!', flush=True)
        self.add_tags(recipe_created, tags)
        return recipe_created

    def add_ingredients(self, recipe, ingredients):
        """Used by create method to add ingredients and amounts to recipe"""
        print('!!!recipe:', recipe, flush=True)
        print('!!!ingredients(again):', ingredients, flush=True)
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
        print('!!!!', instance, flush=True)
        return RecipeListRetrieveSerializer(instance, context=context).data

        # for ingredient in ingredients:
        #     ingredient = Ingredient.objects.get(pk=ingredient['id'])
        #     amount = ingredient['amount']
        #     RecipeIngredient.objects.create(
        #         recipe=recipe, ingredient=ingredient, amount=amount
        #     )


# class RecipeCreateSerializer(serializers.ModelSerializer):
#     ingredients = IngredientAmountSerializer(many=True)  # правильно ли эту модель использовать?
#     # ingredients = RecipeIngredientAddSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # так на вебинаре советовали 1:19
#     image = Base64ImageField()
#     author = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     # author = CustomUserRetrieveSerializer
#     # author = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), read_only=True)
#
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'text', 'author', 'image',
#                   'ingredients', 'tags', 'cooking_time',)
#
#     # def create(self, validated_data):
#     #     ingredients = validated_data.pop('ingredients')
#     #     # recipe_created = super().create(validated_data)
#     #     recipe_created = Recipe.objects.create(**validated_data)
#     #     self.add_ingredients(recipe_created, ingredients)
#     #     # for ingredient in ingredients:
#     #     #     ingredient_obj = Ingredient.objects.get(pk=1)  # хардкод
#     #     #     RecipeIngredient.objects.create(
#     #     #         recipe=recipe_created, ingredient=ingredient_obj, amount=1
#     #     #     )
#     #     return recipe_created
#
#     ## очередная попытка https://app.pachca.com/chats/3891156?thread_id=1796376
#
#     def to_representation(self, instance):
#         request = self.context.get('request')
#         context = {'request': request}
#         return RecipeListRetrieveSerializer(instance, context=context).data
#
#     def create_bulk(self, recipe, ingredients_data):
#         RecipeIngredient.objects.bulk_create(
#             [
#                 RecipeIngredient(
#                     ingredient=Ingredient.objects.get(id=ingredient['id']),
#                     recipe=recipe,
#                     amount=ingredient['amount']
#                     # amount=F('amount')
#                 ) for ingredient in ingredients_data
#             ]
#         )
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         ingredients_data = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(**validated_data)
#         recipe.save()
#         self.create_bulk(recipe, ingredients_data)
#         return recipe


# создаёт... но без ингредиентов...
# class RecipeCreateSerializer(serializers.ModelSerializer):
#     ingredients = IngredientAmountSerializer(many=True, read_only=True)  # правильно ли эту модель использовать?
#     # ingredients = RecipeIngredientAddSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # так на вебинаре советовали 1:19
#     image = Base64ImageField()
#     author = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     # author = CustomUserRetrieveSerializer
#     # author = serializers.PrimaryKeyRelatedField(default=serializers.CurrentUserDefault(), read_only=True)
#
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'text', 'author', 'image',
#                   'ingredients', 'tags', 'cooking_time',)
#
#     def get_ingredients(self, recipe):
#         ingredients = recipe.ingredients.values(
#             'id', 'name', 'measurement_unit', amount=F('ingredient_recipe__amount')
#         )
#         return ingredients


class RecipeListRetrieveSerializer(serializers.ModelSerializer):
    author = CustomUserRetrieveSerializer(read_only=True)  # read_only надо ли?
    # ingredients = RecipeIngredientSerializer(many=True, read_only=True) # хз правильно ли эту модель использовать, нужно количество ингридиентов
    # tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # так на вебинаре советовали
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)  # написать метод
    # is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)  # написать метод

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  # 'ingredients',
                  'tags', 'cooking_time', 'is_favorited')

    def get_is_favorited(self, obj):
        if not self.context.get('request').user.is_authenticated:
            return False
        current_user = self.context.get('request').user
        return Favorite.objects.filter(user=current_user, recipe=obj).exists()
    # def get_ingredients(self, recipe):
    #     ingredients = recipe.ingredients.values(
    #         'id',
    #         'name',
    #         'measurement_unit',
    #     )


# class RecipeCreateSerializer(RecipeListRetrieveSerializer):
#     ingredients = RecipeIngredientSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
#     image = Base64ImageField()
#     author = serializers.HiddenField(default=serializers.CurrentUserDefault())
#
#     def create(self, validated_data):
#         # author = self.context['request'].user
#         ingredients_data = validated_data.pop('ingredients')
#         recipe = Recipe.objects.create(**validated_data)
#         ingredients_list = []
#         for ingredient_data in ingredients_data:
#             ingredient = Ingredient.objects.get(id=ingredient_data['id'])
#             amount = ingredient_data['amount']
#             recipe_ingredient = RecipeIngredient(recipe=recipe, ingredient=ingredient, amount=amount)
#             ingredients_list.append(recipe_ingredient)
#         RecipeIngredient.objects.bulk_create(ingredients_list)
#         return recipe


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
    # recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('id', 'user', 'recipe')

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        # print('!!!!', instance['recipe'], flush=True)
        return RecipeShortListRetrieveSerializer(instance['recipe'], context=context).data

