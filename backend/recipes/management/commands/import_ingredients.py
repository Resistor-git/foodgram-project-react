# import json
# from pathlib import Path
#
# from django.conf import settings
# from django.core.management.base import BaseCommand
#
# from recipes.models import Ingredient
# #
# # #loop:
# # # for line in csv file:
# # #      line = parse line to a list
# # #      # add some custom validation\parsing for some of the fields
# # #
# # #      foo = Foo(fieldname1=line[1], fieldname2=line[2] ... etc. )
# # #      try:
# # #          foo.save()
# # #      except:
# # #          # if the're a problem anywhere, you wanna know about it
# # #          print "there was a problem with line", i
# #
# CSV_INGREDIENTS = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.json'
# #
# #
# class Command(BaseCommand):
#     help: str = 'Imports data from json to database.'
#
#     def handle(self, *args, **options):
#         ingredients_import()
#
#         self.stdout.write("End of import.")
#
#
# def ingredients_import():
#     with CSV_INGREDIENTS.open('r', 'utf-8') as f:
#         data = json.load(f)
#         for item in data:
#             new_ingredient = Ingredient(
#                 name=item['name'],
#                 measurement_unit=item['measurement_unit']
#             )
#             print(new_ingredient)
#         new_ingredient.save()


# import csv
# from pathlib import Path
#
# from django.core.management.base import BaseCommand
# from django.conf import settings
#
# from recipes.models import Ingredient
#
# CSV_INGREDIENTS = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.json'

# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         print('foo')
#         with open(CSV_INGREDIENTS, 'r', encoding='utf-8') as table:
#             reader = csv.DictReader(table)
#             print(reader)
#             Ingredient.objects.bulk_create(Ingredient(**data) for data in reader)
#
#         self.stdout.write("End of import.")

##########
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         with open(CSV_INGREDIENTS, 'r', encoding='utf-8') as f:
#             reader = csv.reader(f)
#             for row in reader:
#                 print(row)
#                 _, created = Ingredient.objects.get_or_create(
#                     name=row[0],
#                     measurement_unit=row[1],
#                 )
#         self.stdout.write("End of import.")



# import json
# import os
# from pathlib import Path
#
# from django.conf import settings
# from django.core.management.base import BaseCommand
# from recipes.models import Ingredient


# CSV_INGREDIENTS = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.json'
#
# class Command(BaseCommand):
#     help = 'Загрузка данных из json файла в модель Ingredients.'
#
#     # def add_arguments(self, parser):
#     #     parser.add_argument('json_file', type=str, help='Путь до JSON файла.')
#
#     def handle(self, *args, **options):
#         # json_file = options['json_file']
#         # absolute_path = os.path.abspath(json_file)
#         # self.stdout.write(f'Parsing JSON file: {absolute_path}')
#
#         with open(CSV_INGREDIENTS, 'r', encoding='utf-8') as file:
#             data = json.load(file)
#
#         # Создание списка объектов модели для bulk_create
#         objects_to_create = [
#             Ingredient(name=item['name'],
#                        measurement_unit=item['measurement_unit'])
#             for item in data
#         ]
#         Ingredient.objects.bulk_create(objects_to_create)
#         self.stdout.write(self.style.SUCCESS('Данные загружены в БД.'))
###############
# БЫСТРЫЙ, ДОЛЖЕН БЫТЬ РАБОЧИЙ
import json
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

# python manage.py import_ingredients ../data/ingredients.json
class Command(BaseCommand):
    help = 'Загрузка данных из json файла в модель Ingredients.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Путь до JSON файла.')

    def handle(self, *args, **options):
        json_file = options['json_file']
        absolute_path = os.path.abspath(json_file)
        self.stdout.write(f'Parsing JSON file: {absolute_path}')

        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Создание списка объектов модели для bulk_create
        objects_to_create = [
            Ingredient(name=item['name'],
                       measurement_unit=item['measurement_unit'])
            for item in data
        ]
        Ingredient.objects.bulk_create(objects_to_create)
        self.stdout.write(self.style.SUCCESS('Данные загружены в БД.'))

#######################
# import csv
# from pathlib import Path
#
# from django.conf import settings
# from django.core.management.base import BaseCommand
#
# from recipes.models import Ingredient
#
# CSV_INGREDIENTS = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.json'
#
# class Command(BaseCommand):
#     help='Imports data from csv to database.'
#
#     def handle(self, *args, **kwargs):
#         with open(CSV_INGREDIENTS, encoding='utf-8') as file:
#             reader = csv.reader(file)
#             next(reader)
#             ingredients = [
#                 Ingredient(
#                     name=row[0],
#                     measurement_unit=row[1]
#                 )
#                 for row in reader
#             ]
#             Ingredient.objects.bulk_create(ingredients)
#         self.stdout.write('End of import.')

###
# РАБОЧИЙ, МЕДЛЕННЫЙ
# import csv
# from pathlib import Path
#
# from django.conf import settings
# from django.core.management.base import BaseCommand, CommandError
#
# from recipes.models import Ingredient
#
# CSV_INGREDIENTS = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.csv'
#
# class Command(BaseCommand):
#     help='Imports data from csv to database.'
#
#     def handle(self, *args, **kwargs):
#         try:
#             with open(CSV_INGREDIENTS, 'r', encoding='utf-8') as csv_file:
#                 rows = csv.reader(csv_file)
#                 for row in rows:
#                     name, measurement_unit = row
#                     Ingredient.objects.get_or_create(
#                         name=name,
#                         measurement_unit=measurement_unit
#                     )
#         except FileNotFoundError:
#             raise CommandError('Csv file not found')
#         self.stdout.write('End of import.')
