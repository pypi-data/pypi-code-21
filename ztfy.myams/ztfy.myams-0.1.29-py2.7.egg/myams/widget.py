#
# Copyright (c) 2008-2015 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__docformat__ = 'restructuredtext'


# import standard library

# import interfaces
from z3c.form.interfaces import IFieldWidget
from ztfy.myams.interfaces.widget import ISelect2Widget
from zope.schema.interfaces import IChoice

# import packages
from z3c.form.browser.select import SelectWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.i18n import translate
from zope.interface import implementer, implementer_only
from ztfy.myams.layer import MyAMSLayer

from ztfy.myams import _


@implementer_only(ISelect2Widget)
class Select2Widget(SelectWidget):
    """Select2 widget"""

    noValueMessage = _("(no selected value)")

    def get_content(self, entry):
        return translate(entry['content'], context=self.request)


@adapter(IChoice, MyAMSLayer)
@implementer(IFieldWidget)
def ChoiceFieldWidget(field, request):
    return FieldWidget(field, Select2Widget(request))
