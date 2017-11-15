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
from z3c.form.interfaces import HIDDEN_MODE

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplicationSecurityInfo
from ztfy.sendit.profile.interfaces import IProfile

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.jqueryui import jquery_multiselect
from ztfy.sendit.profile import getUserProfile
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import MenuItem
from ztfy.skin.page import TemplateBasedPage, BaseBackView
from ztfy.sendit.skin import ztfy_sendit_base

from ztfy.sendit import _


class ProfileSearchView(BaseBackView, TemplateBasedPage):
    """Profile search view"""

    def update(self):
        BaseBackView.update(self)
        jquery_multiselect.need()
        ztfy_sendit_base.need()

    @property
    def auth_plugins(self):
        return ','.join((str(plugin) for plugin in ISenditApplicationSecurityInfo(self.context).single_auth_plugins))


class ProfileSearchMenuItem(MenuItem):
    """Profile search menu item"""

    title = _("User profiles")


class ProfileEditForm(DialogEditForm):
    """Profile edit form"""

    legend = _("Edit profile properties")
    fields = field.Fields(IProfile).select('owner', 'owner_title', 'quota_size', 'max_documents',
                                           'filtered_uploads', 'disabled_upload', 'disabled')

    def getContent(self):
        principal_id = self.request.form.get(self.prefix + 'widgets.owner')
        if not principal_id:
            principal_id = self.request.form.get('uid')
        return getUserProfile(principal_id, create=True)

    def updateWidgets(self):
        super(ProfileEditForm, self).updateWidgets()
        self.widgets['owner'].mode = HIDDEN_MODE

    def updateContent(self, content, data):
        content = getUserProfile(data.get('owner'))
        return super(ProfileEditForm, self).updateContent(content, data)
