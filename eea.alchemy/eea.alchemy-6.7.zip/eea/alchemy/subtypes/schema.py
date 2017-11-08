""" Schema extender for Disable Autolinks for context/page
"""
from zope.interface import implements
from Products.Archetypes.public import BooleanField, BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField


class EEAAlchemyBooleanField(ExtensionField, BooleanField):
    """ BooleanField for schema extender
    """

class EEAAlchemySchemaExtender(object):
    """ Schema extender for disable auto-links field
    """
    implements(ISchemaExtender)
    fields = (
        EEAAlchemyBooleanField(
            name='forcedisableautolinks',
            schemata='settings',
            default=False,
            searchable=False,
            widget=BooleanWidget(
                label='Force Disable Autolinks',
                description='Disable Autolinks for this context/page',
            )
        ),

    )


    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Returns provenance list field
        """
        return self.fields
