from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, RegexValidator

User = get_user_model()


# проверить поля на соответствие документации, например colour_code
class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text='Name of the tag'
    )
    color = models.CharField(
        # можно заменить на colorfield https://pypi.org/project/django-colorfield/
        max_length=7,
        unique=True,
        help_text='Color code in HEX, example: #49B64E'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        validators=[RegexValidator('^[-a-zA-Z0-9_]+$')],
        help_text='Slug for the tag'
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Name of the ingredient',
    )
    measurement_unit = models.CharField(
        max_length=200,
        help_text='Units of measurement for the ingredient'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Recipe(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(
        max_length=200,
        help_text='Name of the recipe'
    )
    text = models.TextField(
        max_length=600,
        help_text='Description of the recipe'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes')
    image = models.ImageField(
        upload_to='recipes/'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        help_text='Time to cook according to the recipe',
        validators=[
            MinValueValidator(limit_value=1,
                              message="Cooking time can't be less than 1 minute")
        ]
    )

    class Meta:
        verbose_name = 'Recipe',
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        help_text='Amount of the ingredient')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favored',  # subscriptions
        verbose_name='User who favored a recipe'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Favorite recipes of a user'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='User who added recipe to shopping list'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',  # ?? или наоборот purchases
        verbose_name='Favorite recipes of a user'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shoppingcart'
            )
        ]
