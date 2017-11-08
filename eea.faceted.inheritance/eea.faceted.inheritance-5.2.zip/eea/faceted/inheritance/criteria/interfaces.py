""" Criteria interfaces
"""
from eea.facetednavigation.interfaces import ICriteria
from zope.interface import Interface

class IHeritorAccessor(Interface):
    """ Heritor accessor/mutator
    """

__all__ = [
    ICriteria.__name__,
    IHeritorAccessor.__name__,
]
