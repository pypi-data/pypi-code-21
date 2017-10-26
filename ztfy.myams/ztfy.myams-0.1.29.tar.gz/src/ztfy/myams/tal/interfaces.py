#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface

# import local packages


class IMyAMSTalesAPI(Interface):
    """myams: TALES namespace interface"""

    def data(self):
        """Get context data"""

    def configuration(self):
        """Get application configuration"""

    def static_configuration(self):
        """Get application static configuration"""

    def resources(self):
        """Include application's Fanstatic resources"""
