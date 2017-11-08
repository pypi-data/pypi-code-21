from django.core.management.base import BaseCommand, CommandError

from ..supervisor import Supervisor

class Command(BaseCommand):
    help = 'Reload all open browser windoes.'

    def handle(self, *args, **options):
        Supervisor.kill(Supervisor.RESTART_SIGNAL)




