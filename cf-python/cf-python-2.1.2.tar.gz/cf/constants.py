import sys

from psutil   import virtual_memory
from tempfile import gettempdir

from numpy.ma import masked as numpy_ma_masked
from numpy.ma import nomask as numpy_ma_nomask

#platform = sys.platform
#if platform == 'darwin':
#    from psutil import virtual_memory

# --------------------------------------------------------------------
# Find the total amount of memory, in bytes
# --------------------------------------------------------------------
_TOTAL_MEMORY = float(virtual_memory().total)
#if platform == 'darwin':
#    # MacOS
#    _MemTotal = float(virtual_memory().total)
#else:
#    # Linux
#    _meminfo_file = open('/proc/meminfo', 'r', 1)
#    for line in _meminfo_file:
#        field_size = line.split()
#        if field_size[0] == 'MemTotal:':
#            _MemTotal = float(field_size[1]) * 1024
#            break
#    #--- End: for
#    _meminfo_file.close()
##--- End: if



# --------------------------------------------------------------------
#   A dictionary of useful constants.
#
#   Whilst the dictionary may be modified directly, it is safer to
#   retrieve and set the values with a function where one is
#   provided. This is due to interdependencies between some values.
#
#   :Keys:
#
#        ATOL : float
#	    The value of absolute tolerance for testing numerically
#	    tolerant equality.
#
#        TOTAL_MEMORY : float
#	    Find the total amount of physical memory (in bytes).
#
#        CHUNKSIZE : float
#	    The chunk size (in bytes) for data storage and
#	    processing.
#
#        FM_THRESHOLD : float
#	    The minimum amount of memory (in bytes) to be kept free
#	    for temporary work space. This should always be
#	    MINNCFM*CHUNKSIZE.
#
#        MINNCFM : int
#	    The number of chunk sizes to be kept free for temporary
#	    work space.
#
#        OF_FRACTION : float
#	    The fraction of the maximum number of concurrently open
#	    files which may be used for files containing data
#	    arrays.
#
#        RTOL : float
#	    The value of relative tolerance for testing numerically
#	    tolerant equality.
#
#        TEMPDIR : str
#	    The location to store temporary files. By default it is
#	    the default directory used by the :mod:`tempfile` module.
#
#        REGRID_LOGGING : bool
#        Whether or not to enable ESMPy logging. If it is logging is performed
#        after every call to ESMPy. By default logging is disabled.
#
# --------------------------------------------------------------------
CONSTANTS = {'RTOL'              : sys.float_info.epsilon,
             'ATOL'              : sys.float_info.epsilon,
             'TEMPDIR'           : gettempdir(),
             'MINNCFM'           : 10,
             'OF_FRACTION'       : 0.5,
             'TOTAL_MEMORY'      : _TOTAL_MEMORY,
             'CHUNKSIZE'         : _TOTAL_MEMORY * 0.01,
             'REGRID_LOGGING'    : False,
             'RELAXED_IDENTITIES': False,
             'IGNORE_IDENTITIES' : False,
             }

CONSTANTS['FM_THRESHOLD'] = CONSTANTS['MINNCFM']*CONSTANTS['CHUNKSIZE']

masked = numpy_ma_masked
nomask = numpy_ma_nomask

_file_to_fh = {}

