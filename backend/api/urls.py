from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet

app_name = 'api'

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('v1/', include(v1_router.urls))
]
