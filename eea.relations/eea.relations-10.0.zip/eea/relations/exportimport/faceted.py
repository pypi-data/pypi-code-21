""" XML Adapter
"""
#from zope import event
from eea.relations.interfaces import IFacetedNavigable
from eea.relations.exportimport.contenttype import ContentTypeXMLAdapter
from eea.facetednavigation.exportimport.faceted import \
     FacetedNavigableXMLAdapter as FacetedXMLAdapter
from Products.GenericSetup.utils import XMLAdapterBase

class FacetedNavigableXMLAdapter(XMLAdapterBase):
    """ Generic setup import/export xml adapter
    """
    __used_for__ = IFacetedNavigable

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        content = ContentTypeXMLAdapter(self.context, self.environ)
        node = content.node
        faceted = FacetedXMLAdapter(self.context, self.environ)
        for child in faceted.node.childNodes:
            if not child.childNodes:
                continue
            node.appendChild(child)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        content = ContentTypeXMLAdapter(self.context, self.environ)
        content._importNode(node)
        faceted = FacetedXMLAdapter(self.context, self.environ)
        faceted._importNode(node)

    node = property(_exportNode, _importNode)
