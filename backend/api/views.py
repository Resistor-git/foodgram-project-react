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
    RecipeSerializer,
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
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]


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
