from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from colab.plugins import helpers
import colab_mkdocs_tos
import os


class Command(BaseCommand):

    def handle(self, *args, **options):
        mkdocs_path = os.path.dirname(colab_mkdocs_tos.__file__)
        filename = os.path.join(mkdocs_path, 'mkdocs.yml')
        plugin_config = helpers.get_plugin_config('colab_mkdocs_tos')
        rendered = render_to_string('mkdocs.yml', {
            'mkdocs_title': plugin_config['docs_title'],
            'mkdocs_dir': mkdocs_path,
            'mkdocs_pages': plugin_config['pages']
        })

        with open(filename, 'w'):
            # Clean file
            pass

        with open(filename, 'w') as config_file:
            config_file.write(rendered.encode('utf8'))
