""" Graph interfaces
"""
from zope.interface import Interface

class INode(Interface):
    """ Generate pydot.Node from context properties
    """

class IEdge(Interface):
    """ Generate pydot.Edge from context properties
    """

class IGraph(Interface):
    """ Utility to generate image from pydot.Graph
    """
    def __call__(graph):
        """ Generate image
        """
