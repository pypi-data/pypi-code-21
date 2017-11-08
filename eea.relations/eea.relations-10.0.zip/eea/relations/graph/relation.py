""" Graph for Relation
"""
from pydot import Edge as PyEdge

from zope.component import queryAdapter
from zope.interface import implements
from eea.relations.graph.interfaces import IEdge, INode
from Products.CMFCore.utils import getToolByName

class Edge(object):
    """ Adapter for Relation to represent it as a pydot.Edge
    """
    implements(IEdge)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        """ Returns a pydot.Node object
        """
        rtool = getToolByName(self.context, 'portal_relations')

        # Source
        field = self.context.getField('from')
        nfrom = field.getAccessor(self.context)()
        if not nfrom in rtool.objectIds():
            return None

        nfrom = rtool[nfrom]
        nfrom = queryAdapter(nfrom, INode)
        if not nfrom:
            return None

        # Destination
        field = self.context.getField('to')
        nto = field.getAccessor(self.context)()
        if not nto in rtool.objectIds():
            return None

        nto = rtool[nto]
        nto = queryAdapter(nto, INode)
        if not nto:
            return None

        attributes = {}

        # Required
        field = self.context.getField('required')
        req = field.getAccessor(self.context)()
        if req:
            attributes['color'] = 'red'

        # Required for workflow state
        field = self.context.getField('required_for')
        req = field.getAccessor(self.context)()
        if req:
            attributes['fontcolor'] = '#74AE0B'
            attributes['label'] = '"%s"' % "\\n".join(req)

        # Edge
        return PyEdge(nfrom(), nto(), **attributes)

    def __repr__(self):
        """ Returns a string representation of the node in dot language.
        """
        return self().to_string()
