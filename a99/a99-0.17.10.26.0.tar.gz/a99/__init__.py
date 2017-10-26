# # Temporary imports
#   =================
# These modules should be be del'eted at the end
import sys
import logging


# # Prevents from running in Python 2
#   =================================
# (http://stackoverflow.com/questions/9079036)
if sys.version_info[0] < 3:
    raise RuntimeError("Python version detected:\n*****\n{0!s}\n*****\nCannot run, must be using Python 3".format(sys.version))

# Antecipated import because of str_exc() used below
from .loggingaux import *


# # Initializes matplotlib to work with Qt4
#   =======================================
# Tk backend problems:
# - plot windows pop as modal
# - configuration options not as rich as Qt4Agg
# However, if another backend has been chosen before importing astroapi, will not choose Qt4 backend
flag_matplotlib = True
try:
    def init_agg():
        import matplotlib
        matplotlib.use('Qt5Agg')
    if not 'matplotlib.backends' in sys.modules:
        init_agg()
except ImportError as e:
    flag_matplotlib = False
    logging.warning("Error importing matplotlib: '{}', "
        "matplotlib-related resources will not available".format(str_exc(e)))

# # Setup
#   =====

# ## Constants affecting the Graphical User Interface style
#    ------------------------------------------------------

# ### Color definition
# Error color
COLOR_ERROR = "#AA0000" # sortta wine
# Warning color
COLOR_WARNING = "#C98A00" # sortta yellow
# Default color for label text
COLOR_DESCR = "#222222"


# ## Constants affecting logging
#    ---------------------------
#
# If the following need change, this should be done before calling get_python_logger() for the
# first time

# Set this to make the python logger to log to the console. Note: will have no
# effect if changed after the first call to get_python_logger()
flag_log_console = True

# Set this to make the python logger to log to a file named "python.log".
# Note: will have no effect if changed after the first call to get_python_logger()
flag_log_file = False

# Logging level for the python logger
logging_level = logging.INFO


from .conversion import *
from .debugging import *
from .fileio import *
from .introspection import *
if flag_matplotlib:
    from .matplotlibaux import *
from .misc import *
from .parts import *
from .search import *
from .textinterface import *
from .config import *
from .litedb import *
from .gui import *
from .datetimefunc import *
try:
    from .astropyaux import *
except ImportError as e:
    logging.warning("Error importing astropy: '{}', "
                    "astropy-related resources will not available".format(str_exc(e)))

# from . import conversion
# from . import debugging
# from . import fileio
# from . import introspection
# from . import loggingaux
# from . import matplotlibaux
# from . import misc
# from . import parts
# from . import search
# from . import textinterface
# from . import config
from . import gui

# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del init_agg, sys, logging  # Don't want this in the namespace
