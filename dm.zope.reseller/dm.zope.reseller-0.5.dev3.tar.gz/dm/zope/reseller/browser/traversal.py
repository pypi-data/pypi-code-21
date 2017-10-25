# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Traversal machinery."""
from zope.interface import implements, Interface
from zope.component import queryAdapter, queryMultiAdapter, getMultiAdapter, \
     adapts
from zope.traversing.namespace import SimpleHandler

from ..i18n import _

from .interfaces import IProxy, IContained, ILayer

class Proxy(object):
  """Object proxies used for traversal."""
  implements(IProxy)
  
  def __init__(self, parent, obj=None, name=None):
    self.obj = obj; self.__parent__ = parent; self.__name__ = name

  browser_default = ()
  def browserDefault(self, request): return (self, self.browser_default)

  def publishTraverse(self, request, name):
    # called only when *name* does not start with `@` or `+`
    proxy = queryAdapter(self, IContained, name=name)
    if proxy is not None:
      proxy.__name__ = name
      return proxy
    else:
      # try it as a view
      return getMultiAdapter((self, request), Interface, name=name)

  @property
  def title(self):
    title = getattr(self.obj, "title", None)
    if title is None: return _(unicode(self.__class__.__name__))
    else:
      return _(u"%s ${obj_title}" % self.__class__.__name__,
               mapping=dict(obj_title=title),
               )


class CollectionProxy(Proxy):
  browser_default = "crud",


class Namespace(SimpleHandler):
  # to be defined by derived classes
  NAME = None
  OBJECT_FACTORY = None

  def PROXY_FACTORY(self, obj):
    return getMultiAdapter((self.context, obj), IProxy)


  def traverse(self, name, unused):
    obj = self.OBJECT_FACTORY(int(name))
    if obj is None: raise KeyError(name)
    proxy = self.PROXY_FACTORY(obj)
    proxy.__name__ = "++%s++%s" % (self.NAME, name)
    return proxy


class ChildNamespace(Namespace):
  adapts(CollectionProxy, ILayer)

  NAME = "child"

  def OBJECT_FACTORY(self, id): return self.context.obj.get_item(id, KeyError)
  
    
    

class Constant(object):
  """A descriptor to implement a constant."""
  def __init__(self, constant): self.__const = constant

  def __get__(self, *args): return self.__const
  def __set__(self, inst, value): assert value is None # we ignore `None` assignments
