import logging

from django.core.management.base import BaseCommand, CommandError
from ...filters import get_all_filters

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'List available asset filters'

    def handle(self, *args, **options):
        for name, f in get_all_filters():
            print(name, f.__doc__)



