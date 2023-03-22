import simplejson
from django.core.management.base import BaseCommand

from api.models import Tag, Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('Starting data migration...')
        tag_data = [
            {'name': 'lunch', 'color': '#4b5c38', 'slug': 'lunch'},
            {'name': 'dinner', 'color': '#5a0e2d', 'slug': 'dinner'},
            {'name': 'sup', 'color': '#e5c07b', 'slug': 'sup'}
        ]

        for data in tag_data:
            Tag.objects.get_or_create(**data)

        f = open('ingredients.json', 'r', encoding='UTF-8')
        obj = simplejson.load(f)
        objs = [
            Ingredient(
                name=parametr['name'],
                measurement_unit=parametr['measurement_unit']
                ) for parametr in obj
            ]
        Ingredient.objects.bulk_create(objs)
        print('Data migration comlete')
