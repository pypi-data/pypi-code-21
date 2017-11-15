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

# import Zope3 packages

# import local packages
from ztfy.appskin.viewlets.actions import ActionMenu
from ztfy.sendit.profile import getUserProfile

from ztfy.sendit import _


class UploadAction(ActionMenu):
    """Upload action"""

    label = _("Upload new packet")

    def __new__(cls, context, request, view, manager):
        profile = getUserProfile(request.principal)
        if profile.getQuotaUsage(context) >= (profile.getQuotaSize(context) * 1024 * 1024):
            return None
        return ActionMenu.__new__(cls)
