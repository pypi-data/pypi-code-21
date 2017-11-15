### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

# import local interfaces

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher

# import local packages
from ztfy.security.search import findPrincipals


def getPrincipalTitle(principal):
    title = principal.title
    if '@' in principal.id:
        _name, domain = principal.id.split('@')
        title = '%s (%s)' % (title, domain)
    return title


class PrincipalSearchView(MethodPublisher):
    """Filtered principal search view"""

    def findFilteredPrincipals(self, query, names=None):
        app = self.context
        return [{ 'value': principal.id,
                  'caption': getPrincipalTitle(principal) } for principal in findPrincipals(query, names)
                                                                          if principal.id not in (app.excluded_principals or ()) ]
