""" Faceted Tool
"""
from zope.component import queryMultiAdapter
from zope.interface import implements
from OFS.Folder import Folder
from Products.CMFCore.utils import getToolByName
from BTrees.IIBTree import IIBucket

from eea.faceted.tool.interfaces import IFacetedTool
from eea.faceted.tool.interfaces import IFacetedCatalog

class FacetedTool(Folder):
    """ A local utility storing all faceted navigation global settings """
    implements(IFacetedTool)

    id = 'portal_faceted'
    title = 'Manages faceted navigation global settings'
    meta_type = 'EEA Faceted Tool'

    def apply_index(self, index, value):
        """ Custom catalog apply_index method
        """
        ctool = getToolByName(self, 'portal_catalog')
        catalog = queryMultiAdapter((self, ctool), IFacetedCatalog)
        if not catalog:
            return IIBucket(), (index.getId(),)
        return catalog.apply_index(index, value)

    def search(self, **query):
        """
        Use this method to search over catalog using defined
        faceted portal types.
        """
        ctool = getToolByName(self, 'portal_catalog')
        catalog = queryMultiAdapter((self, ctool), IFacetedCatalog)
        if not catalog:
            return ctool(**query)
        return catalog(**query)
