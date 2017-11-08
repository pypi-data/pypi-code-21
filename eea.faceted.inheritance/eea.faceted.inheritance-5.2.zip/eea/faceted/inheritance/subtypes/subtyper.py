""" Subtyping support
"""
from zope.event import notify
from zope.interface import implements
from zope.interface import alsoProvides

from eea.faceted.inheritance.subtypes.interfaces import IFacetedHeritorSubtyper
from eea.facetednavigation.subtypes.subtyper import FacetedPublicSubtyper
from eea.facetednavigation.events import FacetedWillBeEnabledEvent
from eea.facetednavigation.events import FacetedEnabledEvent

from eea.faceted.inheritance.interfaces import IPossibleFacetedHeritor
from eea.faceted.inheritance.interfaces import IFacetedHeritor

class FacetedHeritorPublicSubtyper(FacetedPublicSubtyper):
    """ Public support for subtyping objects
    """
    implements(IFacetedHeritorSubtyper)

    @property
    def can_enable_heritor(self):
        """ See IFacetedHeritorSubtyper
        """
        if not IPossibleFacetedHeritor.providedBy(self.context):
            return False

        if IFacetedHeritor.providedBy(self.context):
            return False
        return True

class FacetedHeritorSubtyper(FacetedHeritorPublicSubtyper):
    """ Support for subtyping objects
    """
    def enable(self):
        """ See IFacetedSubtyper
        """
        if not self.can_enable_heritor:
            return self._redirect('Faceted inheritance not supported')

        notify(FacetedWillBeEnabledEvent(self.context))
        alsoProvides(self.context, IFacetedHeritor)
        notify(FacetedEnabledEvent(self.context))
        self._redirect('Faceted inheritance enabled')
