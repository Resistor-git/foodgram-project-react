from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from djoser.conf import settings

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    viewsets,
    permissions,
    # filters,
    status,
    serializers,
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
    # SubscriptionCreateSerializer,
    SubscriptionSerializer,
    CustomUserCreateSerializer,
    CustomUserRetrieveSerializer,
    FavoriteSerializer,
    ShoppingCartSerializer,
    # ShoppingCartDownloadSerializer
)
from api.permissions import (
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
    IsAuthenticatedOrListOnly,
)
from api.filters import (
    RecipeFilter,
    IngredientFilter
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()  # или CustomUser?
    # serializer_class = CustomUserRetrieveSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    permission_classes = [IsAuthenticatedOrListOnly]

    def get_serializer_class(self):
        # print('!!!self.request.method:', self.request.method, flush=True)
        if self.request.method in permissions.SAFE_METHODS and self.request.user.is_authenticated:
            # print('!!!Using CustomUserRetrieveSerializer', flush=True)
            return CustomUserRetrieveSerializer
        return super().get_serializer_class()

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=SubscriptionSerializer,
        # удостовериться, что другой не может изменить подписку
    )
    def subscribe(self, request, id):  # id сюда как прилетает? - вроде как из реквеста (а в нём из url)
        user = request.user
        author = get_object_or_404(User, id=id)

        # if request.method == 'POST':
        #     if User.objects.filter(id=id).exists() and user != author:  # не факт, что срабатывает
        #         print('!!!!request_data:', request.data, flush=True)
        #         serializer = SubscriptionSerializer(
        #             data=request.data,
        #             context={'request': request}
        #         )
        #         # serializer.is_valid(raise_exception=True)
        #         Subscription.objects.create(user=user, author=author)
        #         # print('!!!!serializer.data:', serializer, flush=True)
        #         return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        #     else:
        #         error_message = {'error': 'Can not subscribe to yourself'}
        #         return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            if User.objects.filter(id=id).exists():
                if user == author:
                    error_message = {'error': 'Can not subscribe to yourself'}
                    return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)
                if Subscription.objects.filter(user=user, author=author).exists():
                    error_message = {'error': 'You are already subscribed to that author'}
                    return Response(data=error_message, status=status.HTTP_400_BAD_REQUEST)
                serializer = self.get_serializer(author)
                Subscription.objects.create(user=user, author=author)
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
    queryset = Recipe.objects.all().order_by('-created_at')
    # serializer_class = RecipeListRetrieveSerializer
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListRetrieveSerializer
        return RecipeCreateSerializer

    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context.update({"request": self.request})
    #     return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     print('!!!instance:', instance)
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)

    # def perform_update(self, serializer):
    #     serializer.save()

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if recipe:
                serializer = FavoriteSerializer(
                    data={'recipe': recipe.pk},
                    context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                if serializer.is_valid:  # два раза проверка?
                    Favorite.objects.create(user=user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if Favorite.objects.filter(user=user, recipe=recipe).exists():
                Favorite.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'errors': 'The recipe does not exist'}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['POST', 'DELETE'],  # GET чтобы скачать?
        detail=True,
        permission_classes=[IsAuthorOrReadOnly],  # строже? isAuthorOrAdmin
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if recipe:
                serializer = ShoppingCartSerializer(
                    data={'recipe': recipe.pk},
                    context={'request': request}
                )
                serializer.is_valid(raise_exception=True)
                if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                    ShoppingCart.objects.create(user=user, recipe=recipe)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(
                    {'errors': 'The recipe is already in shopping cart'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'errors': 'The recipe does not exist'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if request.method == 'DELETE':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                ShoppingCart.objects.get(user=user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {'errors': 'The recipe is not in shopping cart'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        methods=['GET'],
        detail=False,
        # permission_classes=[permissions.IsAuthor]
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
            if el.get('ingredient__name') not in shopping_cart_summed_ingredients.keys():
                shopping_cart_summed_ingredients[name] = {'unit': unit, 'amount': amount}
            else:
                shopping_cart_summed_ingredients[name]['amount'] += amount
        for key, value in shopping_cart_summed_ingredients.items():
            text.append(f'{key.capitalize()} ({value["unit"]}):  {value["amount"]}\n')
        return HttpResponse(
            text,
            headers={'Content-Type': 'text/plain', 'Content-Disposition': 'attachment; filename="shopping_cart.txt"'}
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
    permission_classes = [IsAdminOrReadOnly]  # ??? или readonly? или allowany? или дефолтный?
    pagination_class = None


class FavoriteViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthorOrReadOnly]  # вообще, там не author, а user... т.е. авторство по другому полю определяется