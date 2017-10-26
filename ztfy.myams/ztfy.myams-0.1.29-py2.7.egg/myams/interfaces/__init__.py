#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces
from z3c.form.interfaces import IInputForm
from ztfy.baseskin.interfaces import ISkinnable
from ztfy.baseskin.interfaces.form import checkSubmitButton

# import local interfaces

# import Zope3 packages
from z3c.form import button
from zope.interface import Interface, Attribute
from zope.schema import TextLine, Dict

# import local packages
from ztfy.baseskin.schema import CloseButton, ResetButton

from ztfy.myams import _


class IMyAMSApplication(ISkinnable):
    """MyAMS application interface"""

    configuration_name = TextLine(title=_("Application static configuration name"),
                                  required=True)

    resources = Attribute(_("Fanstatic static resources"))


class IObjectData(Interface):
    """Object custom data interface"""

    object_data = Dict(title=_("Data associated with this object"),
                       required=False)


class IFullPage(Interface):
    """Full page marker interface"""


class IModalFullPage(IFullPage):
    """Full page modal dialog marker interface"""

    dialog_class = Attribute(_("Default dialog CSS class"))


class IInnerPage(Interface):
    """Inner page marker interface"""


class IModalPage(Interface):
    """Modal page marker interface"""


class IAddFormButtons(Interface):
    """Default add form buttons"""

    reset = ResetButton(name='reset', title=_("Reset"))
    add = button.Button(name='add', title=_("Add"), condition=checkSubmitButton)


class IModalAddFormButtons(Interface):
    """Modal add form buttons"""

    close = CloseButton(name='close', title=_("Close"))
    add = button.Button(name='add', title=_("Add"), condition=checkSubmitButton)


class IEditFormButtons(Interface):
    """Default edit form buttons"""

    reset = ResetButton(name='reset', title=_("Reset"))
    submit = button.Button(name='submit', title=_("Submit"), condition=checkSubmitButton)


class IModalEditFormButtons(Interface):
    """Modal edit form buttons"""

    close = CloseButton(name='close', title=_("Close"))
    submit = button.Button(name='submit', title=_("Submit"), condition=checkSubmitButton)


class IModalDisplayFormButtons(Interface):
    """Modal display form buttons"""

    close = CloseButton(name='close', title=_("Close"))


class IInnerForm(IInputForm):
    """Inner form marker interface"""
