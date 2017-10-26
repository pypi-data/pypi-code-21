#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.myams.viewlet.menu.interfaces import IMainMenusViewletManager, IMenu, IMenuItem

# import Zope3 packages
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.baseskin.viewlet import WeightViewletManagerBase, ViewletBase


class MainMenusViewletManager(WeightViewletManagerBase):
    """Mains menus viewlet manager"""

    implements(IMainMenusViewletManager)


class Menu(WeightViewletManagerBase, ViewletBase):
    """Menu header"""

    implements(IMenu)

    header = FieldProperty(IMenu['header'])

    def __init__(self, context, request, view, manager=None):
        WeightViewletManagerBase.__init__(self, context, request, view)
        ViewletBase.__init__(self, context, request, view, manager)

    def update(self):
        WeightViewletManagerBase.update(self)

    def render(self):
        return ViewletBase.render(self)


class MenuItem(WeightViewletManagerBase, ViewletBase):
    """Menu viewlet"""

    implements(IMenuItem)

    css_class = FieldProperty(IMenuItem['css_class'])
    icon_class = FieldProperty(IMenuItem['icon_class'])
    label = FieldProperty(IMenuItem['label'])
    badge = FieldProperty(IMenuItem['badge'])
    badge_class = FieldProperty(IMenuItem['badge_class'])
    notice = FieldProperty(IMenuItem['notice'])
    notice_class = FieldProperty(IMenuItem['notice_class'])
    click_handler = FieldProperty(IMenuItem['click_handler'])
    url = FieldProperty(IMenuItem['url'])
    target = FieldProperty(IMenuItem['target'])
    modal_target = FieldProperty(IMenuItem['modal_target'])
    data = FieldProperty(IMenuItem['data'])

    def __init__(self, context, request, view, manager=None):
        WeightViewletManagerBase.__init__(self, context, request, view)
        ViewletBase.__init__(self, context, request, view, manager)

    def update(self):
        WeightViewletManagerBase.update(self)

    def render(self):
        return ViewletBase.render(self)

    def getURL(self):
        return self.url

    def getDataAttributes(self):
        data = self.data.copy()
        if self.click_handler:
            data.update({'data-ams-click-handler': self.click_handler})
        return ' '.join('%s=%s' % item for item in data.iteritems())


class MenuDivider(ViewletBase):
    """Menu divider viewlet"""

    implements(IMenuItem)

    header = None
    css_class = 'divider'
    icon_class = None
    label = None
    badge = None
    badge_class = None
    notice = None
    notice_class = None
    click_handler = None
    url = None
    target = None
    modal_target = False
    data = None

    def getURL(self):
        return None
