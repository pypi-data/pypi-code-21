'''
The router type to use.  Options are BROADCAST (through pubsub), ROUND_ROBIN,
and RANDOM.

Created on Nov 1, 2017

@author: aevans
'''

from enum import Enum


class RouterType(Enum):
    BROADCAST = 1
    ROUND_ROBIN = 2
    RANDOM = 3
