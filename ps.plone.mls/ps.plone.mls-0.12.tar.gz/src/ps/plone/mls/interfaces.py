# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports
from zope.interface import Interface


class IListingTraversable(Interface):
    """Marker interface for traversable listings."""


class IDevelopmentTraversable(Interface):
    """Marker interface for traversable listings."""


class IBaseDevelopmentItems(IDevelopmentTraversable):
    """Marker interface for all development 'collection' items."""


class IDevelopmentCollection(IBaseDevelopmentItems):
    """Marker interface for DevelopmentCollection viewlet."""


class IDevelopmentDetails(Interface):
    """Marker interface for DevelopmentDetails view."""


class IDevelopmentListings(Interface):
    """Marker interface for DevelopmentListings view."""


class IPossibleDevelopmentCollection(Interface):
    """Marker interface for possible DevelopmentCollection viewlet."""


class IPossibleListingSearchBanner(Interface):
    """Marker interface for possible Listing Search Banner viewlet."""


class IListingSearchBanner(Interface):
    """Marker interface for Listing Search Banner viewlet."""
