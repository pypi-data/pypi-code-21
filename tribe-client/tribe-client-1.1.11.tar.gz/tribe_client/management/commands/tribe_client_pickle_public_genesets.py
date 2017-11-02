import logging

from django.core.management.base import BaseCommand, CommandError
from organisms.models import Organism

from tribe_client.utils import pickle_organism_public_genesets

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Command(BaseCommand):
    help = ('Loop through all the organisms in the database and pickle all '
            'the publicly avilable Tribe genesets for each of those '
            'organisms.')

    def handle(self, *args, **options):
        for organism in Organism.objects.all():
            try:
                pickle_organism_public_genesets(organism.scientific_name)
                logger.info('Successfully pickled Tribe public genesets '
                            'for organism "%s".' % organism.scientific_name)

            except Exception as e:
                logger.error(e)
                raise CommandError(
                    'Error when pickling Tribe public genesets for '
                    'organism "%s".' % organism.scientific_name)
