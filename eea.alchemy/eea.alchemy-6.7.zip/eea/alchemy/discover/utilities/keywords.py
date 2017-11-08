""" Utility for keywords
"""
import logging
from zope.interface import implements
from zope.component import getUtility
from eea.alchemy.interfaces import IAlchemyAPI
from eea.alchemy.interfaces import IDiscoverKeywords
logger = logging.getLogger('eea.alchemy')

class DiscoverKeywords(object):
    """ Auto discover keywords
    """
    implements(IDiscoverKeywords)

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
            res = self.alchemy.TextGetRankedKeywords(text)
        except Exception, err:
            logger.exception("%s while discovering: %s", err, path)
            return

        for keyword in res.get('keywords', []):
            yield keyword
