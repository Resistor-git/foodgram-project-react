from django.shortcuts import render
from rest_framework import (
    viewsets,
    permissions,
    # filters,
    # status,
    serializers
)

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
)
from api.serializers import (
    RecipeListRetrieveSerializer,
    RecipeCreateSerializer,
    IngredientSerializer,
    TagSerializer,
)
from api.permissions import (
    IsAuthorOrReadOnly,
    IsAdminOrReadOnly,
)


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
