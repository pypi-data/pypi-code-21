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
from fanstatic import Library, Resource, Group

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.appskin import ztfy_appskin, ztfy_appskin_grey_css
from ztfy.skin import ztfy_skin_base


library = Library('ztfy.sendit', 'resources')

ztfy_sendit_bo_css = Resource(library, 'css/ztfy.sendit.back.css',
                              minified='css/ztfy.sendit.back.min.css')

ztfy_sendit_css = Resource(library, 'css/ztfy.sendit.css',
                           minified='css/ztfy.sendit.min.css',
                           depends=[ztfy_appskin_grey_css])

ztfy_sendit_base = Resource(library, 'js/ztfy.sendit.js',
                            minified='js/ztfy.sendit.min.js',
                            depends=[ztfy_skin_base],
                            bottom=True)

ztfy_sendit = Group(depends=[ztfy_sendit_base,
                             ztfy_sendit_css,
                             ztfy_appskin])
