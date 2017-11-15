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
from datetime import datetime
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations
from zope.dublincore.interfaces import IZopeDublinCore
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.security.interfaces import IPrincipal

# import local interfaces
from ztfy.sendit.packet.interfaces import IDocument, IPacket
from ztfy.sendit.profile.interfaces.history import IDocumentHistory, IPacketHistory, IProfileHistory

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.container.btree import BTreeContainer
from zope.container.contained import Contained
from zope.event import notify
from zope.interface import implementer, implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location.location import locate
from zope.schema.fieldproperty import FieldProperty
from ztfy.security.search import getPrincipal

# import local packages
from ztfy.security.property import RolePrincipalsProperty
from ztfy.utils.timezone import tztime


#
# Document history classes
#

class DocumentHistory(Persistent, Contained):
    """Document history object"""

    implements(IDocumentHistory)

    title = FieldProperty(IDocumentHistory['title'])
    filename = FieldProperty(IDocumentHistory['filename'])
    contentType = FieldProperty(IDocumentHistory['contentType'])
    contentSize = FieldProperty(IDocumentHistory['contentSize'])
    downloaders = FieldProperty(IDocumentHistory['downloaders'])


@adapter(IDocument)
@implementer(IDocumentHistory)
def DocumentHistoryFactory(document):
    history = DocumentHistory()
    history.title = document.title
    history.filename = document.filename
    history.contentType = unicode(document.data.contentType)
    history.contentSize = document.data.getSize()
    downloaders = {}
    for uid, date in (document.downloaders or {}).items():
        downloaders[unicode(getPrincipal(uid).title)] = date
    history.downloaders = downloaders
    return history


#
# Packet history classes
#

class PacketHistory(BTreeContainer):
    """packet history object"""

    implements(IPacketHistory)

    title = FieldProperty(IPacketHistory['title'])
    description = FieldProperty(IPacketHistory['description'])
    recipients = FieldProperty(IPacketHistory['recipients'])
    creation_time = FieldProperty(IPacketHistory['creation_time'])
    expiration_date = FieldProperty(IPacketHistory['expiration_date'])
    deletion_time = FieldProperty(IPacketHistory['deletion_time'])


@adapter(IPacket, IProfileHistory)
@implementer(IPacketHistory)
def PacketHistoryFactory(packet, profile_history):
    history = PacketHistory()
    notify(ObjectCreatedEvent(history))
    locate(history, profile_history)
    history.title = packet.title
    history.description = packet.description
    history.recipients = [unicode(getPrincipal(uid).title) for uid in packet.recipients.split(',')]
    history.creation_time = tztime(IZopeDublinCore(packet).created)
    history.expiration_date = packet.expiration_date.date()
    history.deletion_time = tztime(datetime.utcnow())
    for name, document in packet.items():
        history[name] = IDocumentHistory(document)
    return history


#
# Profile history classes and adapters
#

class UserProfileHistory(BTreeContainer):
    """User profile history"""

    implements(IProfileHistory)

    owner = RolePrincipalsProperty(IProfileHistory['owner'], role='ztfy.SenditProfileOwner')


SENDIT_USER_HISTORY = 'ztfy.sendit.history'

@adapter(IPrincipal)
@implementer(IProfileHistory)
def UserProfileHistoryFactory(principal):
    if principal.id == 'zope.anybody':
        return None
    utility = queryUtility(IPrincipalAnnotationUtility)
    if utility is not None:
        annotations = IAnnotations(utility.getAnnotationsById(principal.id))
        history = annotations.get(SENDIT_USER_HISTORY)
        if history is None:
            history = annotations[SENDIT_USER_HISTORY] = UserProfileHistory()
            history.owner = principal.id
            notify(ObjectCreatedEvent(history))
            locate(history, utility)
        return history


def getUserProfileHistory(principal, create=True):
    if IPrincipal.providedBy(principal):
        principal = principal.id
    if principal == 'zope.anybody':
        return None
    utility = queryUtility(IPrincipalAnnotationUtility)
    if utility is not None:
        annotations = IAnnotations(utility.getAnnotationsById(principal))
        history = annotations.get(SENDIT_USER_HISTORY)
        if (history is None) and create:
            history = annotations[SENDIT_USER_HISTORY] = UserProfileHistory()
            history.owner = principal
            notify(ObjectCreatedEvent(history))
            locate(history, utility)
        return history
