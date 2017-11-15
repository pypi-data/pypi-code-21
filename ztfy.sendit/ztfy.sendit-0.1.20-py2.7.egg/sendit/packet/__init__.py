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
from datetime import timedelta
from persistent import Persistent

# import Zope3 interfaces
from zope.dublincore.interfaces import IZopeDublinCore

# import local interfaces
from ztfy.sendit.packet.interfaces import IPacket, IDocument, \
                                          IDocumentDownloadEvent, IPacketDeleteEvent, \
                                          BACKUP_DURATIONS

# import Zope3 packages
from zope.app.content import queryContentType
from zope.component.interfaces import ObjectEvent
from zope.container.contained import Contained
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.base.ordered import OrderedContainer
from ztfy.extfile.blob import BlobFile
from ztfy.file.property import FileProperty
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.size import getHumanSize
from ztfy.utils.timezone import tztime


class Document(Persistent, Contained):
    """Document persistent class"""

    implements(IDocument)

    title = FieldProperty(IDocument['title'])
    data = FileProperty(IDocument['data'], klass=BlobFile)
    filename = None

    downloaders = FieldProperty(IDocument['downloaders'])

    @property
    def content_type(self):
        return queryContentType(self).__name__

    def getSize(self, request=None):
        return getHumanSize(self.data.getSize(), request)


class DocumentDownloadEvent(ObjectEvent):
    """Document download event"""

    implements(IDocumentDownloadEvent)

    def __init__(self, object, request, view):
        self.object = object
        self.request = request
        self.downloader = request.principal
        self.view = view


class Packet(OrderedContainer):
    """Packet persistent class"""

    implements(IPacket)

    title = FieldProperty(IPacket['title'])
    description = FieldProperty(IPacket['description'])
    recipients = RolePrincipalsProperty(IPacket['recipients'], role='ztfy.SenditRecipient')
    notification_mode = FieldProperty(IPacket['notification_mode'])
    backup_time = FieldProperty(IPacket['backup_time'])

    @property
    def content_type(self):
        return queryContentType(self).__name__

    @property
    def expiration_date(self):
        creation_date = IZopeDublinCore(self).created
        return tztime(creation_date) + timedelta(days=BACKUP_DURATIONS[self.backup_time])

    @property
    def downloaders(self):
        result = {}
        [ result.update(document.downloaders or {}) for document in self.values() ]
        return result


class PacketDeleteEvent(ObjectEvent):
    """Packet delete event"""

    implements(IPacketDeleteEvent)

    def __init__(self, object, view):
        self.object = object
        self.view = view
