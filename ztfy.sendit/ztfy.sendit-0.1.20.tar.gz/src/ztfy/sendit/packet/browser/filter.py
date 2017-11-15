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
from ztfy.sendit.packet.interfaces.filter import IMimetypeFilterPluginInfo

# import Zope3 packages
from z3c.form import field

# import local packages
from ztfy.skin.form import DialogEditForm
from ztfy.skin.menu import DialogMenuItem

from ztfy.sendit import _


class MimetypeFilterEditForm(DialogEditForm):
    """MIME types filter settings edit form"""

    legend = _("Edit MIME types filter")
    help = _("Packets contents files are scanned for specific extensions, MIME types and through Magic library (which sometimes use different MIME types names).\n"
             "Several archives formats (ZIP, tar.gz...) are also scanned recursively for these bad contents.")

    fields = field.Fields(IMimetypeFilterPluginInfo)


class MimetypeFilterMenuItem(DialogMenuItem):
    """MIME types filter settings menu"""

    title = _(":: MIME types filter...")
    target = MimetypeFilterEditForm
