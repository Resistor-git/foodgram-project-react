import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from users.models import (
    CustomUser,
    Follow,
)
from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
)


User = get_user_model  # оно подхватывает кастомную модель CustomUser?


# создать отдельный сериализатор для отображения инфы о пользователе?
# весь огород с кастомными пользователями нужен чтобы показывать подписки... вроде бы
# class UserCreateSerializer(UserCreateSerializer):
#     # эот сериалайзер вообще нужен? указывается в settings.py
#     # https://www.youtube.com/watch?v=lFD5uoCcvSA&t=105s
#
#     class Meta(UserCreateSerializer.Meta):  # вызывает ошибку 'function' object has no attribute '_meta'
#         # model = CustomUser
#         model = User  # надо ли указывать кастомную модель?
#         fields = (
#             'username',
#             'password',
#             'email',
#             'first_name',
#             'last_name',
#         )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'text', 'author', 'image',
                  'ingredients', 'tags', 'cooking_time')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class FollowSerializer(serializers.ModelSerializer):
    # копипаста из api_final_yatube; following заменён на author
    # TODO в выдачу нужно добавить рецепты от тех на кого подписки
    # почему я тогда использовал SlugRelatedField?
    user = SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    author = SlugRelatedField(slug_field='username',
                                 queryset=CustomUser.objects.all())  # или просто User?

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author')
            )
        ]

    def validate(self, data):
        if self.context['request'].user == data.get('author'):
            raise serializers.ValidationError("Can't subscribe to yourself")
        return data
