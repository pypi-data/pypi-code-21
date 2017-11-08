""" XML Adapter
"""
from zope.component import queryMultiAdapter
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.interfaces import IBody
from eea.faceted.tool.interfaces import IFacetedTool

class FacetedToolXMLAdapter(XMLAdapterBase):
    """ Generic setup export/import xml adapter
    """
    __used_for__ = IFacetedTool

    def _exportBody(self):
        """Export the object as a file body.
        """
        self._doc.appendChild(self._exportNode())
        xml = self._doc.toprettyxml(' ', encoding='utf-8')
        self._doc.unlink()
        return xml
    body = property(_exportBody, XMLAdapterBase._importBody)

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        for portal_type in self.context.objectValues():
            exporter = queryMultiAdapter((portal_type, self.environ), IBody)
            node.appendChild(exporter.node)
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        purge = node.getAttribute('purge')
        purge = self._convertToBoolean(purge)
        if purge:
            self.context.manage_delObjects(self.context.objectIds())

        for child in node.childNodes:
            if child.nodeName != 'portal_type':
                continue

            purge_child = child.getAttribute('purge')
            purge_child = self._convertToBoolean(purge_child)
            uid = child.getAttribute('name').encode('utf-8')
            obj_ids = self.context.objectIds()
            if uid in obj_ids and purge_child:
                self.context.manage_delObjects([uid, ])
                continue

            portal_type = self.context._getOb(uid, None)
            if not portal_type:
                add = self.context.unrestrictedTraverse('@@add')
                portal_type = add.createAndAdd(dict(title=uid))

            importer = queryMultiAdapter((portal_type, self.environ), IBody)
            importer.node = child

    node = property(_exportNode, _importNode)
