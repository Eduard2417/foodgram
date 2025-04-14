import csv

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

file_name = settings.BASE_DIR / 'data/ingredients.csv'


class Command(BaseCommand):
    help = 'Load data from CSV files into Django models'

    def handle(self, *args, **options):
        Ingredient = apps.get_model(app_label='recipes',
                                    model_name='Ingredient')
        with open(file_name, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            ingredients = [Ingredient(name=name,
                                      measurement_unit=measurement_unit)
                           for name, measurement_unit in reader]
        Ingredient.objects.bulk_create(ingredients)
