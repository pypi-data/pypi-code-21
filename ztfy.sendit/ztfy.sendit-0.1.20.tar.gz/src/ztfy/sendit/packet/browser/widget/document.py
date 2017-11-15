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
from z3c.form.interfaces import IObjectWidget, IFieldWidget, IMultiWidget

# import local interfaces

# import Zope3 packages
from z3c.form.object import ObjectConverter
from zope.component import adapter, adapts
from zope.interface import implementer, implements
from ztfy.sendit.packet.interfaces import IDocumentField, IDocumentsListField
from z3c.form.browser.object import ObjectWidget
from ztfy.skin.layer import IZTFYBrowserLayer
from z3c.form.widget import FieldWidget
from z3c.form.browser.multi import MultiWidget

# import local packages


#
# Document field converter and widget
#

class IDocumentFieldWidget(IObjectWidget):
    """Document widget interface"""


class DocumentFieldConverter(ObjectConverter):
    """Media document converter"""

    adapts(IDocumentField, IDocumentFieldWidget)

    def toWidgetValue(self, value):
        result = super(DocumentFieldConverter, self).toWidgetValue(value)
        result['__data__'] = value
        return result


class DocumentFieldWidget(ObjectWidget):
    """Document widget"""

    implements(IDocumentFieldWidget)


@adapter(IDocumentField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def DocumentFieldWidgetFactory(field, request):
    return FieldWidget(field, DocumentFieldWidget(request))


#
# Documents list widget
#

class IDocumentsListWidget(IMultiWidget):
    """Documents list widget interface"""


class DocumentsListWidget(MultiWidget):
    """Documents list widget"""

    implements(IDocumentsListWidget)


@adapter(IDocumentsListField, IZTFYBrowserLayer)
@implementer(IFieldWidget)
def DocumentsListWidgetFactory(field, request):
    return FieldWidget(field, DocumentsListWidget(request))
