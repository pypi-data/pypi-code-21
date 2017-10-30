from django.core.management.base import BaseCommand, CommandError

from ..supervisor import Supervisor
from ..wsgi_worker import Worker

class Command(BaseCommand):
    help = 'Serve static files using a CORS-enabled http.server'

    def handle(self, *args, **options):
        if Worker.is_worker():
            agent = Worker()
        else:
            agent = Supervisor()
        agent.run_forever()




