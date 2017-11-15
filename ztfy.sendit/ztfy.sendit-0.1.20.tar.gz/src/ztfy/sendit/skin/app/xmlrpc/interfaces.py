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

# import Zope3 packages
from zope.interface import Interface

# import local packages


class ISenditApplicationServices(Interface):
    """Sendit application XML-RPC services definition"""

    def searchPrincipals(self, query, names=None):
        """Search principals matching given query"""

    def getPrincipalInfo(self, principal_id):
        """Get user profile info"""

    def canRegisterPrincipal(self):
        """Check if external users registration is opened"""

    def registerPrincipal(self, email, firstname, lastname, company_name=None):
        """Create a new profile with given attributes"""

    def uploadPacket(self, title, description, recipients, notification_mode, backup_time, documents):
        """Send a new packet with given properties"""
