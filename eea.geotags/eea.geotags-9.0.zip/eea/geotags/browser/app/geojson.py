""" JSON Service
"""
from pprint import pformat
import logging
import json as simplejson
from zope.component import queryAdapter, getAdapter
from Products.Five.browser import BrowserView
from eea.geotags.interfaces import IJsonProvider, IGeoTags
from eea.geotags.cache import ramcache, cacheGeoJsonKey

logger = logging.getLogger('eea.geotags.browser.json')

class JSON(BrowserView):
    """ JSON service
    """

    @ramcache(cacheGeoJsonKey, dependencies=['eea.geotags'])
    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)

        service = queryAdapter(self.context, IJsonProvider)
        jsondata = kwargs.pop('type', 'search')
        if jsondata == 'groups':
            res = service.groups(**kwargs)
        elif jsondata == 'biogroups':
            res = service.biogroups(**kwargs)
        elif jsondata == 'countries':
            res = service.countries(**kwargs)
        elif jsondata == 'nuts':
            res = service.nuts(**kwargs)
        elif jsondata == 'cities':
            res = service.cities(**kwargs)
        elif jsondata == 'natural':
            res = service.natural_features(**kwargs)
        else:
            res = service.search(**kwargs)

        if kwargs.get('print', None):
            return pformat(res)
        return simplejson.dumps(res)

class JSONDATA(BrowserView):
    """ Return the JSON with geographical tags from annotations
    """

    def __call__(self, **kwargs):
        geo = getAdapter(self.context, IGeoTags)
        return simplejson.dumps(geo.tags)
