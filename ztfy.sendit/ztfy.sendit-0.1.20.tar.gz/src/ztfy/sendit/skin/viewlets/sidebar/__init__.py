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
from hurry.query.interfaces import IQuery

# import local interfaces

# import Zope3 packages
from hurry.query.query import And
from hurry.query.value import Eq
from hurry.query.set import AnyOf
from zope.component import getUtility

# import local packages
from ztfy.appskin.viewlets.sidebar import SidebarMenu
from ztfy.utils.request import setRequestData

from ztfy.sendit import _


class UploadSidebarMenu(SidebarMenu):
    """Upload sidebar menu"""

    title = _("Upload new packet")
    cssClass = 'upload btn-danger'


class DashboardSidebarMenu(SidebarMenu):
    """Dashboard sidebar menu"""

    title = _("Dashboard")


class InboxSidebarMenu(SidebarMenu):
    """Inbox sidebar menu"""

    title = _("Inbox")

    @property
    def label(self):
        query = getUtility(IQuery)
        principal_id = self.request.principal.id
        params = (Eq(('Catalog', 'content_type'), 'IPacket'),
                  AnyOf(('SecurityCatalog', 'ztfy.SenditRecipient'), (self.request.principal.id,) + tuple(self.request.principal.groups)))
        results = query.searchResults(And(*params))
        setRequestData('ztfy.sendit.inbox', results, self.request)
        return len([packet for packet in results if principal_id not in packet.downloaders])


class OutboxSidebarMenu(SidebarMenu):
    """Outbox sidebar menu"""

    title = _("Outbox")


class HistorySidebarMenu(SidebarMenu):
    """History sidebar menu"""

    title = _("History")
