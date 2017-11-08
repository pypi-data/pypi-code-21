""" Caching
"""
from zope.component import queryAdapter
from eea.geotags.interfaces import IJsonProvider

def cacheGeoJsonKey(method, self, *args, **kwargs):
    """ Generate unique cache id
    """
    kwargs = kwargs.copy()
    service = queryAdapter(self.context, IJsonProvider)
    if service:
        kwargs['_service_'] = '.'.join((
            service.__module__,
            service.__class__.__name__
        ))
    kwargs.update(self.request.form)
    return kwargs
