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
from ztfy.sendit.packet.interfaces import IPacketInfo

# import Zope3 packages
from zope.interface import Interface
from zope.schema import URI, TextLine, List, Object

# import local packages
from ztfy.file.schema import FileField

from ztfy.sendit import _


class ISenditClientDocument(Interface):
    """Sendit document interface"""

    title = TextLine(title=_("Document title"))
    filename = TextLine(title=_("Document filename"))
    data = FileField(title=_("Document content"))


class ISenditClientPacket(IPacketInfo):
    """Sendit packet interface"""

    documents = List(title=_("Packet documents"),
                     value_type=Object(schema=ISenditClientDocument))


class ISenditClientInfo(Interface):
    """Sendit client base interface"""

    server_url = URI(title=_("SendIt server URL"),
                     description=_("HTTP address of target server"),
                     required=False)

    def searchPrincipals(self, query, names=None, request=None, credentials=None):
        """Search principals matching given query"""

    def getPrincipalInfo(self, principal_id, request=None, credentials=None):
        """Get user profile info"""

    def canRegisterPrincipal(self, request=None, credentials=None):
        """Check if external users registration is available"""

    def registerPrincipal(self, email, firstname, lastname, company_name=None, request=None, credentials=None):
        """Register a new principal with given attributes"""

    def uploadPacket(self, title, description, recipients, notification_mode, backup_time, documents, request=None, credentials=None):
        """Send a new packet with given properties"""


class ISenditClient(ISenditClientInfo):
    """Sendit client interface"""
