""" Suggestions
"""
import logging
import json as simplejson
from zope.component import queryAdapter
from Products.Five.browser import BrowserView

from eea.alchemy.interfaces import IDiscoverGeoTags

logger = logging.getLogger('@@eea.geotags.suggestions')
LOOKIN = ('title', 'description')

class View(BrowserView):
    """ Suggest geotags for context
    """
    def __call__(self, lookin=LOOKIN, **kwargs):
        entities = []
        discover = queryAdapter(self.context, IDiscoverGeoTags)
        if discover:
            discover.metadata = lookin
            entities = [entity for entity in discover.tags]

        return simplejson.dumps({
            'suggestions': entities
        })
