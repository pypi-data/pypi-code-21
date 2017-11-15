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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from ztfy.sendit.skin.app.interfaces import ISenditApplicationPresentationInfo
from ztfy.skin.interfaces import IPresentationTarget

# import Zope3 packages
from zope.component import adapter, adapts
from zope.container.contained import Contained
from zope.interface import implementer, implements
from zope.location import locate

# import local packages
from ztfy.file.property import ImageProperty
from ztfy.i18n.property import I18nTextProperty
from ztfy.jqueryui import jquery_jsonrpc
from ztfy.sendit.app.interfaces import ISenditApplication
from ztfy.sendit.skin.layer import ISenditLayer
from ztfy.sendit.skin.menu import SenditLayerDialogMenuItem
from ztfy.skin.presentation import BasePresentationEditForm

from ztfy.sendit import _


SENDIT_APPLICATION_PRESENTATION_KEY = 'ztfy.sendit.app.presentation'


class SenditApplicationPresentation(Persistent, Contained):
    """Sendit application presentation class"""

    implements(ISenditApplicationPresentationInfo)

    site_icon = ImageProperty(ISenditApplicationPresentationInfo['site_icon'])
    logo = ImageProperty(ISenditApplicationPresentationInfo['logo'])
    footer_text = I18nTextProperty(ISenditApplicationPresentationInfo['footer_text'])


@adapter(ISenditApplication)
@implementer(ISenditApplicationPresentationInfo)
def SenditApplicationPresentationFactory(context):
    annotations = IAnnotations(context)
    presentation = annotations.get(SENDIT_APPLICATION_PRESENTATION_KEY)
    if presentation is None:
        presentation = annotations[SENDIT_APPLICATION_PRESENTATION_KEY] = SenditApplicationPresentation()
        locate(presentation, context, '++presentation++')
    return presentation


class SenditApplicationPresentationTargetAdapter(object):

    adapts(ISenditApplication, ISenditLayer)
    implements(IPresentationTarget)

    target_interface = ISenditApplicationPresentationInfo

    def __init__(self, context, request):
        self.context, self.request = context, request


class SenditApplicationPresentationEditForm(BasePresentationEditForm):
    """Site manager presentation edit form"""

    legend = _("Edit presentation properties")

    parent_interface = ISenditApplication


class SenditApplicationPresentationMenuItem(SenditLayerDialogMenuItem):
    """Site manager presentation menu item"""

    title = _(" :: Presentation model...")

    def render(self):
        result = super(SenditApplicationPresentationMenuItem, self).render()
        if result:
            jquery_jsonrpc.need()
        return result
