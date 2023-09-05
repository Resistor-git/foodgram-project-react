from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import (
    viewsets,
    permissions,
    # filters,
    status,
    serializers
)
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
)
from users.models import (
    Subscription,
    CustomUser,
)
from api.serializers import (
    RecipeListRetrieveSerializer,
    RecipeCreateSerializer,
    IngredientSerializer,
    TagSerializer,
    # SubscriptionCreateSerializer,
    SubscriptionSerializer,
    CustomUserCreateSerializer,
    CustomUserRetrieveSerializer,
)
from api.permissions import (
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()  # или CustomUser?
    serializer_class = CustomUserRetrieveSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserRetrieveSerializer

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
        # удостовериться, что другой не может изменить подписку
    )
    def subscribe(self, request, id):  # id сюда как прилетает?
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if User.objects.filter(id=id).exists() and user != author:  # не факт, что срабатывает
                Subscription.objects.create(user=user, author=author)
                serializer = SubscriptionSerializer(
                    author,
                    data=request.data,
                    context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if Subscription.objects.filter(user=user, author=author).exists():
                Subscription.objects.get(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        authors = CustomUser.objects.filter(following__user=user)
        page = self.paginate_queryset(authors)
        if page:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            serializer = SubscriptionSerializer(
                authors,
                many=True,
                context={'request': request}
            )
            return Response(data=serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD for recipes"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeListRetrieveSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListRetrieveSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        # не уверен, что здесь это писать, возможно нужно в create сериализатора засунуть
        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Get a single or all ingredients. Readolny."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Get a single or all tags. Readolny.
    Used to assign tags to recipes."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]  # ??? или readonly? или allowany? или дефолтный?


# class SubscriptionViewSet(viewsets.ModelViewSet):
#     queryset = Subscription.objects.all()
#     serializer_class = SubscriptionCreateSerializer  # заменить на чтение?
#     permission_classes = [permissions.IsAuthenticated]
