from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet, TagViewSet, IngredientViewSet, CustomUserViewSet

app_name = 'api'

# v1_router = DefaultRouter()
# v1_router.register('recipes', RecipeViewSet, basename='recipes')
#
# urlpatterns = [
#     path('v1/', include(v1_router.urls)),
#     path('v1/', include('djoser.urls')),  # оставить или убрать ???
#     path('v1/auth/', include('djoser.urls.authtoken')),
# ]


router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet)  # на вэбинаре не было такого эндпоинта

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
