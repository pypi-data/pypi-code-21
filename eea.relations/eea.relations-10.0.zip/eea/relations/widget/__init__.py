""" Widget
"""
from Products.Archetypes.atapi import registerType
from Products.Archetypes.Registry import registerWidget
from eea.relations.config import PROJECTNAME
from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget
from eea.relations.widget.referencedemo import EEARefBrowserDemo

def register():
    """ Register custom widgets and content-types
    """
    registerWidget(EEAReferenceBrowserWidget,
        title='EEA Reference Browser',
        description=(('Reference widget that allows you to browse '
                      'or search the portal for objects to refer to.')),
        used_for=('Products.Archetypes.Field.ReferenceField',))

    registerType(EEARefBrowserDemo, PROJECTNAME)
