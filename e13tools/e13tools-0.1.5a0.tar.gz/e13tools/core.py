# -*- coding: utf-8 -*-

"""
Core
====
Provides a collection of functions that are not specialized. Imported
automatically with e13Tools.

"""

# %% IMPORTS
from __future__ import division, absolute_import, print_function

import numpy as np


# %% FUNCTIONS
def product(*iterables):
    """
    Generates a list containing all possible permutations

    """

    # Create empty result list
    result = [[]]

    # Fill the list with all possible combinations
    for iterable in iterables:
        results = list(result)
        result = [[]]
        for x in results:
            for y in iterable:
                z = list(x)
                if(result == [[]]):
                    z.append(y)
                    result = [z]
                else:
                    z.append(y)
                    result.append(z)

    # Return it
    return(result)
