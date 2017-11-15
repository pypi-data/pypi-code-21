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
from ztfy.sendit.user.interfaces import IUser

# import Zope3 packages
from zope.container.folder import Folder
from zope.interface import implements

# import local packages
from ztfy.security.property import RolePrincipalsProperty


class User(Folder):
    """User owner folder"""

    implements(IUser)

    owner = RolePrincipalsProperty(IUser['owner'], role="ztfy.SenditProfileOwner")

    def getQuotaUsage(self):
        result = 0
        for packet in self.values():
            for document in packet.values():
                result += document.data.getSize()
        return result
