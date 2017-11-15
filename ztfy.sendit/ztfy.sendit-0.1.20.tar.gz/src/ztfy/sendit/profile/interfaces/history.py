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
from zope.container.interfaces import IContainer

# import local interfaces

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface
from zope.schema import TextLine, Text, Int, List, Dict, Date, Datetime

# import local packages

from ztfy.sendit import _
from ztfy.security.schema import Principal


class IDocumentHistoryInfo(Interface):
    """Document history base interface"""

    title = TextLine(title=_("Title"),
                     required=False)

    filename = TextLine(title=_("File name"),
                        required=False)

    contentType = TextLine(title=_("Content type"))

    contentSize = Int(title=_("File size"))

    downloaders = Dict(title=_("Downloaders"),
                       required=False,
                       key_type=TextLine(),
                       value_type=Datetime())


class IDocumentHistory(IDocumentHistoryInfo):
    """Document history interface"""


class IPacketHistoryInfo(Interface):
    """Packet history base interface"""

    title = TextLine(title=_("Packet title"))

    description = Text(title=_("Description"),
                       required=False)

    recipients = List(title=_("Packet recipients"),
                      value_type=TextLine())

    creation_time = Datetime(title=_("Creation time"))

    expiration_date = Date(title=_("Packet expiration date"))

    deletion_time = Datetime(title=_("Deletion time"))


class IPacketHistory(IPacketHistoryInfo, IContainer):
    """Packet history interface"""

    contains(IDocumentHistory)


class IProfileHistoryInfo(Interface):
    """Profile history base interface"""

    owner = Principal(title=_("Profile owner"))


class IProfileHistory(IProfileHistoryInfo, IContainer):
    """Profile history interface"""

    contains(IPacketHistory)
