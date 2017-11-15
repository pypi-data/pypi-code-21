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
from zope.container.interfaces import IReadContainer, IWriteContainer

# import local interfaces
from ztfy.sendit.packet.interfaces import IPacket

# import Zope3 packages
from zope.container.constraints import contains
from zope.interface import Interface

# import local packages
from ztfy.security.schema import Principal

from ztfy.sendit import _


#
# User folder info
#

class IUserPublicInfo(Interface):
    """User public info"""

    owner = Principal(title=_("Profile owner"))


class IUserInfo(Interface):
    """Sendit application user base interface"""

    def getQuotaUsage(self):
        """Get current quota usage"""


class IUserMapping(IReadContainer):
    """Sendit application user mapping interface"""


class IUserWriter(IWriteContainer):
    """Sendit application user writer interface"""


class IUser(IUserPublicInfo, IUserInfo, IUserMapping, IUserWriter):
    """Sendit application user marker interface
    
    User is the container for users packets"""

    contains(IPacket)


#
# Sendit application users interface
#

class ISenditApplicationUsersMapping(IReadContainer):
    """Sendit application users mapping interface"""

    def getUserFolder(self, principal=None):
        """Get profile matching given principal"""

    def addUserFolder(self, principal):
        """Add given user profile to library"""


class ISenditApplicationUsersWriter(IWriteContainer):
    """Sendit application users writer interface"""


class ISenditApplicationUsers(ISenditApplicationUsersMapping, ISenditApplicationUsersWriter):
    """Sendit application users marker interface"""

    contains(IUser)
