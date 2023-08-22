from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RecipeViewSet

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

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),  # оставить или убрать ???
    path('/auth/', include('djoser.urls.authtoken')),
]
