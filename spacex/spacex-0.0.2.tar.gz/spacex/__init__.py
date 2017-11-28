"""

A synchronous wrapper for the Space X API.

"""

__tile__ = 'spacex'
__author__ = 'Tyler Gibbs'
__version__ = '0.0.2'
__copyright__ = 'Copyright 2017 TheTrain2000'
__license__ = 'MIT'

from .launchpad import *
from .company import *
from .vehicle import *
from .launch import *
from .errors import *
from .core import *
