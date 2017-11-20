from django.core.management.base import BaseCommand
from colab_wikilegis.data_importer import ColabWikilegisPluginDataImporter
from colab_discourse.data_importer import ColabDiscoursePluginDataImporter
from colab_audiencias.data_importer import ColabAudienciasPluginDataImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        wikilegis_data = ColabWikilegisPluginDataImporter()
        discourse_data = ColabDiscoursePluginDataImporter()
        audiencias_data = ColabAudienciasPluginDataImporter()
        wikilegis_data.fetch_data()
        discourse_data.fetch_data()
        audiencias_data.fetch_data()
