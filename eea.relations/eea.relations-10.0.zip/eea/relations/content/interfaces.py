""" Content interfaces
"""
from zope.interface import Interface
from Products.Archetypes.interfaces import IBaseObject as IATBaseObject

class IContentType(Interface):
    """ Content type
    """

class IRelation(Interface):
    """ Relation between 2 content types
    """

class IRelationsTool(Interface):
    """ portal_relations tool
    """

class IToolAccessor(Interface):
    """ portal_relations tool accessor
    """
    def relations(proxy):
        """
        Returns defined possible relation.

        If proxy=True returns catalog brains
        """

    def types(proxy):
        """ Returns defined content types. If proxy=True returns catalog brains
        """

class IBaseObject(IATBaseObject):
    """ Interface to be used for generic relations as Archetypes.IBaseObject
    is blacklisted in Products.CMFPlone.CatalogTool.BLACKLISTED_INTERFACES

    More details about this issue on:
    https://svn.eionet.europa.eu/projects/Zope/ticket/4908
    """
