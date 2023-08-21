from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()

# CHOISES_INGRIDIENTS = [
#     ('', ''),
#     ('', ''),
#     ('', ''),
#     ('', ''),
# ]


class Tag(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        help_text='Name of the tag'
    )
    colour_code = models.CharField(
        max_length=7
    )
    slug = models.SlugField(
        max_length=30,
        unique=True,
        help_text='Slug for the tag'
    )

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    # Данные об ингредиентах должны храниться в нескольких связанных таблицах. WAT???
    name = models.CharField(
        max_length=60,
        help_text='Name of the ingredient',
    )
    measurement_unit = models.CharField(
        max_length=16,
        help_text='Units of measurement for the ingredient'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
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
    ) # ??? Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения ??? models.CharField(max_length=16, choices=CHOISES_INGRIDIENTS)
    # То же можно сделать и на уровне сериализатора, указав для поля color тип ChoiceField и передав в параметр choices список с возможными вариантами
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
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
        on_delete=models.CASCADE
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


# class Favourite(models.Model):
#     ...
