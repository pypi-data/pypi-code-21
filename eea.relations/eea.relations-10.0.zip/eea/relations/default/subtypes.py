""" Overrides default keywords widget
"""
from zope.interface import implements
from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from eea.relations.browser.interfaces import IEEARelationsLayer
from eea.relations.widget.referencewidget import EEAReferenceBrowserWidget
from Products.ATContentTypes import ATCTMessageFactory as _

widget = EEAReferenceBrowserWidget(
    label=_(u'Related Items'),
    description='',
    visible={'edit' : 'visible', 'view' : 'invisible'},
    i18n_domain="plone"
)

class SchemaModifier(object):
    """ EEA Relations widget
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEARelationsLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Modify schema
        """
        if 'relatedItems' in schema:
            xfield = schema['relatedItems']
            xfield.widget = widget
