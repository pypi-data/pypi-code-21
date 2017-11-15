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
from datetime import datetime

# import Zope3 interfaces
from zope.dublincore.interfaces import IZopeDublinCore
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.profile.interfaces import IProfilesCleanerTask

# import Zope3 packages
from zope.component import queryUtility, getUtility
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.scheduler.task import BaseTask
from ztfy.sendit.profile import SENDIT_USER_PROFILE
from ztfy.utils.timezone import tztime
from ztfy.utils.traversing import getParent


class ProfilesCleanerTask(BaseTask):
    """Profiles cleaning task
    
    This task is automatically deleting non-activated profiles
    """

    implements(IProfilesCleanerTask)

    def run(self, report):
        count = 0
        principal_annotations = queryUtility(IPrincipalAnnotationUtility)
        if principal_annotations is None:
            raise Exception("No principal annotations utility found")
        principal_annotations = removeSecurityProxy(principal_annotations)
        app = getParent(self, ISenditApplication)
        auth_plugin = getUtility(IAuthenticatorPlugin, app.external_auth_plugin)
        prefix_length = len(auth_plugin.prefix)
        for principal_id, annotations in principal_annotations.annotations.items():
            # only check for external users
            if auth_plugin.principalInfo(principal_id) is None:
                continue
            # get SendIt profile
            profile = annotations.get(SENDIT_USER_PROFILE)
            if (profile is not None) and not profile.activated:
                created = IZopeDublinCore(profile).created
                # get time elapsed since profile creation date
                if (tztime(datetime.utcnow()) - tztime(created)).days > app.confirmation_delay:
                    report.write(' - deleting profile %s (created on %s)\n' % (annotations.__name__,
                                                                               tztime(created).strftime('%Y-%m-%d')))
                    del annotations[SENDIT_USER_PROFILE]
                    # delete all profile annotations if empty
                    if not annotations.data:
                        del principal_annotations.annotations[principal_id]
                    # delete user
                    del auth_plugin[principal_id[prefix_length:]]
                    count += 1
        if count > 0:
            report.write('--------------------\n')
            report.write('%d profile(s) deleted' % count)
