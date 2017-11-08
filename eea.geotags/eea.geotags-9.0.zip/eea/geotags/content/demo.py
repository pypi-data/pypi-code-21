""" Demonstrates the use of EEA Geotags widget
"""
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from eea.geotags import field
from eea.geotags import widget

SIMPLE_SCHEMA = ATFolder.schema.copy() + atapi.Schema((
    field.GeotagsStringField('location',
        schemata='geographical coverage',
        widget=widget.GeotagsWidget(
            label='Location',
            description='Single geographical location'
        )
    ),
))

SCHEMA = ATFolder.schema.copy() + atapi.Schema((
    field.GeotagsLinesField('location',
        schemata='geographical coverage',
        widget=widget.GeotagsWidget(
            label='Location',
            description="Multiple geo tags"
        )
    ),
))

class EEAGeotagsSimpleDemo(ATFolder):
    """ Demo from EEA Geotags Widget
    """
    archetypes_name = meta_type = portal_type = 'EEATagsSimpleDemo'
    _at_rename_after_creation = True
    schema = SIMPLE_SCHEMA

class EEAGeotagsDemo(ATFolder):
    """ Demo from EEA Geotags Widget
    """
    archetypes_name = meta_type = portal_type = 'EEATagsDemo'
    _at_rename_after_creation = True
    schema = SCHEMA
