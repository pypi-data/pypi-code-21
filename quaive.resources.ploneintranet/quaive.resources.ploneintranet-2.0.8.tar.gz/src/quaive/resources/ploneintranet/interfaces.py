# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from ploneintranet.theme.interfaces import IThemeSpecific as IBaseThemeSpecific


class IThemeSpecific(IBaseThemeSpecific):
    """ Marker interface that defines a Zope 3 browser layer and a plone skin
        marker.
    """
