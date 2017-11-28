from django.core.management.base import BaseCommand
from django.core import management
from mkdocs.config import load_config
from mkdocs.commands.build import build
import colab_mkdocs_tos
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        management.call_command('generate_mkdocs_config')
        mkdocs_path = os.path.dirname(colab_mkdocs_tos.__file__)
        filename = os.path.join(mkdocs_path, 'mkdocs.yml')
        mkdocs_config = load_config(config_file=filename)
        build(mkdocs_config)
