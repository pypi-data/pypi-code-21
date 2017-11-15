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
from zope.interface.common.interfaces import IException

# import local interfaces

# import Zope3 packages
from zope.interface import implements, Interface, Attribute

# import local packages

from ztfy.sendit import _


#
# Filtering plug-ins interfaces
#

class IFilteredPacketException(IException):
    """Marker interface for filtered packet exceptions"""


class FilteredPacketException(Exception):
    """Filtered packet exception, raised when an invalid packet has been filtered"""

    implements(IFilteredPacketException)


class IFilteringPluginInfo(Interface):
    """Sendit application filter plug-in interface"""

    marker_interface = Attribute(_("Filter marker interface"))
    config_interface = Attribute(_("Filter configuration interface"))

    def filter(self, packet):
        """Filter given packet.
        
        Raise an exception if packet can't be uploaded.
        Exception message will be returned back to packet transmitter by mail.
        """


class IFilteringPlugin(IFilteringPluginInfo):
    """Sendit application plug-in interface
    
    Filtering plug-ins are declared as named utilities.
    The application administrator can choose which plug-ins to activate.
    """
