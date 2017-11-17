'''
Module:
    tcl

Authors:
    Siming Yuan (siyuan), CSG Test - Ottawa

Description:
    This module provides a standard way for users to access Tcl code/libraries
    when using the python ATS infrastructure.

    This module requires environment variable AUTOTEST to be set to user's
    Tcl ATS tree for proper ATS Tcl functionalities to work.

    It acts as a wrapper to Python's Tkinter module, and in addition provides
    standard typecasting for easy conversion from Tcl string to python native
    objects.

    By default, this module provides one managed interpreter.

'''

# metadata
__version__ = '4.0.0'
__author__ = 'Cisco Systems'
__contact__ = 'pyats-support-ext@cisco.com'
__copyright__ = 'Copyright (c) 2017, Cisco Systems Inc.'

import os
import sys
import inspect
import logging

# create logger
logger = logging.getLogger(__name__)

# check whether tkinter is loadable first
try:
    from tkinter import TclError
except ImportError as e:
    # if 'AUTOTEST' not in os.environ:
    #     # drop a warning if user didn't source their ats tree.
    #     logger.warning('Environment variable AUTOTEST is not set.')

    # suppress the libtk8.4.so warning as it doesn't make sense to the user
    raise ImportError('Cannot use %s module when tkinter module cannot '
                      'be imported.' % __name__) from e

# only proceed with import from this module if tkinter loadable
from .interpreter import Interpreter
from .array import Array
from .keyedlist import KeyedList
from .tclstr import tclstr, tclobj
from .history import History, Entry
from .namespace import *

# create the managed interpreter instance
# and shortwire the module to it so everyone uses
# the same tcl interpreter
extra_members = inspect.getmembers(sys.modules[__name__], callable)

sys.modules[__name__] = interpreter = Interpreter()
for name, value in extra_members:
    setattr(interpreter, name, value)

# hardwire all module hidden attributes to interpreter instance
interpreter.__file__    = __file__
interpreter.__loader__  = __loader__
interpreter.__package__ = __package__
interpreter.__name__    = __name__
interpreter.__path__    = __path__
interpreter.__spec__    = __spec__
interpreter.__doc__     = __doc__
