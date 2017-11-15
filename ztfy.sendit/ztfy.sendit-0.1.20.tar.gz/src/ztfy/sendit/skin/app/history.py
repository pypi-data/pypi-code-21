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
from z3c.table.interfaces import IBatchProvider

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.profile.interfaces.history import IProfileHistory
from ztfy.sendit.skin.layer import ISenditLayer

# import Zope3 packages
from z3c.table.batch import BatchProvider
from z3c.table.column import GetAttrColumn, Column
from z3c.table.table import Table
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements

# import local packages
from ztfy.sendit.skin.page import BaseSenditApplicationPage
from ztfy.utils.date import formatDatetime, formatDate
from ztfy.utils.size import getHumanSize

from ztfy.sendit import _


class SenditApplicationHistory(BaseSenditApplicationPage, Table):
    """Sendit application history view"""

    shortname = _("History")

    cssClasses = {'table': 'table table-bordered table-striped table-hover'}
    sortOn = None
    batchSize = 20
    startBatchingAt = 20

    def __init__(self, context, request):
        BaseSenditApplicationPage.__init__(self, context, request)
        Table.__init__(self, context, request)

    def update(self):
        BaseSenditApplicationPage.update(self)
        Table.update(self)

    @property
    def values(self):
        history = IProfileHistory(self.request.principal)
        return sorted(history.values(), key=lambda x: x.creation_time, reverse=True)


class SendedColumn(GetAttrColumn):
    """History sended date column"""

    header = _("Send on")
    cssClasses = {'th': 'span3',
                  'td': 'small'}
    weight = 0

    def getValue(self, obj):
        return formatDatetime(obj.creation_time, request=self.request)


class PacketColumn(Column):
    """Outbox packet column"""

    header = _("Packet content")
    template = ViewPageTemplateFile('templates/history_packet.pt')
    weight = 10

    def renderCell(self, item):
        self.context = item
        return self.template(self)

    def getSize(self, document):
        return getHumanSize(document.contentSize)

    def getDate(self, date):
        return formatDatetime(date, request=self.request)

    def getExpirationDate(self):
        return formatDate(self.context.expiration_date, request=self.request)

    def getArchiveDate(self):
        return formatDatetime(self.context.deletion_time, request=self.request)


class SenditApplicationHistoryBatchProvider(BatchProvider):
    """History batch provider"""

    adapts(ISenditApplication, ISenditLayer, SenditApplicationHistory)
    implements(IBatchProvider)

    def renderBatchLink(self, batch, cssClass=None):
        return '<li%s>%s</li>' % (' class="active"' if batch == self.batch else '',
                                  super(SenditApplicationHistoryBatchProvider, self).renderBatchLink(batch, cssClass))
