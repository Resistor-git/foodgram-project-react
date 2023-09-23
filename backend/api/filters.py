import django_filters

from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'tags', 'author']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            try:
                return queryset.filter(favorites__user=self.request.user)
            except TypeError:
                return queryset
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            try:
                return queryset.filter(carts__user=self.request.user)
            except TypeError:
                return queryset
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
