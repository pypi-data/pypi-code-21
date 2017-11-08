""" eea.faceted.tool public interface
"""
from zope import schema
from zope.interface import Interface

# Storage
class IPortalType(Interface):
    """ Custom portal type
    """
    title = schema.TextLine(
        title=u'Title',
        description=u'Friendly name',
        required=True
    )

    search_interface = schema.Choice(
        title=u'Provided interface',
        description=u'Interface to search for',
        vocabulary="eea.faceted.vocabularies.ObjectProvides",
        required=False
    )

    search_type = schema.Choice(
        title=u'Portal type',
        description=u'Portal type to search for',
        vocabulary="eea.faceted.vocabularies.PortalTypes",
        required=False
    )

# Catalog
class IFacetedCatalog(Interface):
    """ Custom faceted catalog
    """

class IFacetedTool(Interface):
    """ Faceted Tool
    """
