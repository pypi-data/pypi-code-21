### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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
from ztfy.sendit.profile.interfaces import IProfilesCleanerTaskInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.jqueryui import jquery_multiselect
from ztfy.scheduler.browser.task import BaseTaskAddForm
from ztfy.sendit.profile.task import ProfilesCleanerTask
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.sendit import _


class ProfilesCleanerTaskAddForm(BaseTaskAddForm):
    """Profiles cleaner task add form"""

    task_factory = ProfilesCleanerTask


class ProfilesCleanerTaskAddFormMenu(DialogMenuItem):
    """Profiles cleaner task add form menu"""

    title = _(" :: Add profiles cleaner...")
    target = ProfilesCleanerTaskAddForm


class ProfilesCleanerTaskEditForm(DialogEditForm):
    """Profiles cleaner task edit form"""

    fields = field.Fields(IProfilesCleanerTaskInfo)
    resources = (jquery_multiselect,)

    def applyChanges(self, data):
        result = super(ProfilesCleanerTaskEditForm, self).applyChanges(data)
        if result:
            self.context.reset()
        return result


class ProfilesCleanerTaskEditFormMenu(DialogMenuItem):
    """Profiles cleaner task edit form menu"""

    title = _(" :: Profiles cleaner properties...")
    target = ProfilesCleanerTaskEditForm
