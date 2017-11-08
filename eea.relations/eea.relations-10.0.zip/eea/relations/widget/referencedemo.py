""" Demonstrates the use of EEAReferenceBrowserWidget """

from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from eea.relations.field.referencefield import EEAReferenceField
from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget

SCHEMA = ATFolder.schema.copy() + atapi.Schema((
    EEAReferenceField('relatedItems',
        schemata='default',
        relationship='relatesTo',
        multiValued=True,
        widget=EEAReferenceBrowserWidget(
            label='Related items',
            description='Relations.'
        )
    ),
))

class EEARefBrowserDemo(ATFolder):
    """ Demo from EEAReferenceBrowserWidget
    """
    archetypes_name = meta_type = portal_type = 'EEARefBrowserDemo'
    _at_rename_after_creation = True
    schema = SCHEMA
