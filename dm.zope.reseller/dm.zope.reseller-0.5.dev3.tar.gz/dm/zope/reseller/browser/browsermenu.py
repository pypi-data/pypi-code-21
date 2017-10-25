# Copyright (C) 2014 by Dr. Dieter Maurer <dieter@handshake.de>
"""`zope.browsermenu` extension.

Might move into a special (public) package (e.g. `dm.zope.browsermenu`).
"""
from urllib import quote

from zope.interface import Interface, implements, providedBy
from zope.interface.interfaces import IInterface
from zope.component import getAdapters, getUtility
from zope.schema import Int, Tuple
from zope.security.proxy import removeSecurityProxy

from zope.browsermenu.interfaces import \
     IBrowserMenuItem, \
     IBrowserSubMenuItem as IZopeBrowserSubMenuItem, \
     IBrowserMenu
from zope.browsermenu.menu import BrowserMenuItem, BrowserSubMenuItem, \
     BrowserMenu, getMenu
from zope.browsermenu.metaconfigure import \
     menuItemsDirective as Zope_menuItemsDirective, \
     menuItemDirective as Zope_menuItemDirective, \
     subMenuItemDirective as Zope_subMenuItemDirective

from Products.PageTemplates.Expressions import getEngine

from dm.reuse import rebindFunction

# fix menu directives (which use the wrong engine)
class menuItemsDirective(Zope_menuItemsDirective):
  # we could also use our item classes
  menuItem = rebindFunction(Zope_menuItemsDirective.menuItem,
                             Engine=getEngine()
                             )
  subMenuItem = rebindFunction(Zope_menuItemsDirective.subMenuItem,
                             Engine=getEngine()
                             )

menuItemDirective = rebindFunction(Zope_menuItemDirective,
                                    menuItemsDirective=menuItemsDirective
                                    )
subMenuItemDirective = rebindFunction(Zope_subMenuItemDirective,
                                       menuItemsDirective=menuItemsDirective
                                       )

class IBrowserMenuItem(IBrowserMenuItem):
  menu_depth = Int(
    title=u"The depth this menu item lives on -- relative to a setup depth",
    required=False,
    )

class IBrowserSubMenuItem(IBrowserMenuItem, IZopeBrowserSubMenuItem): pass


class BrowserMenuItem(BrowserMenuItem):
  """Improve on the base menu items.

   * support for menu items at a specific level (relative to `setup_depth`
     set up by a call to `setup_request`).

     This is helpful to implement global menus, usable uniformly
     over an object hierachy.

     This extension is triggered by `menu_depth`.
  """
  implements(IBrowserMenuItem)

  menu_depth = None

  # `menu_depth` aware action access
  __action = BrowserMenuItem.action

  def set_action(self, action): self.__action = action

  def get_action(self):
    action = self.__action
    if not action: return action
    depth_offset = self._depth_offset()
    if depth_offset <= 0: return action
    return depth_offset * "../" + action

  action = property(get_action, set_action)


  def available(self):
    return self._depth_offset() >= 0 and super(BrowserMenuItem, self).available()


  def _depth_offset(self):
    md = self.menu_depth
    if md is None: return 0
    r = self.request
    si = r.get(request_tag)
    if si is None: return 0
    return request_depth(r) - si["setup_depth"] - md


class BrowserSubMenuItem(BrowserMenuItem, BrowserSubMenuItem):
  implements(IZopeBrowserSubMenuItem)


class BrowserMenu(BrowserMenu):
  """Extensions for `zope.browsermenu.BrowserMenu`.

  * for submenuitems, use the submenu's title and description as
    item defaults

    Note: the stupid infrastructure uses the specified submenuitem title
    as registration name - therefore, all items must have distinct
    names (otherwise, some items disappear magically).
    If the title starts with `@`, then we assume that this title has
    been used for only this purpose.

  * give each item a unique CSS safe id, derived from the menu id
    and the item index.
  """

  def getMenuItems(self, object, request):
    obj = removeSecurityProxy(object)
    id = self.id
    css_safe_id = css_safe(id)
    il = [
      item
      for (unused, item) in getAdapters((obj, request), self.getMenuItemType())
      if item.available()
      ]
    # order -- see the original code
    ifaces = list(providedBy(obj).__iro__); mk = len(ifaces)
    def if_index(item):
      iface = item._for
      if iface is None: return ifaces.index(Interface)
      if isinstance(obj, iface): return -1
      if IInterface.providedBy(iface): return ifaces.index(iface)
      return mk
    def item_attr(item, attr):
      """*attr* from *item* or the submenu (for a submenu item)."""
      av = getattr(item, attr)
      if (av and not av.startswith("@")) or not IZopeBrowserSubMenuItem.providedBy(item): return av
      return getattr(getUtility(IBrowserMenu, item.submenuId), attr)
    return [
      dict(
        id=css_safe_id + "___" + `i`,
        title=item_attr(item, "title"),
        description=item_attr(item, "description"),
        action=item.action,
        selected=item.selected() and u"selected" or u"",
        icon=item.icon,
        extra=item.extra,
        submenu=(IZopeBrowserSubMenuItem.providedBy(item)
                 and getMenu(item.submenuId, object, request)
                 or None)
        )
      for i, item in enumerate(
          si[3] for si in
          sorted([(if_index(item), item.order, item_attr(item, "title"), item)
                  for item in il])
        )
      ]


request_tag = __name__

def request_depth(r):
  """the depth of request *r*."""
  return len(r._steps)

def setup_request(r):
  """remember information to determine depth in request *r*."""
  r.set(request_tag, dict(setup_depth=request_depth(r) + 1))

def get_request_setup_depth(r): return r[request_tag]["setup_depth"]



def css_safe(id):
  return quote(id, "").replace(".", "%2E").replace("_", "%5F").replace("%", "_")

