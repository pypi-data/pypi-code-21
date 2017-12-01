#!/usr/bin/env python3

# internal modules
from numericalmodel.examples.equations.lineardecay import LinearDecayEquation
from numericalmodel.numericalmodel import NumericalModel
from numericalmodel.interfaces import *
from numericalmodel.numericalschemes import *
from . import NumericalModelExampleArgumentParser

# external modules
import numpy as np
np.random.seed(42)


class LinearDecayModel(NumericalModel):
    """ 
    A simple linear decay model as a temperature adjustment

    - Euler implicit scheme

    """
    def __init__(self):
        # create a model
        super().__init__()
        self.initial_time = 0
        self.name = "linear decay model"
        self.description = "a simple linear decay model"

        # define values
        temperature = StateVariable( 
            id = "T", name = "temperature", unit = "K", bounds = [0,np.Inf]  )
        parameter = Parameter( 
            id = "a", name = "linear parameter", unit = "1/s",
            bounds = [0,np.Inf]  )
        forcing = ForcingValue( 
            id = "F", name = "forcing parameter", unit = "K/s",
            bounds = [0,np.Inf] )

        # add the values to the model
        self.variables  = SetOfStateVariables( [ temperature  ]  )
        self.parameters = SetOfParameters(     [ parameter  ]    )
        self.forcing    = SetOfForcingValues(  [ forcing  ]      )

        # set initial values
        self.variables["T"].value  = 20 + 273.15
        self.parameters["a"].value = 0.1
        self.forcing["F"].value    = 28

        # create an equation object
        decay_equation = LinearDecayEquation(
            variable = temperature,
            input = SetOfInterfaceValues( [parameter, forcing] ),
            )

        # create a numerical scheme
        implicit_scheme = EulerImplicit(
            equation = decay_equation
            )

        # add the numerical scheme to the model
        self.numericalschemes = SetOfNumericalSchemes( [ implicit_scheme ] )


if __name__ == "__main__":
    model = LinearDecayModel()
    parser = NumericalModelExampleArgumentParser(
        description = "linear decay model")
    parser.cli(model)
