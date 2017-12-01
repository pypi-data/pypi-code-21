#!/usr/bin/env python3

# internal modules
from numericalmodel.equations import PrognosticEquation

# external modules
import numpy as np

class LinearDecayEquation(PrognosticEquation):
    r"""
    A simple linear decay equation :math:`\frac{dT}{dt} = - a * T + F`
    """
    def linear_factor(self, time = None ):
        """ 
        The negative :math:`a` parameter
        """
        # take the "a" parameter from the input, interpolate it to the given
        # "time" and return the negative value
        return - self.input["a"](time)

    def independent_addend(self, time = None ):
        r""" 
        The forcing parameter :math:`F` 
        """
        # take the "F" forcing parameter from the input, interpolate it to
        # the given "time" and return it
        return self.input["F"](time)

    def nonlinear_addend(self, *args, **kwargs):
        r""" 
        The **linear** decay equation has no nonlinear part, so this is
        :math:`0`.
        """
        return 0 # nonlinear addend is always zero (LINEAR decay equation)

