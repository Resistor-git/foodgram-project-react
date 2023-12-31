from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    viewsets,
    permissions,
    status,
    mixins
)
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
    Tag,
    Favorite,
    ShoppingCart,
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
    SubscriptionCreateDestroySerializer,
    SubscriptionRetrieveSerializer,
    CustomUserRetrieveSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
)
from api.my_permissions import (
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
)
from api.filters import (
    RecipeFilter,
    IngredientFilter,
)

from api.paginators import (
    CustomLimitPagination,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomLimitPagination

    def get_serializer_class(self):
        if (self.request.method in permissions.SAFE_METHODS
                and self.request.user.is_authenticated):
            return CustomUserRetrieveSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'me' and self.request.user.is_anonymous:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        # source code for UserViewSet returns empty queryset for
        # anonymous user, had to override it
        queryset = User.objects.all()
        return queryset

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticatedOrReadOnly],
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = SubscriptionCreateDestroySerializer(
            data={
                'user': user.pk,
                'author': author.pk
            },
            context={'request': request}
        )

        if request.method == 'POST':
            if serializer.is_valid(raise_exception=True):
                Subscription.objects.create(user=user, author=author)
                return Response(
                    data=serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            if serializer.is_valid(raise_exception=True):
                Subscription.objects.get(user=user, author=author).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated],
        pagination_class=CustomLimitPagination
    )
    def subscriptions(self, request):
        user = request.user
        authors = CustomUser.objects.filter(following__user=user)
        page = self.paginate_queryset(authors)
        if page:
            serializer = SubscriptionRetrieveSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_200_OK)


class RecipeViewSet(viewsets.ModelViewSet):
    """CRUD for recipes"""
    queryset = Recipe.objects.all().order_by('-created_at')
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomLimitPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListRetrieveSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoriteSerializer(
            data={'recipe': recipe.pk},
            context={'request': request}
        )
        if request.method == 'POST':
            if serializer.is_valid(raise_exception=True):
                Favorite.objects.create(user=user, recipe=recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            if serializer.is_valid(raise_exception=True):
                Favorite.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthorOrReadOnly],
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartSerializer(
            data={'recipe': recipe.pk},
            context={'request': request}
        )

        if request.method == 'POST':
            if serializer.is_valid(raise_exception=True):
                ShoppingCart.objects.create(user=user, recipe=recipe)
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'DELETE':
            if serializer.is_valid(raise_exception=True):
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        shopping_cart_ingredients = RecipeIngredient.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )
        text = []
        shopping_cart_summed_ingredients = {}
        for el in shopping_cart_ingredients:
            name = el.get('ingredient__name')
            unit = el.get("ingredient__measurement_unit")
            amount = el.get('amount')
            if (
                    el.get('ingredient__name') not in
                    shopping_cart_summed_ingredients.keys()
            ):
                shopping_cart_summed_ingredients[name] = {
                    'unit': unit, 'amount': amount
                }
            else:
                shopping_cart_summed_ingredients[name]['amount'] += amount
        for key, value in shopping_cart_summed_ingredients.items():
            text.append(
                f'{key.capitalize()} ({value["unit"]}):  {value["amount"]}\n'
            )
        return HttpResponse(
            text,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': 'attachment; filename="shop_cart.txt"'
            }
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Get a single or all ingredients. Readolny."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Get a single or all tags. Readolny.
    Used to assign tags to recipes."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthorOrReadOnly]
