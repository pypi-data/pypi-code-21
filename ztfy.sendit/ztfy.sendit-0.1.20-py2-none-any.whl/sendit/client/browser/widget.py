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

# import Zope3 packages
from z3c.form.widget import FieldWidget
from zope.component import queryUtility

# import local packages
from ztfy.sendit.skin.packet.widget import PacketRecipientsWidget
from ztfy.sendit.client.interfaces import ISenditClient


class SenditClientPacketRecipientsWidget(PacketRecipientsWidget):
    """Sendit client packet recipients widget"""

    query_name = 'findSenditPrincipals'
    registration_view_name = 'register_sendit_user.html'

    def canRegisterUser(self):
        client = queryUtility(ISenditClient)
        if client is None:
            return False
        return client.canRegisterPrincipal(self.request)


def SenditClientPacketRecipientsWidgetFactory(field, request):
    return FieldWidget(field, SenditClientPacketRecipientsWidget(request))
