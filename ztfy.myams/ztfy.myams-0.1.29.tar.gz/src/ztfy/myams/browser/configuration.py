#
# Copyright (c) 2012 Thierry Florac <tflorac AT onf.fr>
# All Rights Reserved.
#


# import standard packages

# import Zope3 interfaces

# import local interfaces
from ztfy.myams.interfaces.configuration import IMyAMSConfiguration
from ztfy.skin.interfaces import IPropertiesMenuTarget

# import Zope3 packages
from z3c.form import field
from zope.interface import implements
from zope.traversing.namespace import view

# import local packages
from ztfy.skin.form import EditForm
from ztfy.skin.menu import MenuItem

from ztfy.myams import _


class MyAMSConfigurationNamespaceTraverser(view):
    """++configuration++ namespace"""

    def traverse(self, name, ignored):
        return IMyAMSConfiguration(self.context)


class MyAMSConfigurationEditForm(EditForm):
    """MyAMS main configuration edit form"""

    implements(IPropertiesMenuTarget)

    legend = _("Application properties")
    fields = field.Fields(IMyAMSConfiguration)

    def getContent(self):
        return IMyAMSConfiguration(self.context)


class MyAMSConfigurationMenuItem(MenuItem):
    """MyAMS configuration menu item"""

    title = _("Properties")
