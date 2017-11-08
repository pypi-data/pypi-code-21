""" Faceted Inheritance XML Adapters
"""
from Products.GenericSetup.utils import XMLAdapterBase
from eea.faceted.inheritance.interfaces import IFacetedHeritor

class FacetedHeritorXMLAdapter(XMLAdapterBase):
    """ GenericSetup XML adapter for Faceted Heritor
    """
    __used_for__ = IFacetedHeritor

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        return

    node = property(_exportNode, _importNode)
