'''
A set of restart strategies.  These are used to restart actors when a child
dies.

Created on Nov 13, 2017

@author: aevans
'''

from enum import Enum


class Strategy(Enum):
    """
    Restart strategies.  This includes one to one; halt.
    """
    ONE_TO_ONE = 1
    HALT = 2
