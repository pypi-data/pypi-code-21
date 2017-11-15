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
from ztfy.appskin.interfaces import IApplicationPresentationInfo

# import Zope3 packages
from zope.interface import Interface

# import local packages


class ISenditApplicationPresentationInfo(IApplicationPresentationInfo):
    """Sendit application presentation info"""


class ISenditInboxTable(Interface):
    """Sendit inbox table marker interface"""


class ISenditOutboxTable(Interface):
    """Sendit outbox table marker interface"""
