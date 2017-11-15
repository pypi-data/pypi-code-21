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
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.skin.app.interfaces import ISenditInboxTable, ISenditOutboxTable
from ztfy.sendit.user.interfaces import ISenditApplicationUsers

# import Zope3 packages
from hurry.query.query import And
from hurry.query.set import AnyOf
from hurry.query.value import Eq
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements

# import local packages
from ztfy.sendit.skin.page import BaseSenditApplicationPage
from ztfy.skin.container import InnerContainerBaseView
from ztfy.utils.property import cached_property
from ztfy.utils.request import getRequestData, setRequestData

from ztfy.sendit import _


class SenditDashboardInboxView(InnerContainerBaseView):
    """Sendit dashboard inbox view"""

    implements(ISenditInboxTable)

    cssClasses = {'table': 'table table-bordered table-striped table-hover'}
    sortOn = None

    @cached_property
    def values(self):
        results = getRequestData('ztfy.sendit.inbox', self.request)
        if results is None:
            query = getUtility(IQuery)
            params = (Eq(('Catalog', 'content_type'), 'IPacket'),
                      AnyOf(('SecurityCatalog', 'ztfy.SenditRecipient'),
                            (self.request.principal.id,) + tuple(self.request.principal.groups)))
            results = query.searchResults(And(*params))
            setRequestData('ztfy.sendit.inbox', results, self.request)
        return sorted(results, key=lambda x: IZopeDublinCore(x).created, reverse=True)[:3]


class SenditDashboardOutboxView(InnerContainerBaseView):
    """Sendit dashboard outbox view"""

    implements(ISenditOutboxTable)

    cssClasses = {'table': 'table table-bordered table-striped table-hover'}
    sortOn = None

    @cached_property
    def quota_pc(self):
        profile = IProfile(self.request.principal)
        return profile.getQuotaUsagePc(self.context)

    @property
    def quota_title(self):
        return translate(_("Used quota: %d%%"), context=self.request) % self.quota_pc

    @cached_property
    def values(self):
        folder = ISenditApplicationUsers(self.context).getUserFolder()
        if folder is not None:
            return sorted(folder.values(), key=lambda x: IZopeDublinCore(x).created, reverse=True)[:3]
        else:
            return ()


class SenditApplicationDashboard(BaseSenditApplicationPage):
    """Sendit application dashboard"""

    shortname = _("Dashboard")

    inbox = None
    outbox = None

    def update(self):
        super(SenditApplicationDashboard, self).update()
        self.inbox = SenditDashboardInboxView(self, self.request)
        self.inbox.update()
        self.outbox = SenditDashboardOutboxView(self, self.request)
        self.outbox.update()
