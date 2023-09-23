from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    RecipeViewSet,
    TagViewSet,
    IngredientViewSet,
    CustomUserViewSet
)

app_name = 'api'

router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
