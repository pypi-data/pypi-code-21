""" Schema extender for Disable Autolinks for context/page
"""
from zope.interface import implements
from Products.Archetypes.public import BooleanField, BooleanWidget
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField
from eea.annotator.config import EEAMessageFactory as _
from eea.annotator.interfaces import ILayer
from eea.annotator.controlpanel.interfaces import ISettings


class EEABooleanField(ExtensionField, BooleanField):
    """ BooleanField for schema extender
    """


class EEASchemaExtender(object):
    """ Schema extender for inline comment fields
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = ILayer

    fields = (
        EEABooleanField(
            name='disableAnnotator',
            schemata='settings',
            default=False,
            searchable=False,
            widget=BooleanWidget(
                label=_('Disable inline comments'),
                description=_("Do not allow editors to add inline comments on "
                              "this context/page"),
            )
        ),
        EEABooleanField(
            name='readOnlyAnnotator',
            schemata='settings',
            default=False,
            searchable=False,
            widget=BooleanWidget(
                label=_('Read-only inline comments'),
                description=_("Make inline comments read-only"),
            )
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Returns provenance list field
        """
        settings = ISettings(self.context)
        if not settings.disabled:
            return self.fields
        return ()
