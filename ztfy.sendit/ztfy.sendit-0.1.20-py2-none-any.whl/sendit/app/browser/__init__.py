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

# import local interfaces
from ztfy.sendit.app.interfaces import ISenditApplicationInfo, ISenditApplicationSecurityInfo, \
                                       ISenditApplicationBackInfo, ISenditApplicationMailingInfo, \
                                       ISenditApplicationQuotaInfo, ISenditApplicationFiltersInfo
from ztfy.skin.interfaces import IPropertiesMenuTarget

# import Zope3 packages
from z3c.form import field
from zope.interface import implements
from zope.traversing import namespace

# import local packages
from ztfy.jqueryui import jquery_multiselect, jquery_tinymce
from ztfy.skin.form import EditForm, DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.sendit import _
from ztfy.sendit.skin import ztfy_sendit_bo_css


class SenditApplicationPropertiesEditForm(EditForm):
    """Sendit application properties edit form"""

    implements(IPropertiesMenuTarget)

    legend = _("Sendit application properties")
    fields = field.Fields(ISenditApplicationInfo)

    def updateWidgets(self):
        super(SenditApplicationPropertiesEditForm, self).updateWidgets()
        self.widgets['heading'].cols = 80
        self.widgets['heading'].rows = 10
        self.widgets['description'].cols = 80
        self.widgets['description'].rows = 3


#
# Back-office properties menus and forms
#

class SenditApplicationBackInfoEditForm(DialogEditForm):
    """Sendit application back-office infos edit form"""

    legend = _("Edit back-office presentation properties")
    fields = field.Fields(ISenditApplicationBackInfo)

    def getContent(self):
        return ISenditApplicationBackInfo(self.context)


class SenditApplicationBackInfoMenuItem(DialogMenuItem):
    """Sendit application back-office infos menu item"""

    title = _(":: Back-office...")
    target = SenditApplicationBackInfoEditForm


class SenditApplicationBackInfoNamespace(namespace.view):
    """++back++ application namespace traverser"""

    def traverse(self, name, ignored):
        return ISenditApplicationBackInfo(self.context)


#
# Sendit application security settings
#

class SenditApplicationSecurityEditForm(DialogEditForm):
    """Sendit application security settings edit form"""

    legend = _("Update security settings")
    fields = field.Fields(ISenditApplicationSecurityInfo).omit('filtering_plugins')
    resources = (jquery_multiselect,)


class SenditApplicationSecurityMenuItem(DialogMenuItem):
    """Sendit application security menu item"""

    title = _(":: Security...")
    target = SenditApplicationSecurityEditForm


#
# Sendit application mailing settings
#

class SenditApplicationMailingEditForm(DialogEditForm):
    """Sendit application mailing settings edit form"""

    legend = _("Update mailing settings")
    fields = field.Fields(ISenditApplicationMailingInfo)

    resources = (jquery_tinymce,)


class SenditApplicationMailingMenuItem(DialogMenuItem):
    """Sendit application mailing settings menu item"""

    title = _(":: Mailing settings...")
    target = SenditApplicationMailingEditForm


#
# Sendit application quota settings
#

class SenditApplicationQuotaEditForm(DialogEditForm):
    """Sendit application default quota edit form"""

    legend = _("Update default user quota")
    fields = field.Fields(ISenditApplicationQuotaInfo)


class SenditApplicationQuotaMenuItem(DialogMenuItem):
    """Sendit application default quota menu item"""

    title = _(":: User quota...")
    target = SenditApplicationQuotaEditForm


#
# Sendit application filters settings
#

class SenditApplicationFiltersEditForm(DialogEditForm):
    """Sendit application filters edit form"""

    legend = _("Update application filters")
    fields = field.Fields(ISenditApplicationFiltersInfo)
    cssClass = "form edit filters"
    resources = (jquery_multiselect, ztfy_sendit_bo_css)


class SenditApplicationFiltersMenuItem(DialogMenuItem):
    """Sendit application filters menu item"""

    title = _(":: Recipients filters...")
    target = SenditApplicationFiltersEditForm


#
# Sendit application plug-ins settings
#

class SenditApplicationPluginsEditForm(DialogEditForm):
    """Sendit application plug-ins settings edit form"""

    legend = _("Select packets filters")
    fields = field.Fields(ISenditApplicationSecurityInfo).select('filtering_plugins')

    def getOutput(self, writer, parent, changes=()):
        if changes:
            return writer.write({ 'output': 'RELOAD' })
        else:
            return super(SenditApplicationPluginsEditForm, self).getOutput(writer, parent, changes)


class SenditApplicationPluginsMenuItem(DialogMenuItem):
    """Sendit application packets filters menu item"""

    title = _(":: Filtering plug-ins...")
    target = SenditApplicationPluginsEditForm
