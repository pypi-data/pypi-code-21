from django.core.management.base import BaseCommand
from colab_wikilegis.data_importer import ColabWikilegisPluginDataImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        wikilegis_data = ColabWikilegisPluginDataImporter()
        wikilegis_data.fetch_data()
