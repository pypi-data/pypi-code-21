# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


class ICollectiveQuerynextprevLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class INextPrevViewletManager(IViewletManager):

    """Viewlet manager for next/previous functionnality."""


class IAdditionalDataProvider(Interface):

    """Additional data provider."""

    def get_key(self):
        """Key under which the data will be stored in session."""

    def get_value(self):
        """Data that will be stored in session."""


class INextPrevNotNavigable(Interface):

    """Marker interface for contents that are not next/prev navigables."""
