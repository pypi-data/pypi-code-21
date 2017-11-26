'''
The publisher type as an enum. Available are BALANCING, LOGIC; MULTIQUEUE.

Created on Nov 10, 2017

@author: aevans
'''

from enum import Enum

class PublisherType(Enum):
    BALANCING = 1
    LOGIC = 2
    MULTIQUEUE = 3
