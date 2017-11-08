""" XML Adapter
"""
from eea.relations.interfaces import IContentType
from Products.GenericSetup.utils import XMLAdapterBase

class ContentTypeXMLAdapter(XMLAdapterBase):
    """ Generic setup import/export xml adapter
    """
    __used_for__ = IContentType

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        for prop in ('title', 'ct_type', 'ct_interface', 'ct_default_location'):
            child = self._doc.createElement('property')
            child.setAttribute('name', prop)
            field = self.context.getField(prop)
            value = field.getAccessor(self.context)()
            if prop == 'ct_default_location' and value is None:
                value = u'python:None'
            value = self._doc.createTextNode(str(value))
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
            field = self.context.getField(name)
            field.getMutator(self.context)(value)
        self.context.reindexObject()

    node = property(_exportNode, _importNode)
