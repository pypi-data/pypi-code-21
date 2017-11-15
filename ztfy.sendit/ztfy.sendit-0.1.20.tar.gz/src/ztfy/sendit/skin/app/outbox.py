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
from z3c.form.interfaces import HIDDEN_MODE
from z3c.json.interfaces import IJSONWriter
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.security.interfaces import ISecurityManager
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.skin.app.interfaces import ISenditOutboxTable
from ztfy.sendit.user.interfaces import ISenditApplicationUsers

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import jsaction, ajax
from z3c.table.column import Column, GetAttrColumn
from z3c.table.table import Table
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, Interface
from zope.schema import Bool, Int
from zope.traversing.api import getParent, getName

# import local packages
from ztfy.jqueryui import jquery_multiselect_css
from ztfy.security.search import getPrincipal
from ztfy.sendit.packet import PacketDeleteEvent
from ztfy.sendit.skin.page import BaseSenditApplicationPage
from ztfy.skin.form import BaseDialogAddForm
from ztfy.utils.catalog import getIntIdUtility
from ztfy.utils.date import formatDatetime, formatDate

from ztfy.sendit import _


class SenditApplicationOutbox(BaseSenditApplicationPage, Table):
    """Sendit application outbox page"""

    implements(ISenditOutboxTable)

    shortname = _("Outbox")

    cssClasses = {'table': 'table table-bordered table-striped table-hover'}
    sortOn = None
    batchSize = 9999

    def __init__(self, context, request):
        BaseSenditApplicationPage.__init__(self, context, request)
        Table.__init__(self, context, request)

    def update(self):
        BaseSenditApplicationPage.update(self)
        Table.update(self)
        jquery_multiselect_css.need()

    @property
    def quota_pc(self):
        profile = IProfile(self.request.principal)
        return profile.getQuotaUsagePc(self.context)

    @property
    def quota_title(self):
        return translate(_("Used quota: %d%%"), context=self.request) % self.quota_pc

    @property
    def values(self):
        folder = ISenditApplicationUsers(self.context).getUserFolder()
        if folder is not None:
            return sorted(folder.values(), key=lambda x: IZopeDublinCore(x).created, reverse=True)
        else:
            return ()


class SendedColumn(GetAttrColumn):
    """Inbox sended date column"""

    header = _("Send on")
    cssClasses = {'th': 'span3',
                  'td': 'small'}
    weight = 0

    def getValue(self, obj):
        intids = getIntIdUtility(request=self.request)
        packet_oid = intids.register(obj)
        return """%s
               <br /><br /><br />
               <div class="centered" id="delete_%d">
                   <input type="button" class="btn btn-small btn-warning" value="%s" onclick="$.ZTFY.dialog.open('@@deletePacket.html?packet_oid:int=%d');" />
               </div>
               """ % (formatDatetime(IZopeDublinCore(obj).created, request=self.request),
                      packet_oid,
                      translate(_("Delete packet"), context=self.request),
                      packet_oid)


class PacketColumn(Column):
    """Outbox packet column"""

    header = _("Packet content")
    template = ViewPageTemplateFile('templates/outbox_packet.pt')
    weight = 10

    def renderCell(self, item):
        self.context = item
        return self.template(self)

    def getPrincipal(self, principal):
        return getPrincipal(principal).title

    def getDate(self, date):
        return formatDatetime(date, request=self.request)

    def getExpirationDate(self):
        return formatDate(self.context.expiration_date, request=self.request)


#
# Packet delete form
#

class ISenditOutboxDeleteInfo(Interface):
    """Packet deletion form info"""

    packet_oid = Int(title=_("Packet OID"),
                     required=True)

    notify_recipients = Bool(title=_("Notify recipients?"),
                             description=_("Do you want to notify recipients of this packet that it won't "
                                           "be available anymore?"),
                             required=True,
                             default=True)


class ISenditOutboxDeleteButtons(Interface):
    """Default dialog add form buttons"""

    delete = jsaction.JSButton(title=_("Delete packet"))
    cancel = jsaction.JSButton(title=_("Cancel"))


class SenditOutboxDeleteForm(BaseDialogAddForm):
    """Delete packet from outbox"""

    legend = _("Delete packet?")
    help = _("You can delete this packet to get more free space without waiting for its expiration date.\n"
             "But it won't be available anymore for its recipients")

    fields = field.Fields(ISenditOutboxDeleteInfo)
    buttons = button.Buttons(ISenditOutboxDeleteButtons)

    def updateWidgets(self):
        super(SenditOutboxDeleteForm, self).updateWidgets()
        self.widgets['packet_oid'].value = self.request.form.get('packet_oid')
        self.widgets['packet_oid'].mode = HIDDEN_MODE

    @jsaction.handler(buttons['delete'])
    def add_handler(self, event, selector):
        return '$.ZTFY.form.add(this.form, null, $.ZTFY.sendit.form.deletePacketCallback);'

    @jsaction.handler(buttons['cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZTFY.dialog.close();'

    def updateActions(self):
        super(SenditOutboxDeleteForm, self).updateActions()
        self.actions['delete'].addClass('btn btn-inverse')
        self.actions['cancel'].addClass('btn')

    @ajax.handler
    def ajaxCreate(self):
        writer = getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return writer.write(self.getAjaxErrors())
        packet_oid = data.get('packet_oid')
        intids = getIntIdUtility(request=self.request)
        packet = intids.queryObject(packet_oid)
        if (packet is not None) and ISecurityManager(packet).canUsePermission('ztfy.ManageSenditPacket'):
            if data.get('notify_recipients'):
                notify(PacketDeleteEvent(packet, self))
            parent = getParent(packet)
            del parent[getName(packet)]
            return writer.write({'output': u"OK",
                                 'packet_oid': packet_oid})
        else:
            return writer.write({'output': u'NONE'})
