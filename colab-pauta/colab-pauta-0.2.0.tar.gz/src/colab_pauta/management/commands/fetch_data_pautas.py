from django.core.management.base import BaseCommand
from colab_pauta.data_importer import ColabPautaDataImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        pautas_data = ColabPautaDataImporter()
        pautas_data.fetch_data()
