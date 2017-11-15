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
import random
import tempfile
import uuid
import zipfile
from datetime import datetime
from urllib import quote

# import Zope3 interfaces
from z3c.form.interfaces import IErrorViewSnippet
from zope.security.interfaces import Unauthorized

# import local interfaces
from ztfy.security.interfaces import ISecurityManager
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.packet.interfaces import IPacket, IPacketInfo, IDocumentInfo
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.user.interfaces import ISenditApplicationUsers
from ztfy.skin.interfaces import ICustomUpdateSubForm

# import Zope3 packages
from z3c.form import field, button
from zope.component import getMultiAdapter, queryMultiAdapter
from zope.event import notify
from zope.i18n import translate
from zope.interface import implements, Interface, Invalid
from zope.lifecycleevent import ObjectCreatedEvent
from zope.publisher.browser import FileUpload
from zope.security.proxy import removeSecurityProxy
from zope.traversing.browser.absoluteurl import absoluteURL

# import local packages
from ztfy.sendit.packet import Packet, Document, DocumentDownloadEvent
from ztfy.sendit.profile import getUserProfile
from ztfy.sendit.skin.packet.widget import PacketRecipientsWidgetFactory
from ztfy.sendit.skin.page import BaseSenditProtectedPage
from ztfy.skin.form import BaseAddForm, AddSubForm
from ztfy.skin.page import TemplateBasedPage
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


#
# Packet documents schema field
#

class PacketDocumentsSubform(AddSubForm):
    """Packets documents sub-form"""

    implements(ICustomUpdateSubForm)

    legend = _("Selected documents")

    fields = field.Fields(IDocumentInfo)
    prefix = 'documents.'
    ignoreContext = True

    def extractData(self, setErrors=True):
        self.widgets.setErrors = setErrors
        doc_data = { 'documents': [] }
        errors = ()
        prefix = self.prefix + self.widgets.prefix
        fieldnames = ('title', 'data')
        values = [ self.request.form.get(prefix + name) for name in fieldnames ]
        [ doc_data['documents'].append({ 'title': title,
                                         'data': data }) for title, data in zip(*values) if data ]
        if not doc_data['documents']:
            data_widget = self.widgets['data']
            error = Invalid(_("You must provide at least one document"))
            view = getMultiAdapter((error, self.request, data_widget, data_widget.field, self, self.context),
                                   IErrorViewSnippet)
            view.update()
            errors += (view,)
        if errors and setErrors:
            self.widgets.errors = self.errors = errors
        return doc_data, errors

    def updateContent(self, object, data):
        data, _errors = self.extractData()
        for doc_data in data.get('documents'):
            document = Document()
            notify(ObjectCreatedEvent(document))
            document_name = str(uuid.uuid1(random.randrange(0, 1 << 48L) | 0x010000000000L))
            object[document_name] = document
            document.title = doc_data['title'] or translate(_("< document without title >"), context=self.request)
            document.data = doc_data['data']
            if isinstance(doc_data['data'], FileUpload):
                document.filename = doc_data['data'].filename


