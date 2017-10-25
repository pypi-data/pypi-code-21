# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""The reseller root object.

Actually it is a view (and thus not persistent but created on traversal).
Its task is to set up the reseller layer and record information inside
the request object to allow the browser menus to determine the current
depth.
"""
from zope.interface import implements
from zope.component.interfaces import ISite
from zope.component import getGlobalSiteManager
from zope.component.hooks import setSite
from zope.publisher.skinnable import applySkin
from zope.publisher.interfaces.browser import IBrowserPublisher

from .interfaces import IRoot, ILayer, IProxy
from .traversal import Proxy
from .browsermenu import setup_request


class Root(Proxy):
  """registered as view."""
  implements(IRoot, IProxy,
             # work around a bug in `z3c.form.button.ImageButtonAction` which insists that a site has been set up.
             ISite,
             )

  def __init__(self, context, request):
    self.context = context; self.request = request
    super(Root, self).__init__(context)
    applySkin(request, ILayer)
    setup_request(request)
    setSite(self)

  browser_default = "orders",

  # `ISite`
  def getSiteManager(self): return getGlobalSiteManager()

