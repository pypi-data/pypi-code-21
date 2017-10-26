#
# Copyright (c) 2014 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.myams.interfaces import IMyAMSApplication
from ztfy.myams.interfaces.search import IMyAMSApplicationSearch
from ztfy.myams.viewlet.search.interfaces import ISearchViewlet

# import Zope3 packages
from zope.component import adapts
from zope.i18n import translate
from zope.interface import implements, Interface

# import local packages
from ztfy.baseskin.viewlet import ContentProviderBase
from ztfy.myams.layer import MyAMSLayer
from ztfy.utils.traversing import getParent


class SiteSearchViewlet(ContentProviderBase):
    """Site search content provider"""

    adapts(Interface, MyAMSLayer, Interface)
    implements(ISearchViewlet)

    search_config = None

    def update(self):
        app = getParent(self.context, IMyAMSApplication)
        if app is not None:
            self.search_config = IMyAMSApplicationSearch(app, None)

    @property
    def placeholder(self):
        if self.search_config is not None:
            return translate(self.search_config.site_search_placeholder, context=self.request)

    @property
    def handler(self):
        if self.search_config is not None:
            return self.search_config.site_search_handler


class MobileSearchViewlet(ContentProviderBase):
    """Mobile search content provider"""

    adapts(Interface, MyAMSLayer, Interface)
    implements(ISearchViewlet)

    search_config = None

    def update(self):
        app = getParent(self.context, IMyAMSApplication)
        if app is not None:
            self.search_config = IMyAMSApplicationSearch(app, None)

    @property
    def placeholder(self):
        if self.search_config is not None:
            return translate(self.search_config.mobile_search_placeholder, context=self.request)

    @property
    def handler(self):
        if self.search_config is not None:
            return self.search_config.mobile_search_handler
