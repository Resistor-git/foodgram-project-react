from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


# TODO
# связи related_name
# проверить что дописаны все поля и нигде нет троеточия


CHOISES_INGRIDIENTS = [
    ('', ''),
    ('', ''),
    ('', ''),
    ('', ''),
]


class Ingredient(models.Model):
    # Данные об ингредиентах должны храниться в нескольких связанных таблицах. WAT???
    name = models.CharField(
        max_length=60,
        help_text='Name of the ingredient',
        unique=True
    )
    quantity = models.PositiveSmallIntegerField(
        help_text='How much of the ingredient is needed'
    )
    unit_of_measurement = models.CharField(
        max_length=16,
        help_text='Units of measurement for the ingredient'
    )

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


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


class Recipe(models.Model):
    name = models.CharField(
        max_length=200,
        help_text='Name of the recipe'
    )
    description = models.TextField(
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
        related_name='recipes'
    ) # ??? Множественное поле с выбором из предустановленного списка и с указанием количества и единицы измерения ??? models.CharField(max_length=16, choices=CHOISES_INGRIDIENTS)
    # То же можно сделать и на уровне сериализатора, указав для поля color тип ChoiceField и передав в параметр choices список с возможными вариантами
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes'
    )  # подумать, нужна ли промежуточная таблица; many=True? см. задание
    time_to_cook = models.PositiveSmallIntegerField(
        help_text='Time to cook according to the recipe'
    )

    class Meta:
        verbose_name = 'Recipe',
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


