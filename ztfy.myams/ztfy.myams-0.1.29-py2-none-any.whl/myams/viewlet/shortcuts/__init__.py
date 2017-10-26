#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.myams.viewlet.shortcuts.interfaces import IShortcutsViewletManager, IShortcutViewlet

# import Zope3 packages
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.baseskin.viewlet import WeightViewletManagerBase, ViewletBase

from ztfy.myams import _


class ShortcutsViewletManager(WeightViewletManagerBase):
    """Shortcuts viewlet manager"""

    implements(IShortcutsViewletManager)


class Shortcut(ViewletBase):
    """Shortcut viewlet"""

    implements(IShortcutViewlet)

    bg_color_class = FieldProperty(IShortcutViewlet['bg_color_class'])
    icon_class = FieldProperty(IShortcutViewlet['icon_class'])
    href = FieldProperty(IShortcutViewlet['href'])
    target = FieldProperty(IShortcutViewlet['target'])
    modal_target = FieldProperty(IShortcutViewlet['modal_target'])
    checked = FieldProperty(IShortcutViewlet['checked'])

    def getURL(self):
        return self.href


class ManagementInterfaceShortcut(Shortcut):
    """Access to management interface"""

    bg_color_class = 'bg-color-orangeDark'
    icon_class = 'fa-gears'
    label = _("Management interface")
    href = '@@properties.html'
    target = '_blank'
    modal_target = False
    checked = False
