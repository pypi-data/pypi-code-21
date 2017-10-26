#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface, Attribute

# import local packages

from ztfy.myams import _


class ISearchViewlet(Interface):
    """Site search viewlet interface"""

    placeholder = Attribute(_("Search input placeholder"))

    handler = Attribute(_("Search handler"))
