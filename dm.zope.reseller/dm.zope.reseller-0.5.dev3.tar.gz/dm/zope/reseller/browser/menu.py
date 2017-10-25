# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""Specialize menu related classes."""
from zope.component import getUtility
from zope.browsermenu.interfaces import IBrowserMenu
from zope.contentprovider.provider import ContentProviderBase 

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from .interfaces import IRoot
from .browsermenu import BrowserMenuItem, BrowserSubMenuItem, BrowserMenu

class ContextMixin(object):
  """Mixin class to determine `title` from context."""
  def get_title(self): return self.context.title
  def set_title(self, title):
    assert not title or title.startswith("@"), "cannot set title: %s" % title
  title = property(get_title, set_title)

class ContextMenuItem(ContextMixin, BrowserMenuItem): pass
class ContextSubMenuItem(ContextMixin, BrowserSubMenuItem): pass
# this does not work as a menu lacks a context
#class ContextMenu(ContextMixin, BrowserMenu): pass

class AncestorMixin(object):
  """Mixin class to determine `title` from an ancestor.

  The ancestor to use is determined from the original *title*
  which must have the form `@<path-suffix>`. The first
  ancestor whose class name matches *path-suffix* is used
  to determine `title`. If no such ancestor exists, the item
  is unavailable.
  """
  path_suffix = None

  def get_title(self): return self._get_ancestor().title
  def set_title(self, title):
    assert title.startswith("@"), "title must have the form `@<path-suffix>`: %s" % title
    self.path_suffix = title[1:].split(".")
  title = property(get_title, set_title)

  def _get_ancestor(self):
    ps = self.path_suffix
    if ps is None: return
    psl = len(ps)
    obj = self.context
    if not psl: return obj
    while obj is not None:
      c = obj.__class__
      cp = c.__module__.split(".") + [c.__name__]
      if cp[-psl:] == ps: return obj
      if IRoot.providedBy(obj): return
      obj = obj.__parent__
    
  def available(self):
    return self._get_ancestor() is not None \
           and super(AncestorMixin, self).available()

# I cannot abuse the `title` for menu items (only for submenu items)
#class AncestorMenuItem(AncestorMixin, BrowserMenuItem): pass
class AncestorSubMenuItem(AncestorMixin, BrowserSubMenuItem): pass

# generate classes for menus on a specific depth
_m = globals()
def _mk_class(name, depth):
  base = _m[name]
  cl = type(base)(name + 'D' +  `depth`, (base,), dict(menu_depth=depth))
  _m[cl.__name__] = cl

for _i in range(4):
  _mk_class("BrowserMenuItem", _i)
  _mk_class("BrowserSubMenuItem", _i)
  _mk_class("ContextMenuItem", _i)
  _mk_class("ContextSubMenuItem", _i)
  # in principle, I could determine the menu depth automatically
  #_mk_class("AncestorMenuItem", _i)
  _mk_class("AncestorSubMenuItem", _i)

del _i; del _mk_class; del _m



class MenuBarProvider(ContentProviderBase):

  index = ViewPageTemplateFile("menu_bar.pt")

  def render(self): return self.index()

  def menu(self):
    return getUtility(IBrowserMenu, name="dm_zope_reseller__menu_bar")\
           .getMenuItems(self.context, self.request)
