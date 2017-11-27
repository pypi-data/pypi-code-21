from django.core.management import BaseCommand

from examples.restaurants.fixture import restaurants_fixture


class Command(BaseCommand):
    def handle(self, *args, **options):
        restaurants_fixture()
