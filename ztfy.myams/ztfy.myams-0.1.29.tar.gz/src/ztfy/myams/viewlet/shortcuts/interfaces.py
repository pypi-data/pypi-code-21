#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from zope.viewlet.interfaces import IViewlet, IViewletManager

# import local interfaces

# import Zope3 packages
from zope.interface import Attribute
from zope.schema import TextLine, Bool

# import local packages

from ztfy.myams import _


class IShortcutsViewletManager(IViewletManager):
    """Shortcuts viewlet manager interface"""


class IShortcutViewlet(IViewlet):
    """Shortcut viewlet interface"""

    bg_color_class = TextLine(title=_("Shortcut CSS class"))

    icon_class = TextLine(title=_("Shortcut icon class"))

    label = Attribute(_("Shortcut title"))

    href = TextLine(title=_("Shortcut target URL"))

    target = TextLine(title=_("Window target"),
                      required=False)

    modal_target = Bool(title=_("Modal target"),
                        required=True,
                        default=True)

    checked = TextLine(title=_("Checked shortcut class"),
                       required=False)

    def getURL(self):
        """Return shortcut absolute URL"""
