""" EEA Relations public interfaces
"""
# Content
from eea.relations.content.interfaces import IBaseObject
from eea.relations.content.interfaces import IToolAccessor
from eea.relations.content.interfaces import IRelationsTool
from eea.relations.content.interfaces import IContentType
from eea.relations.content.interfaces import IRelation

# Subtypes
from eea.relations.subtypes.interfaces import IFacetedNavigable

# Graph
from eea.relations.graph.interfaces import INode
from eea.relations.graph.interfaces import IEdge
from eea.relations.graph.interfaces import IGraph

# Commponents
from eea.relations.component.interfaces import IContentTypeLookUp
from eea.relations.component.interfaces import IRelationsLookUp

# Auto discovered relations API
from eea.relations.discover.interfaces import IAutoRelations

# pylint, pyflakes
__all__ = [
    IBaseObject.__name__,
    IToolAccessor.__name__,
    IRelationsTool.__name__,
    IContentType.__name__,
    IRelation.__name__,
    IFacetedNavigable.__name__,
    INode.__name__,
    IEdge.__name__,
    IGraph.__name__,
    IContentTypeLookUp.__name__,
    IRelationsLookUp.__name__,
    IAutoRelations.__name__,
]