class PacketAddForm(BaseSenditProtectedPage, BaseAddForm):
    """Sendit packet add form"""

    permission = 'ztfy.UploadSenditPacket'
    legend = _("Uploading a new packet")
    shortname = _("New packet upload")
    icon_class = 'icon-upload'

    fields = field.Fields(IPacketInfo).select('title', 'description',
                                              'recipients', 'notification_mode', 'backup_time')
    fields['recipients'].widgetFactory = PacketRecipientsWidgetFactory

    def __call__(self):
        try:
            BaseSenditProtectedPage.__call__(self)
        except Unauthorized:
            return u''
        else:
            return BaseAddForm.__call__(self)

    def createSubForms(self):
        self.documents = PacketDocumentsSubform(self.context, self.request, self)
        return (self.documents,)

    def updateWidgets(self):
        super(PacketAddForm, self).updateWidgets()
        profile = IProfile(self.request.principal)
        if profile.isExternal():
            app = getParent(self.context, ISenditApplication)
            self.widgets['recipients'].auth_plugins = set(app.single_auth_plugins) & set(app.internal_auth_plugins)
        self.widgets['notification_mode'].addClass('span6')

    def updateActions(self):
        super(PacketAddForm, self).updateActions()
        self.actions['upload'].addClass('btn btn-inverse')

    @button.buttonAndHandler(_('Upload packet'), name='upload')
    def handleUpload(self, action):
        profile = getUserProfile(self.request.principal)
        if profile.getQuotaUsage(self.context) >= (profile.getQuotaSize(self.context) * 1024 * 1024):
            self.status = _("Your storage quota is exceeded. You can't upload any new packet "
                            "without freeing some space...")
            return
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    def extractData(self, setErrors=True):
        data, errors = super(PacketAddForm, self).extractData(setErrors)
        for subform in self.subforms:
            _data, sub_errors = subform.extractData(setErrors)
            errors += sub_errors
        if errors:
            if setErrors:
                self.widgets.errors = errors
            self.status = self.formErrorsMessage
        return data, errors

    def create(self, data):
        return Packet()

    def add(self, object):
        # create packet
        packet_name = str(uuid.uuid1(random.randrange(0, 1 << 48L) | 0x010000000000L))
        user = ISenditApplicationUsers(self.context).getUserFolder(self.request.principal)
        user[packet_name] = object

    def nextURL(self):
        return '%s/@@outbox.html' % absoluteURL(self.context, self.request)


class PacketRejectView(TemplateBasedPage):
    """Rejected packet exception view"""

    shortname = _("Upload error!")

    def render(self):
        self.request.response.setStatus(403)
        return super(PacketRejectView, self).render()


class PacketDownloadView(object):
    """Download full packet as ZIP file"""

    permission = 'ztfy.ViewSenditPacket'

    def download(self):
        security = ISecurityManager(self.context, None)
        if not security.canUsePermission(self.permission):
            app = getParent(self.context, ISenditApplication)
            self.request.response.redirect('%s/@@login.html?came_from=%s' % (absoluteURL(self.context, self.request),
                                                                             quote(absoluteURL(self, self.request), ':/')),
                                           trusted=app.trusted_redirects)
            raise Unauthorized
        packet = self.context
        # init ZIP file
        principal_id = self.request.principal.id
        output = tempfile.TemporaryFile(suffix='.zip')
        zip = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
        # store documents data
        for document in packet.values():
            zip.writestr(document.filename.encode('utf-8'), document.data.data)
            if principal_id not in packet.downloaders:
                notify(DocumentDownloadEvent(document, self.request, self))
            if principal_id not in (document.downloaders or {}):
                downloaders = removeSecurityProxy(document.downloaders) or {}
                downloaders[principal_id] = datetime.utcnow()
                document.downloaders = downloaders
        zip.close()
        self.request.response.setHeader('Content-Type', 'application/zip')
        self.request.response.setHeader('Content-Disposition',
                                        'attachment; filename="%s.zip"' % packet.title.encode('utf-8'))
        return output


class DocumentDownloadView(object):
    """Document download view"""

    permission = 'ztfy.ViewSenditPacket'

    def download(self):
        security = ISecurityManager(self.context, None)
        if not security.canUsePermission(self.permission):
            app = getParent(self.context, ISenditApplication)
            self.request.response.redirect('%s/@@login.html?came_from=%s' % (absoluteURL(self.context, self.request),
                                                                             quote(absoluteURL(self, self.request), ':/')),
                                           trusted=app.trusted_redirects)
            raise Unauthorized
        document = self.context
        packet = getParent(document, IPacket)
        # update document download time
        principal_id = self.request.principal.id
        if principal_id not in packet.downloaders:
            notify(DocumentDownloadEvent(document, self.request, self))
        if principal_id not in (document.downloaders or {}):
            downloaders = removeSecurityProxy(document.downloaders) or {}
            downloaders[principal_id] = datetime.utcnow()
            document.downloaders = downloaders
        # return document
        view = queryMultiAdapter((document.data, self.request), Interface, 'index.html')
        if view is not None:
            if document.filename is not None:
                self.request.response.setHeader('Content-Disposition',
                                                'attachment; filename="%s"' % document.filename.encode('utf-8'))
            return view()
