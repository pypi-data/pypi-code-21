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

# import local interfaces
from ztfy.security.browser.widget.interfaces import IPrincipalListWidget
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.profile.interfaces import IProfile

# import Zope3 packages
from z3c.form.widget import FieldWidget

# import local packages
from ztfy.security.browser.widget.principal import PrincipalListWidget
from ztfy.utils.traversing import getParent


class IPacketRecipientsWidget(IPrincipalListWidget):
    """Packet recipients widget interface"""

    def canRegisterUser(self):
        """Check if user can register new external users"""


class PacketRecipientsWidget(PrincipalListWidget):
    """Packet recipients widget"""

    query_name = 'findFilteredPrincipals'
    registration_view_name = 'register_user.html'

    def canRegisterUser(self):
        profile = IProfile(self.request.principal)
        name, _plugin, _info = profile.getAuthenticatorPlugin()
        if name is None:
            return False
        app = getParent(self.context, ISenditApplication)
        return (app is not None) and (name in app.internal_auth_plugins)


def PacketRecipientsWidgetFactory(field, request):
    return FieldWidget(field, PacketRecipientsWidget(request))
