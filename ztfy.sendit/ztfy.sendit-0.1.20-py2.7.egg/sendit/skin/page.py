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
from urllib import quote

# import Zope3 interfaces
from zope.security.interfaces import Unauthorized

# import local interfaces
from ztfy.security.interfaces import ISecurityManager

# import Zope3 packages
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.traversing import getParent


class BaseSenditProtectedPage(object):
    """Base sendit protected page"""

    permission = "ztfy.ViewSenditApplication"

    def __call__(self):
        security = ISecurityManager(self.context, None)
        if not security.canUsePermission(self.permission):
            app = getParent(self.context, ISenditApplication)
            self.request.response.redirect('%s/@@login.html?came_from=%s' % (absoluteURL(self.context, self.request),
                                                                             quote(absoluteURL(self, self.request), ':/')),
                                           trusted=app.trusted_redirects)
            raise Unauthorized


class BaseSenditApplicationPage(BaseSenditProtectedPage, TemplateBasedPage):
    """Base sendit application page"""

    def __call__(self):
        try:
            BaseSenditProtectedPage.__call__(self)
        except Unauthorized:
            return u''
        else:
            return TemplateBasedPage.__call__(self)
