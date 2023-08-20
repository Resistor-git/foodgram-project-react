import json

from django.conf import settings

from recipes.models import Ingredient

#loop:
# for line in csv file:
#      line = parse line to a list
#      # add some custom validation\parsing for some of the fields
#
#      foo = Foo(fieldname1=line[1], fieldname2=line[2] ... etc. )
#      try:
#          foo.save()
#      except:
#          # if the're a problem anywhere, you wanna know about it
#          print "there was a problem with line", i

CSV_INGREDIENTS = settings.BASE_DIR / 'data' / 'ingredients.json'


def ingredients_import():
    with CSV_INGREDIENTS.open('r') as f:
        data = json.load(f)
        for item in data:
            new_ingredient = Ingredient(
                name=item['name'],
                measurement_unit=item['measurement_unit']
            )
        new_ingredient.save()
        # Ingredient.objects.bulk_create()