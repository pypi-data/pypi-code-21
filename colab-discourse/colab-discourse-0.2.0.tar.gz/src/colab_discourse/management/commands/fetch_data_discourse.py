from django.core.management.base import BaseCommand
from colab_discourse.data_importer import ColabDiscoursePluginDataImporter


class Command(BaseCommand):
    def handle(self, *args, **options):
        discourse_data = ColabDiscoursePluginDataImporter()
        discourse_data.fetch_data()
