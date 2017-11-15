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
from hurry.query.interfaces import IQuery
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.sendit.skin.app.interfaces import ISenditInboxTable

# import Zope3 packages
from hurry.query import And
from hurry.query.value import Eq
from hurry.query.set import AnyOf
from z3c.table.column import Column, GetAttrColumn
from z3c.table.table import Table
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implements

# import local packages
from ztfy.security.search import getPrincipal
from ztfy.sendit.skin.page import BaseSenditApplicationPage
from ztfy.sendit.user.interfaces import IUser
from ztfy.utils.date import formatDatetime
from ztfy.utils.property import cached_property
from ztfy.utils.request import getRequestData, setRequestData
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


class SenditApplicationInbox(BaseSenditApplicationPage, Table):
    """Sendit application inbox view"""

    implements(ISenditInboxTable)

    shortname = _("Inbox")

    cssClasses = {'table': 'table table-bordered table-striped table-hover'}
    sortOn = None
    batchSize = 9999

    def __init__(self, context, request):
        BaseSenditApplicationPage.__init__(self, context, request)
        Table.__init__(self, context, request)

    def update(self):
        BaseSenditApplicationPage.update(self)
        Table.update(self)

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
        return sorted(results, key=lambda x: IZopeDublinCore(x).created, reverse=True)


class SenderColumn(GetAttrColumn):
    """Inbox sender column"""

    header = _("Sender")
    cssClasses = {'th': 'span3'}
    weight = 0

    def getValue(self, obj):
        user = getParent(obj, IUser)
        return '%s<br /><span class="small">%s</span>' % \
               (getPrincipal(user.owner).title,
                translate(_("Sent on: %s"), context=self.request) %
                formatDatetime(IZopeDublinCore(obj).created, request=self.request))


class PacketColumn(Column):
    """Inbox packet column"""

    header = _("Packet content")
    template = ViewPageTemplateFile('templates/inbox_packet.pt')
    weight = 10

    def renderCell(self, item):
        self.context = item
        return self.template(self)

    def getDate(self, date):
        return formatDatetime(date, request=self.request)
