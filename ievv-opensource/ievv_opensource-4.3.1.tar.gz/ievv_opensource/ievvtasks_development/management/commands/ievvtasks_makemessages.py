import os

from django.conf import settings
from django.core import management

from ievv_opensource.ievvtasks_common.base_command import BaseIevvTasksCommand


class Command(BaseIevvTasksCommand):
    help = 'Run makemessages for the languages specified in the ' \
           'IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES setting.'

    def __makemessages(self, ignore, extensions, domain):
        management.call_command(
            'makemessages',
            locale=settings.IEVVTASKS_MAKEMESSAGES_LANGUAGE_CODES,
            ignore=ignore,
            extensions=extensions,
            domain=domain)

    def __build_python_translations(self):
        ignore = getattr(settings, 'IEVVTASKS_MAKEMESSAGES_IGNORE', [
            'static/*'
        ])
        extensions = getattr(settings, 'IEVVTASKS_MAKEMESSAGES_EXTENSIONS', [
            'py', 'html', 'txt'])
        self.__makemessages(ignore=ignore,
                            extensions=extensions,
                            domain='django')

    def __build_javascript_translations(self):
        ignore = getattr(settings, 'IEVVTASKS_MAKEMESSAGES_JAVASCRIPT_IGNORE', [
            'node_modules/*',
            'bower_components/*',
            'not_for_deploy/*',
        ])
        extensions = getattr(settings, 'IEVVTASKS_MAKEMESSAGES_JAVASCRIPT_EXTENSIONS', [
            'js'])
        self.__makemessages(ignore=ignore,
                            extensions=extensions,
                            domain='djangojs')

    def __run_pre_management_commands(self):
        management_commands = getattr(
            settings, 'IEVVTASKS_MAKEMESSAGES_PRE_MANAGEMENT_COMMANDS', [])
        self.run_management_commands(management_commands)

    def handle(self, *args, **options):
        self.__run_pre_management_commands()
        current_directory = os.getcwd()
        for directory in getattr(settings, 'IEVVTASKS_MAKEMESSAGES_DIRECTORIES', [current_directory]):
            directory = os.path.abspath(directory)
            self.stdout.write('Running makemessages for python files in {}'.format(directory))
            os.chdir(directory)
            self.__build_python_translations()
            if getattr(settings, 'IEVVTASKS_MAKEMESSAGES_BUILD_JAVASCRIPT_TRANSLATIONS', False):
                self.stdout.write('Running makemessages for javascript files in {}'.format(directory))
                self.__build_javascript_translations()
            os.chdir(current_directory)
