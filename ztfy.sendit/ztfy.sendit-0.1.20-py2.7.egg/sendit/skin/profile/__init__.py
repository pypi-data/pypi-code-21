### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2013 Thierry Florac <tflorac AT ulthar.net>
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
from datetime import datetime

# import Zope3 interfaces
from z3c.form.interfaces import DISPLAY_MODE
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.security.interfaces import Unauthorized

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.profile.interfaces import IProfileQuotaInfo, IProfileActivationInfo, IProfileActivationAdminInfo, \
                                           IProfile
from ztfy.sendit.skin.app.registration import IUserBaseRegistrationInfo

# import Zope3 packages
from z3c.form import field
from zope.component import getUtility
from zope.i18n import translate

# import local packages
from ztfy.sendit.skin.page import BaseSenditProtectedPage
from ztfy.skin.form import BaseDialogDisplayForm, BaseDialogEditForm
from ztfy.utils.date import formatDatetime
from ztfy.utils.size import getHumanSize
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


class SenditApplicationProfileView(BaseSenditProtectedPage, BaseDialogDisplayForm):
    """Sendit application profile view"""

    legend = _("Profile view")
    icon_class = 'icon-cog'

    fields = field.Fields(IProfileActivationInfo).select('activation_date') + \
             field.Fields(IProfileQuotaInfo).select('quota_size_str', 'quota_usage', 'max_documents_str') + \
             field.Fields(IProfileActivationAdminInfo).omit('disabled_date')

    def __call__(self):
        try:
            BaseSenditProtectedPage.__call__(self)
        except Unauthorized:
            return u''
        else:
            return BaseDialogDisplayForm.__call__(self)

    def update(self):
        self.profile = IProfile(self.request.principal)
        super(SenditApplicationProfileView, self).update()

    def getContent(self):
        return self.profile

    def updateWidgets(self):
        super(SenditApplicationProfileView, self).updateWidgets()
        self.widgets['activation_date'].mode = DISPLAY_MODE
        self.widgets['activation_date'].value = formatDatetime(self.profile.activation_date or datetime.utcnow())
        quota_size = self.profile.getQuotaSize(self.context)
        if quota_size == 0:
            self.widgets['quota_size_str'].value = translate(_("None"), context=self.request)
        else:
            self.widgets['quota_size_str'].value = getHumanSize(quota_size * 1024 * 1024, self.request)
        self.widgets['quota_usage'].value = getHumanSize(self.profile.getQuotaUsage(self.context), self.request)
        max_documents = self.profile.getMaxDocuments(self.context)
        if max_documents == 0:
            self.widgets['max_documents_str'].value = translate(_("None"), context=self.request)
        else:
            self.widgets['max_documents_str'].value = max_documents

    def updateActions(self):
        super(SenditApplicationProfileView, self).updateActions()
        self.actions['dialog_close'].addClass('btn')


class SenditApplicationSettingsView(BaseSenditProtectedPage, BaseDialogEditForm):
    """Sendit application settings view"""

    legend = _("User settings")
    icon_class = 'icon-user'

    fields = field.Fields(IUserBaseRegistrationInfo)

    def __call__(self):
        try:
            BaseSenditProtectedPage.__call__(self)
        except Unauthorized:
            return u''
        else:
            return BaseDialogEditForm.__call__(self)

    def updateActions(self):
        super(SenditApplicationSettingsView, self).updateActions()
        self.actions['dialog_submit'].addClass('btn btn-inverse')
        self.actions['dialog_cancel'].addClass('btn')

    def getContent(self):
        app = getParent(self.context, ISenditApplication)
        plugin = getUtility(IAuthenticatorPlugin, app.external_auth_plugin)
        return plugin.principalInfo(self.request.principal.id)

    def updateContent(self, content, data):
        app = getParent(self.context, ISenditApplication)
        plugin = getUtility(IAuthenticatorPlugin, app.external_auth_plugin)
        prefix = plugin.prefix
        user = plugin[self.request.principal.id[len(prefix):]]
        user.title = '%s %s' % (data.get('lastname'), data.get('firstname'))
        user.description = data.get('company_name') or u''
        if data.get('password'):
            user.password = data.get('password')
        return {IUserBaseRegistrationInfo: ['lastname', 'firstname', 'company_name', 'password']}
