'''
The subscriber type to use. Available are PRIORITY, ROUND_ROBIN; RATED.

Created on Nov 10, 2017

@author: aevans
'''

from enum import Enum


class SubscriberType(Enum):
    PRIORITY = 1
    ROUND_ROBIN = 2
    RATED = 3
