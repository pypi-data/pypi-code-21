""" Alchemy adapters
"""
import logging
from zope.interface import implements
from zope.component import queryAdapter
from zope.component.hooks import getSite
from eea.alchemy.interfaces import IDiscoverAdapter
from eea.alchemy.controlpanel.interfaces import IAlchemySettings
from eea.alchemy.config import EEAMessageFactory as _
logger = logging.getLogger('eea.alchemy')

class Discover(object):
    """ Abstract alchemy adapter.

        All custom alchemy adapters should inherit from this  adapter or at
        least implement it's methods and attributes. See IDiscoverAdapter
        interface for more details.

    """
    implements(IDiscoverAdapter)
    title = _('Abstract')

    def __init__(self, context):
        self.context = context
        self._key = None
        self.field = 'subject'
        self._metadata = ('title', 'description')

    @property
    def key(self):
        """ AlchemyAPI key
        """
        if self._key is not None:
            return self._key

        site = getSite()
        settings = queryAdapter(site, IAlchemySettings)
        self._key = settings.token
        if not self._key:
            logger.exception(
                'AlchemyAPI key not set in Site Setup > Alchemy Settings')
            return self._key
        return self._key

    @property
    def metadata(self):
        """ Get metadata
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """ Set metadata
        """
        if isinstance(value, (str, unicode)):
            value = (value,)
        self._metadata = value
