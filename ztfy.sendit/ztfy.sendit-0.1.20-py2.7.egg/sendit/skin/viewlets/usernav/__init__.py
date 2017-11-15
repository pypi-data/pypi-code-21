### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.sendit.profile.interfaces import IProfile

# import Zope3 packages

# import local packages
from ztfy.appskin.viewlets.usernav import UserNavigationMenu

from ztfy.sendit import _


class UserLoginAction(UserNavigationMenu):
    """User login action"""

    title = _("User settings")

    @property
    def label(self):
        return self.request.principal.title

    @property
    def viewURL(self):
        profile = IProfile(self.request.principal)
        if profile.isExternal():
            return "javascript:$.ZTFY.dialog.open('@@settings.html')"


class UserProfileAction(UserNavigationMenu):
    """User profile action"""

    title = _("View user profile")
    label = _("Profile")
    viewURL = "javascript:$.ZTFY.dialog.open('@@profile.html')"
