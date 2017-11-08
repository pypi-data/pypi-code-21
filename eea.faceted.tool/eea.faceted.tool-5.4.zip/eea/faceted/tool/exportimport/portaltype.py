""" XML Adapter
"""
from eea.faceted.tool.interfaces import IPortalType
from Products.GenericSetup.utils import XMLAdapterBase

class FacetedPortalTypeXMLAdapter(XMLAdapterBase):
    """ Generic setup import/export xml adapter
    """
    __used_for__ = IPortalType

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._doc.createElement('portal_type')
        node.setAttribute('name', self.context.getId())
        for prop in ('title', 'search_type', 'search_interface'):
            child = self._doc.createElement('property')
            child.setAttribute('name', prop)
            value = getattr(self.context, prop, None) or ''
            value = self._doc.createTextNode(value)
            child.appendChild(value)
            node.appendChild(child)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue

            name = child.getAttribute('name')
            value = self._getNodeText(child)
            value = value.decode('utf-8')
            purge = child.getAttribute('purge')
            purge = self._convertToBoolean(purge)
            if purge:
                value = u''
            setattr(self.context, name, value)

    node = property(_exportNode, _importNode)
