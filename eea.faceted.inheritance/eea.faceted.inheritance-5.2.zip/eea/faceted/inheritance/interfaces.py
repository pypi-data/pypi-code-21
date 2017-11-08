""" Faceted inheritance public interfaces
"""
# Subtypes
from eea.faceted.inheritance.subtypes.interfaces import IPossibleFacetedHeritor
from eea.faceted.inheritance.subtypes.interfaces import IFacetedHeritor

# Criteria
from eea.faceted.inheritance.criteria.interfaces import IHeritorAccessor
from eea.faceted.inheritance.criteria.interfaces import ICriteria

__all__ = [
    IPossibleFacetedHeritor.__name__,
    IFacetedHeritor.__name__,
    IHeritorAccessor.__name__,
    ICriteria.__name__,
]
