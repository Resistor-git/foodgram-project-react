from rest_framework import serializers

from recipes.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('name', 'description', 'author', 'image',
                  'ingredients', 'tags', 'time_to_cook')
