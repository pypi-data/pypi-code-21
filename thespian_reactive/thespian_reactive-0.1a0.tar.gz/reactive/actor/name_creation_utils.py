'''
Utilities for handling name creation.

Created on Oct 29, 2017

@author: aevans
'''

from atomos.atomic import AtomicLong
from random import Random
import sys


num = AtomicLong(0)


def get_name():
    """
    Get a randomized name with the actor number.

    :return: The base name number_number.
    :rtype: str()
    """
    base = str(num.get_and_add(1))
    base += "_"
    base += str(Random().randint(0, sys.maxsize))
    return base
