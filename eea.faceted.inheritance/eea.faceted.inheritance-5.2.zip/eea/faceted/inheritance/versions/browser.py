""" Faceted version
"""
from zope.component import queryAdapter
from zope.component import queryMultiAdapter
from eea.faceted.inheritance.interfaces import ICriteria
from Products.Five.browser import BrowserView

class FacetedVersion(BrowserView):
    """ Get version from ancestor
    """
    def __call__(self, **kwargs):
        """ Get version
        """
        handler = queryAdapter(self.context, ICriteria)
        ancestor = getattr(handler, 'ancestor', None)
        if not ancestor:
            return ''

        version = queryMultiAdapter((ancestor, self.request),
                                    name=u'faceted_version')

        if not version:
            return ''
        return version()
