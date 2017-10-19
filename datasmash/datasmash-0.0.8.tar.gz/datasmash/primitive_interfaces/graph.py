from typing import *

from .base import Outputs
from .transformer import TransformerPrimitiveBase
from .types.graph import Graph

__all__ = ('GraphTransformerPrimitiveBase',)

Inputs = TypeVar('Inputs', bound=Sequence[Graph])


class GraphTransformerPrimitiveBase(TransformerPrimitiveBase[Inputs, Outputs]):
    """
    A base class for transformer primitives which take Graph objects as input.
    Graph is an interface which TA1 teams should implement for graph data.
    """
