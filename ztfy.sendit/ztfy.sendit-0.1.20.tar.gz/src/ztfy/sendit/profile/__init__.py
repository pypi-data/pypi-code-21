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
import base64
import hashlib
import hmac
import random
import sys
from datetime import datetime
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.principalannotation.interfaces import IPrincipalAnnotationUtility
from zope.security.interfaces import IPrincipal

# import local interfaces
from ztfy.mail.interfaces import IPrincipalMailInfo
from ztfy.security.interfaces import ISecurityManager
from ztfy.sendit.profile.interfaces import IProfile
from ztfy.sendit.user.interfaces import ISenditApplicationUsers

# import Zope3 packages
from zope.component import adapter, adapts, queryUtility, getUtilitiesFor
from zope.container.contained import Contained
from zope.event import notify
from zope.interface import implementer, implements, Invalid
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location import locate
from zope.schema.fieldproperty import FieldProperty
from zope.security.proxy import removeSecurityProxy

# import local packages
from ztfy.security.property import RolePrincipalsProperty
from ztfy.security.search import getPrincipal
from ztfy.sendit.app.interfaces import ISenditApplication, EMAIL_REGEX
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


class UserProfile(Persistent, Contained):
    """User profile class"""

    implements(IProfile)

    owner = RolePrincipalsProperty(IProfile['owner'], role='ztfy.SenditProfileOwner')

    @property
    def owner_title(self):
        return getPrincipal(self.owner).title

    def getAuthenticatorPlugin(self):
        result = getattr(self, '_v_authenticator', None)
        if result is None:
            result = (None, None, None)
            for name, plugin in getUtilitiesFor(IAuthenticatorPlugin):
                info = plugin.principalInfo(self.owner)
                if info is not None:
                    result = (name, plugin, info)
                    break
            self._v_authenticator = result
        return result

    def isExternal(self):
        name, _plugin, _info = self.getAuthenticatorPlugin()
        if name:
            app = getParent(self, ISenditApplication)
            return name == app.external_auth_plugin

    self_registered = FieldProperty(IProfile['self_registered'])
    activation_secret = FieldProperty(IProfile['activation_secret'])
    activation_hash = FieldProperty(IProfile['activation_hash'])
    activation_date = FieldProperty(IProfile['activation_date'])
    activated = FieldProperty(IProfile['activated'])

    def generateSecretKey(self, login, password):
        seed = self.activation_secret = u'-'.join((str(random.randint(0, sys.maxint)) for i in range(5)))
        secret = hmac.new(password.encode('utf-8'), login, digestmod=hashlib.sha256)
        secret.update(seed)
        self.activation_hash = base64.b32encode(secret.digest()).decode()

    def checkActivation(self, hash, login, password):
        if self.self_registered:
            secret = hmac.new(password.encode('utf-8'), login, digestmod=hashlib.sha256)
            secret.update(self.activation_secret)
            if hash != base64.b32encode(secret.digest()).decode():
                raise Invalid, _("Can't activate profile with given params")
        else:
            # Just check that hash is matching and update user password
            if hash != self.activation_hash:
                raise Invalid, _("Can't activate profile with given params")
            app = getParent(self, ISenditApplication)
            plugin = queryUtility(IAuthenticatorPlugin, app.external_auth_plugin)
            principal = removeSecurityProxy(plugin[login])
            principal.password = password

    filtered_uploads = FieldProperty(IProfile['filtered_uploads'])
    _disabled_upload = FieldProperty(IProfile['disabled_upload'])
    _disabled_upload_date = FieldProperty(IProfile['disabled_upload_date'])

    @property
    def disabled_upload(self):
        return self._disabled_upload

    @disabled_upload.setter
    def disabled_upload(self, value):
        app = getParent(self, ISenditApplication)
        if value:
            if not self._disabled_upload:
                self._disabled_upload_date = datetime.utcnow()
            ISecurityManager(app).denyPermission('ztfy.UploadSenditPacket', self.owner)
        else:
            self._disabled_upload_date = None
            ISecurityManager(app).unsetPermission('ztfy.UploadSenditPacket', self.owner)
        self._disabled_upload = value

    _disabled = FieldProperty(IProfile['disabled'])
    _disabled_date = FieldProperty(IProfile['disabled_date'])

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        app = getParent(self, ISenditApplication)
        if value:
            if not self._disabled:
                self._disabled_date = datetime.utcnow()
            self.disabled_upload = value
            ISecurityManager(app).denyPermission('ztfy.ViewSenditApplication', self.owner)
        else:
            self._disabled_date = None
            ISecurityManager(app).unsetPermission('ztfy.ViewSenditApplication', self.owner)
        self._disabled = value

    quota_size = FieldProperty(IProfile['quota_size'])
    max_documents = FieldProperty(IProfile['max_documents'])
    quota_usage = FieldProperty(IProfile['quota_usage'])

    quota_size_str = FieldProperty(IProfile['quota_size_str'])
    max_documents_str = FieldProperty(IProfile['max_documents_str'])

    def getQuotaSize(self, context):
        result = self.quota_size
        if result is None:
            app = getParent(context, ISenditApplication)
            result = app.default_quota_size
        return result

    def getQuotaUsage(self, context):
        app = getParent(context, ISenditApplication)
        folder = ISenditApplicationUsers(app).getUserFolder(self.owner)
        if folder is not None:
            return folder.getQuotaUsage()
        else:
            return 0

    def getQuotaUsagePc(self, context):
        quota = self.getQuotaSize(context)
        if quota == 0:
            return 0
        usage = self.getQuotaUsage(context)
        return int(round(1. * usage / (quota * 1024 * 1024) * 100))

    def getMaxDocuments(self, context):
        result = self.max_documents
        if result is None:
            app = getParent(context, ISenditApplication)
            result = app.default_max_documents
        return result


