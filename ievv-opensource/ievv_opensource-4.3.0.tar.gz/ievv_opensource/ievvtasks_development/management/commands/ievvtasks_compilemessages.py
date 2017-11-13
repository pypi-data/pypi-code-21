import os

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Compile translations.'

    def handle(self, *args, **options):
        current_directory = os.getcwd()
        for directory in getattr(settings, 'IEVVTASKS_MAKEMESSAGES_DIRECTORIES', [current_directory]):
            os.chdir(directory)
            management.call_command('compilemessages')
            os.chdir(current_directory)
