""" Subtypes interfaces
"""
from zope import schema
from zope.interface import Interface
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.subtypes.interfaces import IFacetedSubtyper

class IPossibleFacetedHeritor(Interface):
    """
    A possible heritor that can inherit faceted configuration from a
    faceted navigable object.
    """

class IFacetedHeritor(IFacetedNavigable):
    """
    A heritor that inherit faceted configuration from a
    faceted navigable object.
    """

class IFacetedHeritorSubtyper(IFacetedSubtyper):
    """ Extends IFacetedSubtyper functionallity
    """
    can_enable_heritor = schema.Bool(u'Can enable faceted inheritance',
                                     readonly=True)
