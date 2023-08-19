from django.shortcuts import render
from rest_framework import (
    viewsets,
    permissions,
    # filters,
    # status,
    serializers
)

# Create your views here.

from recipes.models import Recipe
from api.serializers import (
    RecipeSerializer,
)
from api.permissions import IsAuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsAuthorOrReadOnly]
