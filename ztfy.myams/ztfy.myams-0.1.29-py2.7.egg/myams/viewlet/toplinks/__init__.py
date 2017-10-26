#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.myams.viewlet.toplinks.interfaces import ITopLinksViewletManager, ITopLinksViewlet, ITopLinksMenu, \
    ITopTabsViewlet, ITopTabsTab

# import Zope3 packages
from zope.i18n import translate
from zope.interface import implements
from zope.viewlet.manager import WeightOrderedViewletManager

# import local packages
from ztfy.baseskin.viewlet import WeightViewletManagerBase, ViewletBase


class TopLinksViewletManager(WeightOrderedViewletManager):
    """Top links viewlet manager"""

    implements(ITopLinksViewletManager)


#
# Top links viewlet
#

class TopLinksViewlet(WeightViewletManagerBase, ViewletBase):
    """Top links viewlet"""

    implements(ITopLinksViewlet)

    label = u"Label:"
    css_class = u'top-menu'
    dropdown_label = u"Dropdown label"

    def __init__(self, context, request, view, manager=None):
        WeightViewletManagerBase.__init__(self, context, request, view)
        ViewletBase.__init__(self, context, request, view, manager)

    def update(self):
        WeightViewletManagerBase.update(self)


class TopLinksMenu(ViewletBase):
    """Top link menu"""

    implements(ITopLinksMenu)

    css_class = u""
    label = u"Menu label"
    click_handler = None
    url = u"#"
    data = {}

    def render(self):
        if self.css_class == u'divider':
            return u'<li class="divider"></li>'
        else:
            label = translate(self.label, context=self.request)
            return u'''<li class="%s">
                        <a href="%s" %s>%s</a>
                    </li>''' % (self.css_class,
                                self.url,
                                self.getDataAttributes(),
                                unicode(label, 'utf-8') if isinstance(label, str) else label)

    def getDataAttributes(self):
        data = self.data.copy()
        if self.click_handler:
            data.update({'data-ams-click-handler': self.click_handler})
        return ' '.join('%s=%s' % item for item in data.iteritems())


#
# Top tabs viewlet
#

class TopTabsViewlet(WeightViewletManagerBase, ViewletBase):
    """Top tabs viewlet"""

    implements(ITopTabsViewlet)

    label = u"Label:"
    css_class = u'top-tabs'

    def __init__(self, context, request, view, manager=None):
        WeightViewletManagerBase.__init__(self, context, request, view)
        ViewletBase.__init__(self, context, request, view, manager)

    def update(self):
        WeightViewletManagerBase.update(self)


class TopTabsTab(ViewletBase):
    """Top tabs tab"""

    implements(ITopTabsTab)

    css_class = u""
    label = u"Tab label"
    click_handler = None
    url = u"#"
    data = {'data-toggle': 'tab'}

    def render(self):
        label = translate(self.label, context=self.request)
        return u'''<li class="%s">
                    <a href="%s" %s>%s</a>
                </li>''' % (self.css_class,
                            self.url,
                            self.getDataAttributes(),
                            unicode(label, 'utf-8') if isinstance(label, str) else label)

    def getDataAttributes(self):
        data = self.data.copy()
        if self.click_handler:
            data.update({'data-ams-click-handler': self.click_handler})
        return ' '.join('%s=%s' % item for item in data.iteritems())
