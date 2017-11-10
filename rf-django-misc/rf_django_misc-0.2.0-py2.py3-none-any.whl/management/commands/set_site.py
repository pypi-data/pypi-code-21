from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('id', type=int)
        parser.add_argument('domain', type=str)

    def handle(self, *args, **options):
        Site.objects.update_or_create(
            id=options['id'],
            defaults=dict(
                name=options['domain'],
                domain=options['domain'],
            )
        )
