# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.form.interfaces import IFormLayer


class ICollectiveZ3CformSelect2Layer(IFormLayer, IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
