#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.interface import Interface
from zope.schema import TextLine

# import local packages

from ztfy.myams import _


class IMyAMSApplicationSearch(Interface):
    """MyAMS application search configuration interface"""

    site_search_placeholder = TextLine(title=_("Site search placeholder"),
                                       required=False,
                                       default=_("Search..."))

    site_search_handler = TextLine(title=_("Site search handler"),
                                   required=False,
                                   default=u"#search.html")

    mobile_search_placeholder = TextLine(title=_("Mobile search placeholder"),
                                         required=False,
                                         default=_("Search..."))

    mobile_search_handler = TextLine(title=_("Mobile search handler"),
                                     required=False,
                                     default=u'#search.html')
