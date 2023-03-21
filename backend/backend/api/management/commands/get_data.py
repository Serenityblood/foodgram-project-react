from django.core.management.base import BaseCommand

from api.models import Tag, Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        tag_data = [
            {'name': 'lunch', 'color': '#4b5c38', 'slug': 'lunch'},
            {'name': 'dinner', 'color': '#5a0e2d', 'slug': 'dinner'},
            {'name': 'sup', 'color': '#e5c07b', 'slug': 'sup'}
        ]

        ing_data = [
            {'name': 'Свекла', 'measurement_unit': 'кг'},
            {'name': 'Морковь', 'measurement_unit': 'кг'},
            {'name': 'Помидоры', 'measurement_unit': 'кг'},
            {'name': 'Огурцы', 'measurement_unit': 'кг'},
            {'name': 'Капуста', 'measurement_unit': 'кг'},
            {'name': 'Баклажаны', 'measurement_unit': 'кг'}
        ]

        for data in tag_data:
            Tag.objects.create(**data)

        for data in ing_data:
            Ingredient.objects.create(**data)
