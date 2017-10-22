from django.conf import settings
from django.core.management.base import BaseCommand

import os
import sys

from .....presets.nice import PythonSection


def get_section():

    # Expect classic project layout for now.

    DIR_WORKING = os.getcwd()
    PROJECT_NAME = os.path.basename(DIR_WORKING)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '%s.settings' % PROJECT_NAME)

    section = PythonSection(
        wsgi_module='%s.wsgi' % PROJECT_NAME,

    ).python.set_basic_params(
        python_home=sys.prefix, search_path=DIR_WORKING

    ).main_process.set_owner_params(
        os.getuid(), os.getegid()

    ).main_process.set_naming_params(
        prefix='[uWSGI %s] ' % PROJECT_NAME
    )

    if settings.DEBUG:
        section.python.set_autoreload_params(2)

        def add_static(url, path):

            if url and path:
                section.statics.register_static_map(url, path)

        # todo Gather static or find a workaround.
        add_static(settings.STATIC_URL, settings.STATIC_ROOT)
        add_static(settings.MEDIA_URL, settings.MEDIA_ROOT)

    section.networking.register_socket(
        '127.0.0.1:8000', type=section.networking.socket_types.HTTP)

    return section


class Command(BaseCommand):

    help = 'Runs uWSGI server'

    def handle(self, *args, **options):

        # todo Support automatic loading from project/uwsgicfg.py
        # todo Support loading from given .py config.
        # todo Support loading from default .py config as in ``get_section``.

        section = get_section()
        filepath = section.as_configuration().tofile()

        os.execvp('uwsgi', ['uwsgi', '--ini=%s' % filepath])