#
# Profile adapters
#

SENDIT_USER_PROFILE = 'ztfy.sendit.profile'

@adapter(IPrincipal)
@implementer(IProfile)
def UserProfileFactory(principal):
    if principal.id == 'zope.anybody':
        return None
    utility = queryUtility(IPrincipalAnnotationUtility)
    if utility is not None:
        annotations = IAnnotations(utility.getAnnotationsById(principal.id))
        profile = annotations.get(SENDIT_USER_PROFILE)
        if profile is None:
            profile = annotations[SENDIT_USER_PROFILE] = UserProfile()
            profile.owner = principal.id
            notify(ObjectCreatedEvent(profile))
            locate(profile, utility)
        return profile


def getUserProfile(principal, create=True):
    if IPrincipal.providedBy(principal):
        principal = principal.id
    principal = principal.lower()
    if principal == 'zope.anybody':
        return None
    utility = queryUtility(IPrincipalAnnotationUtility)
    if utility is not None:
        annotations = IAnnotations(utility.getAnnotationsById(principal))
        profile = annotations.get(SENDIT_USER_PROFILE)
        if (profile is None) and create:
            profile = annotations[SENDIT_USER_PROFILE] = UserProfile()
            profile.owner = principal
            notify(ObjectCreatedEvent(profile))
            locate(profile, utility)
        return profile


#
# Profile mail adapter
#

class UserProfileMailInfoAdapter(object):
    """User profile mail info adapter"""

    adapts(IProfile)
    implements(IPrincipalMailInfo)

    def __new__(cls, context):
        _name, _plugin, info = context.getAuthenticatorPlugin()
        if (not info) or (not EMAIL_REGEX.match(info.login)):
            return None
        return object.__new__(cls)

    def __init__(self, context):
        self.context = context

    def getAddresses(self):
        _name, _plugin, info = self.context.getAuthenticatorPlugin()
        return ((info.title, info.login), )
