""" Geographical coverage utility
"""
import logging
from zope.interface import implements
from zope.component import getUtility
from eea.alchemy.interfaces import IAlchemyAPI
from eea.alchemy.interfaces import IDiscoverGeographicalCoverage
logger = logging.getLogger('eea.alchemy')

ENTITY_TYPES = [
    'City',
    'Continent',
    'Country',
    'GeographicFeature',
    'Region',
    'StateOrCounty',
]

class DiscoverGeographicalCoverage(object):
    """ Discover geotags
    """
    implements(IDiscoverGeographicalCoverage)

    def __init__(self):
        self._key = ''
        self._alchemy = None

    @property
    def key(self):
        """ Alchemy key
        """
        return self._key

    @property
    def alchemy(self):
        """ Alchemy API
        """
        if self._alchemy:
            return self._alchemy

        if not self.key:
            logger.exception('You need to provide a valid Alchemy API key')
            return self._alchemy

        self._alchemy = getUtility(IAlchemyAPI)
        self._alchemy.setAPIKey(self.key)
        return self._alchemy

    def __call__(self, key, text="", path=""):
        self._key = key

        if not self.alchemy:
            logger.exception('You need to provide a valid Alchemy API key')
            return

        try:
            res = self.alchemy.TextGetRankedNamedEntities(text)
        except Exception, err:
            logger.exception("%s while discovering: %s", err, path)
            return

        for entity in res.get('entities', []):
            etype = entity.get('type', '')
            if etype not in ENTITY_TYPES:
                continue
            yield entity
