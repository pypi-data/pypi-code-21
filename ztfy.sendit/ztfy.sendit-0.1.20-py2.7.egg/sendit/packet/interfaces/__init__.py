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
from zope.component.interfaces import IObjectEvent
from zope.container.interfaces import IContainer
from zope.location.interfaces import IContained
from zope.schema.interfaces import IObject, IList

# import local interfaces
from ztfy.base.interfaces import IBaseContentType
from ztfy.scheduler.interfaces import ISchedulerTask

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Text, Choice, Dict, Datetime
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

# import local packages
from ztfy.file.schema import FileField
from ztfy.security.schema import PrincipalList, Principal

from ztfy.sendit import _


#
# Interface vocabularies
#

NOTIFICATION_NONE = 0
NOTIFICATION_NAMED = 1
NOTIFICATION_ALL = 2

NOTIFICATIONS = (_("No notification"),
                 _("Notification on named users download"),
                 _("Notification on all downloads"))

NOTIFICATIONS_VOCABULARY = SimpleVocabulary([SimpleTerm(i, i, t) for i, t in enumerate(NOTIFICATIONS)])


BACKUP_LENGTHS = {1: _("1 week"),
                  2: _("2 weeks"),
                  4: _("4 weeks"),
                  8: _("8 weeks")}

BACKUP_DURATIONS = dict(((i, i*7) for i in BACKUP_LENGTHS.keys()))

BACKUP_DURATIONS_VOCABULARY = SimpleVocabulary([SimpleTerm(i, i, t) for i, t in sorted(BACKUP_LENGTHS.items())])


#
# Document interfaces
#

class IDocumentField(IObject):
    """Document field interface"""


class IDocumentsListField(IList):
    """Documents list field interface"""


class IDocumentInfo(Interface):
    """Document info"""

    title = TextLine(title=_("Title"),
                     required=False)

    data = FileField(title=_("Document data"),
                     required=True)

    filename = Attribute(_("File name"))

    def getSize(self, request=None):
        """Get document size in human form"""


class IDocumentDownloadInfo(Interface):
    """Document download info"""

    downloaders = Dict(title=_("Document downloaders"),
                       required=False,
                       key_type=TextLine(),
                       value_type=Datetime())


class IDocument(IDocumentInfo, IDocumentDownloadInfo, IContained):
    """Document interface"""


class IDocumentDownloadEvent(IObjectEvent):
    """Document download event"""

    request = Attribute(_("Download request"))

    downloader = Attribute(_("Document downloader principal"))

    view = Attribute(_("View in which download occurred"))


#
# Packet interfaces
#

class IPacketInfo(Interface):
    """Basic packet info"""

    title = TextLine(title=_("Packet title"),
                     required=True)

    description = Text(title=_("Description"),
                       required=False)

    recipients = PrincipalList(title=_("Packet recipients"),
                               description=_("Input is assisted. You can search principals individually, "
                                             "or by searching for groups or structures"),
                               required=True)

    notification_mode = Choice(title=_("Notification mode"),
                               description=_("You can choose how you will be notified when your recipients "
                                             "will download this packet"),
                               required=True,
                               vocabulary=NOTIFICATIONS_VOCABULARY,
                               default=NOTIFICATION_NAMED)

    backup_time = Choice(title=_("Conservation duration"),
                         description=_("Nomber of days during which this packet will be available"),
                         required=True,
                         vocabulary=BACKUP_DURATIONS_VOCABULARY,
                         default=2)

    expiration_date = Attribute(_("Packet expiration date"))


class IPacketDownloadInfo(Interface):
    """Packet download info"""

    downloaders = Dict(title=_("Document downloaders"),
                       required=False,
                       key_type=TextLine(),
                       value_type=Datetime())


class IPacket(IPacketInfo, IPacketDownloadInfo, IContainer, IContained, IBaseContentType):
    """Packet info"""

    contains(IDocument)


class IPacketFilteredEvent(IObjectEvent):
    """Packet filter event"""


class IPacketDeleteEvent(IObjectEvent):
    """Packet delete event"""

    view = Attribute(_("View in which deletion occurred"))


#
# Packet archiver task interfaces
#

class IPacketArchiverTaskInfo(Interface):
    """Packet archiver task info"""

    principal_id = Principal(title=_("Task execution principal"),
                             description=_("ID of the principal running the task"),
                             required=True,
                             default=u'zope.manager')


class IPacketArchiverTask(IPacketArchiverTaskInfo, ISchedulerTask):
    """Packet archiver task interface"""
