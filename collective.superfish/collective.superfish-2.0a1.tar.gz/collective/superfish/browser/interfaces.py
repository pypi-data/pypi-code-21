# -*- coding: utf-8 -*-
from plone.browserlayer.interfaces import ILocalBrowserLayerType


class ISuperfishLayer(ILocalBrowserLayerType):
    """Display superfish menu only when instlalled in quickinstaller by using
    a custom superfish browserlayer."""
