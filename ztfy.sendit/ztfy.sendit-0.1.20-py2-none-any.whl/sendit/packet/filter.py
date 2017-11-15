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
import mimetypes
import re
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations
from zope.app.file.interfaces import IFile

# import local interfaces
from ztfy.file.interfaces import IArchiveExtractor
from ztfy.sendit.app.interfaces.filter import FilteredPacketException
from ztfy.sendit.packet.interfaces.filter import IMimetypeFilterPluginInfo, IMimetypeFilterPlugin, IMimetypeFilterTarget

# import Zope3 packages
from zope.component import adapter, queryUtility
from zope.container.contained import Contained
from zope.event import notify
from zope.i18n import translate
from zope.interface import implementer, implements
from zope.lifecycleevent import ObjectCreatedEvent
from zope.location.location import locate
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.extfile import getMagicContentType
from ztfy.utils.list import unique
from ztfy.utils.request import queryRequest
from ztfy.utils.traversing import getParent

from ztfy.sendit import _


EXT_REG = re.compile('[,\s]')


class MimetypeFilterPlugin(object):
    """MIME types filter"""

    implements(IMimetypeFilterPlugin)

    marker_interface = IMimetypeFilterTarget
    config_interface = IMimetypeFilterPluginInfo

    def filter(self, packet):
        target = getParent(packet, self.marker_interface)
        if target is None:
            return
        info = self.config_interface(target, None)
        if info is None:
            return
        for document in packet.values():
            self.filterElement(info, document.filename, document.data)

    def filterElement(self, config, filename, data):
        if IFile.providedBy(data):
            data = data.data
        # check extensions
        extensions = EXT_REG.split(config.forbidden_extensions or '')
        if extensions:
            if '.' in filename:
                _name, ext = filename.rsplit('.', 1)
            else:
                _name, ext = filename, ''
            if '.' + ext in extensions:
                raise FilteredPacketException(translate(_("A document containing invalid data (%s) has been uploaded. "
                                                          "Your packet has been rejected."), context=queryRequest())
                                              % filename)
        # check MIME types
        magic_type = getMagicContentType(data)
        if magic_type in (config.forbidden_magic_types or ()):
            raise FilteredPacketException(translate(_("A document containing invalid data (%s) has been uploaded. "
                                                      "Your packet has been rejected."), context=queryRequest()) %
                                          filename)
        mime_type, _encoding = mimetypes.guess_type(filename)
        for name in unique((mime_type, magic_type)):
            if name:
                extractor = queryUtility(IArchiveExtractor, name=name)
                if extractor is not None:
                    extractor.initialize(data)
                    for content, filename in extractor.getContents():
                        self.filterElement(config, filename, content)
                else:
                    extension = mimetypes.guess_extension(name)
                    if extension:
                        mime_types = config.forbidden_mimetypes or ()
                        if extension in mime_types:
                            raise FilteredPacketException(translate(_("A document containing invalid data (%s) has "
                                                                      "been uploaded. Your packet has been rejected."),
                                                                    context=queryRequest()) % filename)


class MimetypeFilterPluginInfo(Persistent, Contained):
    """MIME types packet filter configuration info"""

    implements(IMimetypeFilterPluginInfo)

    forbidden_extensions = FieldProperty(IMimetypeFilterPluginInfo['forbidden_extensions'])
    forbidden_mimetypes = FieldProperty(IMimetypeFilterPluginInfo['forbidden_mimetypes'])
    forbidden_magic_types = FieldProperty(IMimetypeFilterPluginInfo['forbidden_magic_types'])


MIMETYPE_FILTER_INFO_KEY = 'ztfy.sendit.filter.mimetype'

@adapter(IMimetypeFilterTarget)
@implementer(IMimetypeFilterPluginInfo)
def MimetypeFilterPluginInfoFactory(context):
    """SendIt application MIME types filter adapter"""
    annotations = IAnnotations(context)
    info = annotations.get(MIMETYPE_FILTER_INFO_KEY)
    if info is None:
        info = annotations[MIMETYPE_FILTER_INFO_KEY] = MimetypeFilterPluginInfo()
        notify(ObjectCreatedEvent(info))
        locate(info, context)
    return info
