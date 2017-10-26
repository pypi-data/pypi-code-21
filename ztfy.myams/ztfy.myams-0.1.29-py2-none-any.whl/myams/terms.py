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
from z3c.form.interfaces import IWidget, IBoolTerms
from zope.schema.interfaces import IBool

# import local interfaces
from ztfy.myams.layer import MyAMSLayer

# import Zope3 packages
from z3c.form.term import BoolTerms as BaseBoolTerms
from zope.component import adapts
from zope.interface import implementsOnly, Interface

# import local packages

from ztfy.skin import _


class BoolTerms(BaseBoolTerms):
    """Default yes and no terms are used by default for IBool fields."""

    adapts(Interface, MyAMSLayer, Interface, IBool, IWidget)
    implementsOnly(IBoolTerms)

    trueLabel = _('yes')
    falseLabel = _('no')
