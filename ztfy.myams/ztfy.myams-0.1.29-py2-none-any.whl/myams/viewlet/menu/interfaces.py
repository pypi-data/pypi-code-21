#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from zope.viewlet.interfaces import IViewletManager, IViewlet

# import local interfaces

# import Zope3 packages
from zope.schema import TextLine, Bool, Dict

# import local packages

from ztfy.myams import _


class IMainMenusViewletManager(IViewletManager):
    """Main menu viewlet manager"""


class IMenu(IViewlet):
    """Menu interface"""

    header = TextLine(title=_("Menu header"),
                      required=False)


class IMenuItem(IViewlet):
    """Menu item interface

    A menu is a viewlet as well as a viewlets manager,
    containing sub-menus
    """

    css_class = TextLine(title=_("CSS class"),
                         required=False)

    icon_class = TextLine(title=_("Icon CSS class"),
                          required=False)

    label = TextLine(title=_("Menu title"),
                     required=False)

    badge = TextLine(title=_("Badge text"),
                     required=False)

    badge_class = TextLine(title=_("Badge CSS class"),
                           required=False)

    notice = TextLine(title=_("Notice text"),
                      required=False)

    notice_class = TextLine(title=_("Notice CSS class"),
                            required=False)

    click_handler = TextLine(title=_("Menu click handler"),
                             required=False)

    url = TextLine(title=_("Menu link location"),
                   required=False,
                   default=u'#')

    target = TextLine(title=_("Menu link target window"),
                      required=False)

    modal_target = Bool(title=_("Modal target"),
                        required=False,
                        default=False)

    data = Dict(title=_("Menu data attributes"),
                key_type=TextLine(),
                value_type=TextLine(),
                required=False)

    def getURL(self):
        """Get menu target URL"""

    def getDataAttributes(self):
        """Get data attributes"""
