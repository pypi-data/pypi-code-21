### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2013 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#
##############################################################################


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.sendit.client.interfaces import ISenditClient

# import Zope3 packages
from z3c.jsonrpc.publisher import MethodPublisher
from zope.component import queryUtility

# import local packages


class SenditClientMethodsPublisher(MethodPublisher):
    """Sendit client methods publisher"""

    def findSenditPrincipals(self, query, names=None):
        sendit = queryUtility(ISenditClient)
        if sendit is None:
            return ()
        return sendit.searchPrincipals(query, names, request=self.request)
