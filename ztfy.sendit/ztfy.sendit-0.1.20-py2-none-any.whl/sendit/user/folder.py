### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#
##############################################################################


# import standard packages

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.user.interfaces import ISenditApplicationUsers

# import Zope3 packages
from zope.component import adapter
from zope.container.folder import Folder
from zope.interface import implementer, implements
from zope.location import locate
from zope.publisher.interfaces import NotFound
from zope.security.interfaces import IPrincipal

# import local packages
from ztfy.sendit.user import User
from ztfy.utils.request import queryRequest


class UsersFolder(Folder):
    """Users folder class"""

    implements(ISenditApplicationUsers)

    def getUserFolder(self, principal=None):
        if principal is None:
            request = queryRequest()
            if request is not None:
                principal = request.principal
        if principal is None:
            raise NotFound(self, principal)
        if IPrincipal.providedBy(principal):
            principal = principal.id
        return self.get(principal)

    def addUserFolder(self, principal=None):
        if principal is None:
            request = queryRequest()
            if request is not None:
                principal = request.principal
        if principal is None:
            raise NotFound(self, principal)
        if IPrincipal.providedBy(principal):
            principal = principal.id
        # initialize users folder
        user = self.get(principal)
        if user is None:
            user = self[principal] = User()
            user.owner = principal
        return user


SENDIT_APPLICATION_USERS_KEY = 'ztfy.sendit.users'

@adapter(ISenditApplication)
@implementer(ISenditApplicationUsers)
def SenditApplicationUsersFactory(context):
    annotations = IAnnotations(context)
    container = annotations.get(SENDIT_APPLICATION_USERS_KEY)
    if container is None:
        container = annotations[SENDIT_APPLICATION_USERS_KEY] = UsersFolder()
        locate(container, context, '++users++')
    return container
