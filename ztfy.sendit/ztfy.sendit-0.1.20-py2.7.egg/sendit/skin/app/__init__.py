### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################


# import standard packages

# import Zope3 interfaces
from zope.publisher.interfaces import NotFound

# import local interfaces
from ztfy.appskin.interfaces import IApplicationResources
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.skin.app.interfaces import ISenditApplicationPresentationInfo
from ztfy.sendit.skin.layer import ISenditLayer
from ztfy.skin.interfaces.metas import IContentMetasHeaders

# import Zope3 packages
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements, Interface
from zope.publisher.browser import BrowserPage
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.sendit.skin import ztfy_sendit
from ztfy.skin.metas import LinkMeta
from ztfy.utils.traversing import getParent


class SenditApplicationIconView(BrowserPage):
    """'favicon.ico' application view"""

    def __call__(self):
        icon = ISenditApplicationPresentationInfo(self.context).site_icon
        if icon is not None:
            view = queryMultiAdapter((icon, self.request), Interface, 'index.html')
            if view is not None:
                return view()
        raise NotFound(self.context, 'favicon.ico', self.request)


class SenditApplicationMetasHeadersAdapter(object):
    """Sendit application metas adapter"""

    adapts(Interface, ISenditLayer)
    implements(IContentMetasHeaders)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def metas(self):
        result = []
        site = getParent(self.context, ISenditApplication)
        if site is not None:
            info = ISenditApplicationPresentationInfo(site)
            if info.site_icon:
                result.append(LinkMeta('icon', info.site_icon.contentType, absoluteURL(info.site_icon, self.request)))
            else:
                result.append(LinkMeta('icon', 'image/png', '%s/@@/favicon.ico' % absoluteURL(site, self.request)))
        else:
            result.append(LinkMeta('icon', 'image/png', '/@@/favicon.ico'))
        return result


class SenditApplicationResourcesAdapter(object):
    """Sendit application resources adapter"""

    adapts(Interface, ISenditLayer)
    implements(IApplicationResources)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    resources = (ztfy_sendit,)
