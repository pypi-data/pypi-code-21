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
from ztfy.sendit.app.interfaces.filter import IFilteringPlugin

# import Zope3 packages
from zope.interface import Interface
from zope.schema import TextLine, List, Choice

# import local packages

from ztfy.sendit import _


class IMimetypeFilterPluginInfo(Interface):
    """MIME types filter plug-in configuration info"""

    forbidden_extensions = TextLine(title=_("Forbidden extensions"),
                                    description=_("Any packet containing a document with a given extension will be excluded.\n"
                                                  "Please enter forbidden files extensions, including leading dot (like '.doc'), separated with spaces or commas"),
                                    required=False)

    forbidden_mimetypes = List(title=_("Forbidden MIME types"),
                               description=_("Any packet containing a document of a selected MIME type will be excluded"),
                               value_type=Choice(vocabulary="ZTFY MIME types"),
                               required=False)

    forbidden_magic_types = List(title=_("Forbidden Magic types"),
                                 description=_("Magic library provides some custom MIME types, you can select which will be excluded"),
                                 value_type=Choice(vocabulary="ZTFY magic types"),
                                 required=False)


class IMimetypeFilterPlugin(IFilteringPlugin):
    """A filtering plug-in handling MIME types"""


class IMimetypeFilterTarget(Interface):
    """Marker interface for MIME types filtering"""
