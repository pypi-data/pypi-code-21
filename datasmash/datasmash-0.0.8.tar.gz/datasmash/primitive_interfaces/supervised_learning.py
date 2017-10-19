import abc

from .base import *

__all__ = ('SupervisedLearnerPrimitiveBase',)


class SupervisedLearnerPrimitiveBase(PrimitiveBase[Inputs, Outputs, Params]):
    """
    A base class for primitives which have to be fitted on both input and output data
    before they can start producing (useful) outputs from inputs.
    """

    @abc.abstractmethod
    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        """
        Sets training data of this primitive.

        Parameters
        ----------
        inputs : Inputs
            The inputs.
        outputs : Outputs
            The outputs.
        """
