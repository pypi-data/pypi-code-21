""" Schema extender subtypes
"""
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField
from eea.geotags import field
from eea.geotags import widget

class ExtensionGeotagsSinglefield(ExtensionField, field.GeotagsStringField):
    """ derivative of blobfield for extending schemas """

class GeotagsFieldExtender(object):
    """ Extends base schema with extra fields.
    To be used for base content class. """
    implements(ISchemaExtender)

    fields = [
            ExtensionGeotagsSinglefield(
                name='location',
                schemata='categorization',
                widget=widget.GeotagsWidget(
                    label='Location',
                    description=('Geotags: geographical location '
                                 'related to this content.')
                    )
                )
            ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        return self.fields
