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

# import Zope3 packages
from zope.interface import implements
from zope.schema import Object, List

# import local packages
from ztfy.sendit.packet.interfaces import IDocumentField, IDocumentsListField, IDocumentInfo


class DocumentField(Object):
    """Document field"""

    implements(IDocumentField)

    def __init__(self, schema=None, **kw):
        super(DocumentField, self).__init__(schema=IDocumentInfo, **kw)


class DocumentsListField(List):
    """Media documents schema field"""

    implements(IDocumentsListField)

    def __init__(self, value_type=None, unique=False, **kw):
        super(DocumentsListField, self).__init__(value_type=DocumentField(), **kw)
