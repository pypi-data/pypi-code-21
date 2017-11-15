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
from zope.schema.interfaces import IVocabularyFactory

# import local interfaces
from ztfy.sendit.app.interfaces.filter import IFilteringPlugin

# import Zope3 packages
from zope.componentvocabulary.vocabulary import UtilityVocabulary
from zope.interface import classProvides

# import local packages


class FiltersVocabulary(UtilityVocabulary):
    """Packets filters vocabulary"""

    classProvides(IVocabularyFactory)

    interface = IFilteringPlugin
    nameOnly = True
