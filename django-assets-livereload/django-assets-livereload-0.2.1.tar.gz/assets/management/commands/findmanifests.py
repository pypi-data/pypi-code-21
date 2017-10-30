import logging

from django.core.management.base import BaseCommand, CommandError
from assets.manifest  import Manifest

FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Find asset manifests'

    def handle(self, *args, **options):
        Manifest.load()
        print(Manifest.ASSET_LIST)




