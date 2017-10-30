#!/usr/bin/python
"""
Find an index of a number in a given np array
"""

import numpy as np

class myarray(np.ndarray):
    def __new__(cls, *args, **kwargs):
        return np.array(*args, **kwargs).view(myarray)
    def index(self, value):
        return np.where(self==value)



