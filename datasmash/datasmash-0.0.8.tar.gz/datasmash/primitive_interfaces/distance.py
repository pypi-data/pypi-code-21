import abc

from .base import *

__all__ = ('PairwiseDistancePrimitiveBase', 'AutoDistancePrimitiveBase',)


class PairwiseDistancePrimitiveBase(PrimitiveBase[(Inputs, Outputs, Params)]):
    """
    A base class for primitives which learn or compute distances (however defined) between two
    different sets of instances.

    Each metric learning method should probably implement both this and AutoDistancePrimitiveBase
    (as separate primitives), unless it cannot handle one or the other type of produce method.
    """

    @abc.abstractmethod
    def produce(self, *, inputs: Inputs, Y: Inputs = None, timeout: float = None, iterations: int = None) -> Outputs:
        """
        Overrides generic produce method.  Computes distance matrix between two sets of data.

        Parameters
        ----------
        inputs : Inputs
            Collection of instances.
        Y : Inputs
            Collection of instances.  Distance is computed between each instance in inputs and each
            instance in Y.
        timeout : float
            A maximum time this primitive should take to produce outputs during this method call, in seconds.
        iterations : int
            How many of internal iterations should the primitive do.
        """


class AutoDistancePrimitiveBase(PrimitiveBase[(Inputs, Outputs, Params)]):
    """
    A base class for primitives which learn or compute distances (however defined) within a set
    of instances.

    ``produce`` method should compute distance matrix within a set of data.

    Each metric learning method should probably implement both this and PairwiseDistancePrimitiveBase
    (as separate primitives), unless it cannot handle one or the other type of produce method.
    """
