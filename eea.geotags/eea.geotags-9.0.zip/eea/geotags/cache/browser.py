""" Browser
"""
from zope import event
from Products.Five.browser import BrowserView
from eea.geotags.cache import InvalidateCacheEvent

class InvalidateCache(BrowserView):
    """ Utils view to invalidate eea.geotags cache
    """
    def __call__(self, **kwargs):
        event.notify(InvalidateCacheEvent(
            raw=True, dependencies=['eea.geotags']
        ))
