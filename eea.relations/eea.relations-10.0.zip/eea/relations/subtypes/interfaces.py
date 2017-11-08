""" Custom subtypes
"""
from eea.facetednavigation.interfaces import \
     IFacetedNavigable as IOriginalFacetedNavigable

class IFacetedNavigable(IOriginalFacetedNavigable):
    """
    A heritor that inherit faceted configuration from a
    faceted navigable object.
    """
