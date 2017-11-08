""" XML Adapter
"""
from eea.relations.interfaces import IRelation
from eea.relations.content.relation import RelationSchema
from Products.GenericSetup.utils import XMLAdapterBase


class RelationXMLAdapter(XMLAdapterBase):
    """ Generic setup import/export xml adapter
    """
    __used_for__ = IRelation

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        for prop in RelationSchema.keys():
            child = self._doc.createElement('property')
            child.setAttribute('name', prop)
            field = self.context.getField(prop)
            value = field.getAccessor(self.context)()
            if isinstance(value, (tuple, list)):
                for item in value:
                    if not value:
                        continue
                    element = self._doc.createElement('element')
                    element.setAttribute('value', item)
                    child.appendChild(element)
            else:
                if isinstance(value, (bool, int)):
                    value = repr(value)
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
            purge = child.getAttribute('purge')
            purge = self._convertToBoolean(purge)

            elements = []
            for element in child.childNodes:
                if element.nodeName != 'element':
                    continue
                elements.append(element.getAttribute('value'))
            if elements:
                value = elements if not purge else []
            else:
                value = self._getNodeText(child)
                value = value.decode('utf-8')
                value = value if not purge else u''

            if name in ('required',):
                value = self._convertToBoolean(value)
            field = self.context.getField(name)
            field.getMutator(self.context)(value)
        self.context.reindexObject()

    node = property(_exportNode, _importNode)
