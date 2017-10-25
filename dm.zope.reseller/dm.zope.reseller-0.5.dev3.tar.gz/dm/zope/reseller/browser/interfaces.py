# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.location.interfaces import IContained, IRoot
from z3c.form.interfaces import IFormLayer


class ILayer(IDefaultBrowserLayer, IFormLayer):
  """Layer used (by default) for the reseller application."""


class IRoot(IRoot):
  """Interface marking the reseller root object.

  On traversal through this object, the reseller layer is set up.
  In addition, information is recorded in the request to allow
  the browsermenus to determine the current depth.
  """

class IProxy(IContained, IBrowserPublisher):
  """Our traversal proxy interface."""
