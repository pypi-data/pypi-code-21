from django.core.management.base import BaseCommand
from colab_audiencias.data_importer import ColabAudienciasPluginDataImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        audiencias_data = ColabAudienciasPluginDataImporter()
        audiencias_data.fetch_data()
