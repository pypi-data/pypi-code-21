import resource
import copy
import cPickle
import netCDF4
import psutil

from numpy import __file__          as numpy__file__
from numpy import __version__       as numpy__version__
from numpy import all               as numpy_all
from numpy import allclose          as numpy_allclose
from numpy import array             as numpy_array
from numpy import ascontiguousarray as numpy_ascontiguousarray 
from numpy import dtype             as numpy_dtype
from numpy import isclose           as numpy_isclose
from numpy import ndarray           as numpy_ndarray
from numpy import ndim              as numpy_ndim
from numpy import number            as numpy_number
from numpy import shape             as numpy_shape
from numpy import sign              as numpy_sign
from numpy import take              as numpy_take
from numpy import tile              as numpy_tile
from numpy import where             as numpy_where

from numpy.ma import all       as numpy_ma_all
from numpy.ma import allclose  as numpy_ma_allclose
from numpy.ma import is_masked as numpy_ma_is_masked
from numpy.ma import isMA      as numpy_ma_isMA
from numpy.ma import masked    as numpy_ma_masked

from collections import Iterable
from hashlib     import md5 as hashlib_md5
from marshal     import dumps as marshal_dumps
from math        import ceil as math_ceil
from os          import getpid, listdir, mkdir, curdir
from os.path     import isfile       as os_path_isfile
from os.path     import abspath      as os_path_abspath
from os.path     import commonprefix as os_path_commonprefix
from os.path     import expanduser   as os_path_expanduser
from os.path     import expandvars   as os_path_expandvars
from os.path     import dirname      as os_path_dirname
from os.path     import join         as os_path_join
from os.path     import relpath      as os_path_relpath 
from inspect     import getargspec
from itertools   import product as itertools_product
from itertools   import izip, izip_longest
from platform    import system, platform, python_version
from psutil      import virtual_memory, Process
from sys         import executable as sys_executable
from urlparse    import urlparse as urlparse_urlparse
from urlparse    import urljoin  as urlparse_urljoin

from .          import __version__, __file__
from .constants import CONSTANTS, _file_to_fh

# Are we running on GNU/Linux?
_linux = system() == 'Linux'

if _linux:
    # ----------------------------------------------------------------
    # GNU/LINUX
    # ----------------------------------------------------------------
    _meminfo_fields = set(('SReclaimable:', 'Cached:', 'Buffers:', 'MemFree:'))
#    _meminfo_file   = open('/proc/meminfo', 'r', 1)

    def _free_memory():
        '''

The amount of available physical memory on GNU/Linux.

This amount includes any memory which is still allocated but is no
longer required.

:Returns:

    out: `float`
        The amount of available physical memory in bytes.

:Examples:

>>> _free_memory()
96496240.0

'''
        # https://github.com/giampaolo/psutil/blob/master/psutil/_pslinux.py

        # ----------------------------------------------------------------
        # The available physical memory is the sum of the values of
        # the 'SReclaimable', 'Cached', 'Buffers' and 'MemFree'
        # entries in the /proc/meminfo file
        # (http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/tree/Documentation/filesystems/proc.txt).
        # ----------------------------------------------------------------
        free_KiB = 0.0
        n=0
        _meminfo_file   = open('/proc/meminfo', 'r', 1)
        for line in _meminfo_file:
            field_size = line.split()
            if field_size[0] in _meminfo_fields:
                free_KiB += float(field_size[1])
                n += 1
                if n > 3:
                    break
        #--- End: for
#        _meminfo_file.seek(0)
        del _meminfo_file

        return free_KiB * 1024
    #--- End: def
else:
    # ----------------------------------------------------------------
    # NOT GNU/LINUX
    # ----------------------------------------------------------------
    def _free_memory():
        '''

The amount of available physical memory.

:Returns:

    out: `float`
        The amount of available physical memory in bytes.

:Examples:

>>> _free_memory()
96496240.0

'''
        return float(virtual_memory().available)
    #--- End: def
#--- End: if

def FREE_MEMORY():
    '''The available physical memory.

:Returns:

    out: `float`
        The amount of free memory in bytes.

:Examples:

>>> import numpy
>>> print 'Free memory =', cf.FREE_MEMORY()/2**30, 'GiB'
Free memory = 88.2728042603 GiB
>>> a = numpy.arange(10**9)
>>> print 'Free memory =', cf.FREE_MEMORY()/2**30, 'GiB'
Free memory = 80.8082618713 GiB
>>> del a
>>> print 'Free memory =', cf.FREE_MEMORY()/2**30, 'GiB'
Free memory = 88.2727928162 GiB

    '''
    return _free_memory()
#--- End: def

def FM_THRESHOLD():
    '''The amount of memory which is kept free as a temporary work space.

This is the chunk size (returned and set by `cf.CHUNKSIZE`) multiplied
by the number of chunks of memory to be kept free (returned and set by
`cf.MINNCFM`).

.. seealso:: `cf.CHUNKSIZE`, `cf.MINNCFM`

:Returns:

    out: `float`
        The amount of memory in bytes.

:Examples:

>>> cf.FM_THRESHOLD()
10000000000.0
>>> old = cf.MINNCFM(2*cf.MINNCFM())
>>> cf.FM_THRESHOLD()
20000000000.0

    '''
    return CONSTANTS['FM_THRESHOLD']
#--- End: def

def CHUNKSIZE(*size):
    '''

The memory chunk size in bytes for data storage and processing.

When setting the chunk size, the amount of minimum amount of memory to
be kept free as a temporary work space is also updated.

.. seealso:: `cf.MINNCFM`

:Examples 1:

>>> current_chunksize = cf.CHUNKSIZE()

:Parameters:

    size: `int`, optional
        The new chunk size in bytes. The default is to not change the
        current value.

:Returns:

    out: `float`
        The value prior to the change, or the current value if no new
        value was specified.

:Examples 2:

>>> cf.CHUNKSIZE()
57095864.32
>>> old = cf.CHUNKSIZE(2**30)
>>> cf.CHUNKSIZE(old)
1073741824
>>> cf.CHUNKSIZE()
57095864.32

'''
    old = CONSTANTS['CHUNKSIZE']
    if size:
        size = size[0]
        CONSTANTS['CHUNKSIZE']    = size
        CONSTANTS['FM_THRESHOLD'] = MINNCFM() * size

    return old
#--- End: def

def TOTAL_MEMORY():
    '''
'''
    return CONSTANTS['TOTAL_MEMORY']
#--- End: def

def MINNCFM(*arg):
    '''

The number of chunks of memory to be kept free as a temporary work
space.

A chunk of memory is the amount of memory set by `cf.CHUNKSIZE`.
 
.. seealso:: `cf.CHUNKSIZE`

:Parameters:

    arg : int, optional
        The number of chunks to be kept free as a temporary work
        space. The default is to not change the current value.

:Returns:

    out: `int`
        The value prior to the change, or the current value if no new
        value was specified.

:Examples:

>>> cf.MINNCFM()
10
>>> old = cf.MINNCFM(20)
>>> cf.MINNCFM(old)
20
>>> f.MINNCFM()
10

'''
    old = CONSTANTS['MINNCFM']
    if arg:
        minncfm = arg[0]
        CONSTANTS['MINNCFM']      = minncfm
        CONSTANTS['FM_THRESHOLD'] = minncfm * CHUNKSIZE()

    return old
#--- End: def

def TEMPDIR(*arg):
    '''

The directory for internally generated temporary files.

When setting the directory, it is created if the specified path does
not exist.

:Parameters:

    arg : str, optional
        The new directory for temporary files. Tilde expansion (an
        initial component of ``~`` or ``~user`` is replaced by that
        *user*'s home directory) and environment variable expansion
        (substrings of the form ``$name`` or ``${name}`` are replaced
        by the value of environment variable *name*) are applied to
        the new directory name.

        The default is to not change the directory.

:Returns:

    out: `str`
        The directory prior to the change, or the current directory if
        no new value was specified.

:Examples:

>>> cf.TEMPDIR()
'/tmp'
>>> old = cf.TEMPDIR('/home/me/tmp')
>>> cf.TEMPDIR(old)
'/home/me/tmp'
>>> cf.TEMPDIR()
'/tmp'

'''
    old = CONSTANTS['TEMPDIR']
    if arg:
        tempdir = os_path_expanduser(os_path_expandvars(arg[0]))

        # Create the directory if it does not exist.
        try:
            mkdir(tempdir)
        except OSError:
            pass

        CONSTANTS['TEMPDIR'] = tempdir
    #--- End: if

    return old
#--- End: def

def OF_FRACTION(*arg):
    '''

The amount of concurrently open files above which files containing
data arrays may be automatically closed.

The amount is expressed as a fraction of the maximum possible number
of concurrently open files.

Note that closed files will be automatically reopened if subsequently
needed by a variable to access its data array.

.. seealso:: `cf.close_files`, `cf.close_one_file`, `cf.open_files`,
             `cf.open_files_threshold_exceeded`

:Parameters:

    arg : float, optional
        The new fraction (between 0.0 and 1.0). The default is to not
        change the current behaviour.

:Returns:

    out: `float`
        The value prior to the change, or the current value if no new
        value was specified.

:Examples:

>>> cf.OF_FRACTION()
0.5
>>> old = cf.OF_FRACTION(0.33)
>>> cf.OF_FRACTION(old)
0.33
>>> cf.OF_FRACTION()
0.5

The fraction may be translated to an actual number of files as
follows:

>>> old = cf.OF_FRACTION(0.75)
>>> import resource
>>> max_open_files = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
>>> threshold = int(max_open_files * cf.OF_FRACTION())
>>> max_open_files, threshold
(1024, 768)

'''
    old = CONSTANTS['OF_FRACTION']
    if arg:
        CONSTANTS['OF_FRACTION'] = arg[0]

    return old
#--- End: def

def REGRID_LOGGING(*arg):
    '''

Whether or not to enable ESMPy logging.

If it is logging is performed after every call to ESMPy.

:Parameters:

    arg: `bool`, optional
        The new value (either True to enable logging or False to disable it).
        The default is to not change the current behaviour.

:Returns:

    out: `bool`
        The value prior to the change, or the current value if no new
        value was specified.

:Examples:

>>> cf.REGRID_LOGGING()
False
>>> cf.REGRID_LOGGING(True)
False
>>> cf.REGRID_LOGGING()
True

    '''
    old = CONSTANTS['REGRID_LOGGING']
    if arg:
        CONSTANTS['REGRID_LOGGING'] = bool(arg[0])
    
    return old
#--- End:def

def RELAXED_IDENTITIES(*arg):
    '''

:Parameters:

    arg: `bool`, optional
      
:Returns:

    out: `bool`
        The value prior to the change, or the current value if no new
        value was specified.

:Examples:

>>> org = cf.RELAXED_IDENTITIES()
>>> print org
False
>>> cf.RELAXED_IDENTITIES(True)
False
>>> cf.RELAXED_IDENTITIES()
True
>>> cf.RELAXED_IDENTITIES(org)
True
>>> cf.RELAXED_IDENTITIES()
False

    '''
    old = CONSTANTS['RELAXED_IDENTITIES']
    if arg:
        CONSTANTS['RELAXED_IDENTITIES'] = bool(arg[0])
    
    return old
#--- End:def

def IGNORE_IDENTITIES(*arg):
    '''

:Parameters:

    arg: `bool`, optional
      
:Returns:

    out: `bool`
        The value prior to the change, or the current value if no new
        value was specified.

:Examples:

>>> org = cf.IGNORE_IDENTITIES()
>>> print org
False
>>> cf.IGNORE_IDENTITIES(True)
False
>>> cf.IGNORE_IDENTITIES()
True
>>> cf.IGNORE_IDENTITIES(org)
True
>>> cf.IGNORE_IDENTITIES()
False

    '''
    old = CONSTANTS['IGNORE_IDENTITIES']
    if arg:
        CONSTANTS['IGNORE_IDENTITIES'] = bool(arg[0])
    
    return old
#--- End:def

def dump(x, **kwargs):
    '''
    
Print a description of an object.

If the object has a `!dump` method then this is used to create the
output, so that ``cf.dump(f)`` is equivalent to ``print f.dump()``.
Otherwise ``cf.dump(x)`` is equivalent to ``print x``.

:Parameters:

    x :
        The object to print.

    kwargs : *optional*
        As for the input variable's `!dump` method, if it has one.

:Returns:

    None

:Examples:

>>> x = 3.14159
>>> cf.dump(x)
3.14159

>>> f
<CF Field: rainfall_rate(latitude(10), longitude(20)) kg m2 s-1>
>>> cf.dump(f)
>>> cf.dump(f, complete=True)

'''
    if hasattr(x, 'dump') and callable(x.dump):
        print x.dump(**kwargs)
    else:
        print x
#--- End: def

_max_number_of_open_files = resource.getrlimit(resource.RLIMIT_NOFILE)[0]

if _linux:
    # ----------------------------------------------------------------
    # GNU/LINUX
    # ----------------------------------------------------------------

    # Directory containing a symbolic link for each file opened by the
    # current python session
    _fd_dir = '/proc/'+str(getpid())+'/fd'

    def open_files_threshold_exceeded():
        '''

Return True if the total number of open files is greater than the
current threshold. GNU/LINUX.

The threshold is defined as a fraction of the maximum possible number
of concurrently open files (an operating system dependent amount). The
fraction is retrieved and set with the `OF_FRACTION` function.

.. seealso:: `cf.close_files`, `cf.close_one_file`, `cf.open_files`

:Returns:

    out: `bool`
        Whether or not the number of open files exceeds the threshold.

:Examples:

In this example, the number of open files is 75% of the maximum
possible number of concurrently open files:

>>> cf.OF_FRACTION()
0.5
>>> print cf.open_files_threshold_exceeded()
True
>>> cf.OF_FRACTION(0.9)
>>> print cf.open_files_threshold_exceeded()
False

'''
        return len(listdir(_fd_dir)) > _max_number_of_open_files * OF_FRACTION()
    #---End: def
else:
    # ----------------------------------------------------------------
    # NOT GNU/LINUX
    # ---------------------------------------------------------------- 
    _process = Process(getpid())

    def open_files_threshold_exceeded():
        '''

Return True if the total number of open files is greater than the
current threshold.

The threshold is defined as a fraction of the maximum possible number
of concurrently open files (an operating system dependent amount). The
fraction is retrieved and set with the `OF_FRACTION` function.

.. seealso:: `cf.close_files`, `cf.close_one_file`, `cf.open_files`

:Returns:

    out: `bool`
        Whether or not the number of open files exceeds the threshold.

:Examples:

In this example, the number of open files is 75% of the maximum
possible number of concurrently open files:

>>> cf.OF_FRACTION()
0.5
>>> print cf.open_files_threshold_exceeded()
True
>>> cf.OF_FRACTION(0.9)
>>> print cf.open_files_threshold_exceeded()
False

'''
        return len(_process.open_files()) > _max_number_of_open_files * OF_FRACTION()
    #---End: def
#---End: if

def close_files(file_format=None):
    '''Close open files containing sub-arrays of data arrays.

By default all such files are closed, but this may be restricted to
files of a particular format.

Note that closed files will be automatically reopened if subsequently
needed by a variable to access the sub-array.

If there are no appropriate open files then no action is taken.

.. seealso:: `cf.close_one_file`, `cf.open_files`,
             `cf.open_files_threshold_exceeded`

:Parameters:

    file_format : str, optional
        Only close files of the given format. Recognised formats are
        ``'netCDF'`` and ``'PP'``. By default files of any format are
        closed.

:Returns:

    None

:Examples:

>>> cf.close_files()
>>> cf.close_files('netCDF')
>>> cf.close_files('PP')

    '''
    if file_format is not None:
        if file_format in _file_to_fh:
            for fh in _file_to_fh[file_format].itervalues():
                fh.close()
        
            _file_to_fh[file_format].clear()
    else:
        for file_format, value in _file_to_fh.iteritems():
            for fh in value.itervalues():
                fh.close()
        
            _file_to_fh[file_format].clear()
#---End: def

def close_one_file(file_format=None):
    '''Close an arbitrary open file containing a sub-array of a data
array.

By default a file of arbitrary format is closed, but the choice may be
restricted to files of a particular format.

Note that the closed file will be automatically reopened if
subsequently needed by a variable to access the sub-array.

If there are no appropriate open files then no action is taken.

.. seealso:: `cf.close_files`, `cf.open_files`,
             `cf.open_files_threshold_exceeded`

:Parameters:

    file_format : str, optional
        Only close a file of the given format. Recognised formats are
        ``'netCDF'`` and ``'PP'``. By default a file of any format is
        closed.

:Returns:

    None

:Examples:

>>> cf.close_one_file()
>>> cf.close_one_file('netCDF')
>>> cf.close_one_file('PP')

>>> cf.open_files()
{'netCDF': {'file1.nc': <netCDF4.Dataset at 0x181bcd0>,
            'file2.nc': <netCDF4.Dataset at 0x1e42350>,
            'file3.nc': <netCDF4.Dataset at 0x1d185e9>}}
>>> cf.close_one_file()
>>> cf.open_files()
{'netCDF': {'file1.nc': <netCDF4.Dataset at 0x181bcd0>,
            'file3.nc': <netCDF4.Dataset at 0x1d185e9>}}

'''
    if file_format is not None:
        if file_format in _file_to_fh and _file_to_fh[file_format]:
            filename, fh = next(_file_to_fh[file_format].iteritems())
            fh.close()
            del _file_to_fh[file_format][filename]
   
    else:    
        for values in _file_to_fh.itervalues():
            if not values:
                continue
        
            filename, fh = next(values.iteritems())
            fh.close()
            del values[filename]
            return
#---End: def

def open_files(file_format=None):
    '''

Return the open files containing sub-arrays of master data arrays.

By default all such files are returned, but the selection may be
restricted to files of a particular format.

.. seealso:: `cf.close_files`, `cf.close_one_file`,
             `cf.open_files_threshold_exceeded`

:Parameters:

    file_format : str, optional
        Only return files of the given format. Recognised formats are
        ``'netCDF'`` and ``'PP'``. By default all files are returned.

:Returns:

    out: `dict`
        If *file_format* is set then return a dictionary of file names
        of the specified format and their open file objects. If
        *file_format* is not set then return a dictionary for which
        each key is a file format whose value is the dictionary that
        would have been returned if the *file_format* parameter was
        set.

:Examples:

>>> cf.open_files()
{'netCDF': {'file1.nc': <netCDF4.Dataset at 0x187b6d0>}}
>>> cf.open_files('netCDF')
{'file1.nc': <netCDF4.Dataset at 0x187b6d0>}
>>> cf.open_files('PP')
{}

'''  
    if file_format is not None:
        if file_format in _file_to_fh:
            return _file_to_fh[file_format].copy()
        else:
            return {}
    else:   
        out = {}
        for file_format, values in _file_to_fh.iteritems():
            out[file_format] = values.copy()
            
        return out
#---End: def


def ufunc(name, x, *args, **kwargs):
    '''

The variable must have a `!copy` method and a method called
*name*. Any optional positional and keyword arguments are passed
unchanged to the variable's *name* method.

:Parameters:

    name : str

    x :
        The input variable.

    args, kwargs :


:Returns:

    out: 
        A new variable with size 1 axes inserted into the data array.

:Examples:

'''
    x = x.copy()
    getattr(x, name)(*args, **kwargs)
    return x
#--- End: def

def _numpy_allclose(a, b, rtol=None, atol=None):
    '''

Returns True if two broadcastable arrays have equal values to within
numerical tolerance, False otherwise.

The tolerance values are positive, typically very small numbers. The
relative difference (``rtol * abs(b)``) and the absolute difference
``atol`` are added together to compare against the absolute difference
between ``a`` and ``b``.

:Parameters:

    a, b : array_like
        Input arrays to compare.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

:Returns:

    out: `bool`
        Returns True if the arrays are equal, otherwise False.

:Examples:

>>> cf._numpy_allclose([1, 2], [1, 2])
True
>>> cf._numpy_allclose(numpy.array([1, 2]), numpy.array([1, 2]))
True
>>> cf._numpy_allclose([1, 2], [1, 2, 3])
False
>>> cf._numpy_allclose([1, 2], [1, 4])
False

>>> a = numpy.ma.array([1])
>>> b = numpy.ma.array([2])
>>> a[0] = numpy.ma.masked
>>> b[0] = numpy.ma.masked
>>> cf._numpy_allclose(a, b)
True

'''

    # THIS IS WHERE SOME NUMPY FUTURE WARNINGS ARE COMING FROM
    
    a_is_masked = numpy_ma_isMA(a)
    b_is_masked = numpy_ma_isMA(b)
    
    if not (a_is_masked or b_is_masked):
        try:            
            return numpy_allclose(a, b, rtol=rtol, atol=atol)
        except (IndexError, NotImplementedError, TypeError):
            return numpy_all(a == b)
    else:
        if a_is_masked and b_is_masked:
            if (a.mask != b.mask).any():
                return False
        else:
            return False

        try:
            return numpy_ma_allclose(a, b, rtol=rtol, atol=atol)
        except (IndexError, NotImplementedError, TypeError):
            out = numpy_ma_all(a == b)
            if out is numpy_ma_masked:
                return True
            else:
                return out
#--- End: def

def _numpy_isclose(a, b, rtol=None, atol=None):
    '''Returns a boolean array where two broadcastable arrays are
element-wise equal within a tolerance.

The tolerance values are positive, typically very small numbers. The
relative difference (``rtol * abs(b)``) and the absolute difference
``atol`` are added together to compare against the absolute difference
between ``a`` and ``b``.

:Parameters:

    a, b: array_like
        Input arrays to compare.

    atol: `float`, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol: `float`, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

:Returns:

    out: `numpy.ndarray`

:Examples:

    '''      
    try:
        return numpy_isclose(a, b, rtol=rtol, atol=atol)
    except (IndexError, NotImplementedError, TypeError):
        return a == b
#--- End: def

def parse_indices(shape, indices, cyclic=False, reverse=False, envelope=False):
    '''

:Parameters:

    shape: sequence of `ints`

    indices: `tuple` (not a `list`!)

:Returns:

    out: `list` [, `dict`]

:Examples:

'''
    parsed_indices = []
    roll           = {}
    flip           = []
    compressed_indices = []

    if not isinstance(indices, tuple):
        indices = (indices,)

    # Initialize the list of parsed indices as the input indices with any
    # Ellipsis objects expanded
    length = len(indices)
    n = len(shape)
    ndim = n
    for index in indices:
        if index is Ellipsis:
            m = n-length+1
            parsed_indices.extend([slice(None)] * m)
            n -= m            
        else:
            parsed_indices.append(index)
            n -= 1

        length -= 1
    #--- End: for
    len_parsed_indices = len(parsed_indices)

    if ndim and len_parsed_indices > ndim:
        raise IndexError("Invalid indices %s for array with shape %s" %
                         (parsed_indices, shape))

    if len_parsed_indices < ndim:
        parsed_indices.extend([slice(None)]*(ndim-len_parsed_indices))

    if not ndim and parsed_indices:
        ## If data is scalar then allow it to be indexed with an
        ## equivalent to [0]
        #if (len_parsed_indices == 1 and
        #    parsed_indices[0] in (0, 
        #                          -1,
        #                          slice(0, 1), 
        #                          slice(-1, None, -1),  
        #                          slice(None, None, None))):
        #    parsed_indices = []
        #else:            
        raise IndexError("Scalar array can only be indexed with () or Ellipsis")

    #--- End: if


    for i, (index, size) in enumerate(zip(parsed_indices, shape)):
        is_slice = False
        if isinstance(index, slice):            
            is_slice = True
            start = index.start
            stop  = index.stop
            step  = index.step
            if start is None or stop is None:
                step = 0
            elif step is None:
                step = 1

            if step > 0:
                if 0 < start < size and 0 <= stop <= start:
                    # 6:0:1 => -4:0:1
                    # 6:1:1 => -4:1:1
                    # 6:3:1 => -4:3:1
                    # 6:6:1 => -4:6:1
                    start = size-start
                elif -size <= start < 0 and -size <= stop <= start:
                    # -4:-10:1  => -4:1:1
                    # -4:-9:1   => -4:1:1
                    # -4:-7:1   => -4:3:1
                    # -4:-4:1   => -4:6:1 
                    # -10:-10:1 => -10:0:1
                    stop += size
            elif step < 0:
                if -size <= start < 0 and start <= stop < 0:
                    # -4:-1:-1   => 6:-1:-1
                    # -4:-2:-1   => 6:-2:-1
                    # -4:-4:-1   => 6:-4:-1
                    # -10:-2:-1  => 0:-2:-1
                    # -10:-10:-1 => 0:-10:-1
                    start += size
                elif 0 <= start < size and start < stop < size:
                    # 0:6:-1 => 0:-4:-1
                    # 3:6:-1 => 3:-4:-1
                    # 3:9:-1 => 3:-1:-1
                    stop -= size
            #--- End: if            
                        
            if step > 0 and -size <= start < 0 and 0 <= stop <= size+start:
                # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                # -1:0:1  => [9]
                # -1:1:1  => [9, 0]
                # -1:3:1  => [9, 0, 1, 2]
                # -1:9:1  => [9, 0, 1, 2, 3, 4, 5, 6, 7, 8]
                # -4:0:1  => [6, 7, 8, 9]
                # -4:1:1  => [6, 7, 8, 9, 0]
                # -4:3:1  => [6, 7, 8, 9, 0, 1, 2]
                # -4:6:1  => [6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
                # -9:0:1  => [1, 2, 3, 4, 5, 6, 7, 8, 9]
                # -9:1:1  => [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
                # -10:0:1 => [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                if cyclic:
                    index = slice(0, stop-start, step)
                    roll[i] = -start
                else:
                    index = slice(start, stop, step)

            elif step < 0 and 0 <= start < size and start-size <= stop < 0:
                # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                # 0:-4:-1  => [0, 9, 8, 7]
                # 6:-1:-1  => [6, 5, 4, 3, 2, 1, 0]
                # 6:-2:-1  => [6, 5, 4, 3, 2, 1, 0, 9]
                # 6:-4:-1  => [6, 5, 4, 3, 2, 1, 0, 9, 8, 7]
                # 0:-2:-1  => [0, 9]
                # 0:-10:-1 => [0, 9, 8, 7, 6, 5, 4, 3, 2, 1]
                if cyclic:
                    index = slice(start-stop-1, None, step)
                    roll[i] = -1 - stop
                else:
                    index = slice(start, stop, step)

            else:
                start, stop, step = index.indices(size)
                if (start == stop or
                    (start < stop and step < 0) or
                    (start > stop and step > 0)):
                    raise IndexError(
"Invalid indices {} for array with shape {}".format(parsed_indices, shape))
                if step < 0 and stop < 0:
                    stop = None
                index = slice(start, stop, step)
         
        elif isinstance(index, (int, long)):
            if index < 0: 
                index += size

            index = slice(index, index+1, 1)
            is_slice = True
        else:
            convert2positve = True
            if getattr(getattr(index, 'dtype', None), 'kind', None) == 'b':
                # Convert booleans to non-negative integers. We're
                # assuming that anything with a dtype attribute also
                # has a size attribute.
                if index.size != size:
                    raise IndexError(
                        "Invalid indices %s for array with shape %s" %
                        (parsed_indices, shape))

                index = numpy_where(index)[0]
                convert2positve = False
            #--- End: if

            if not numpy_ndim(index):
                if index < 0:
                    index += size

                index = slice(index, index+1, 1)
                is_slice = True
            else:
                len_index = len(index)
                if len_index == 1:                
                    index = index[0]
                    if index < 0:
                        index += size
                    
                    index = slice(index, index+1, 1)
                    is_slice = True
                elif len_index:
                    if convert2positve:
                        # Convert to non-negative integer numpy array
                        index = numpy_array(index)
                        index = numpy_where(index < 0, index+size, index)
    
                    steps = index[1:] - index[:-1]
                    step = steps[0]
                    if step and not (steps - step).any():
                        # Replace the numpy array index with a slice
                        if step > 0:
                            start, stop = index[0], index[-1]+1
                        elif step < 0:
                            start, stop = index[0], index[-1]-1
                            
                        if stop < 0:
                            stop = None
                                
                        index = slice(start, stop, step)
                        is_slice = True
                    else:
                        if ((step > 0 and (steps <= 0).any()) or
                            (step < 0 and (steps >= 0).any()) or
                            not step):
                            raise ValueError("Bad index (not strictly monotonic): %s" % index)
                            
                        if reverse and step < 0:
                            # The array is strictly monotoniticall
                            # decreasing, so reverse it so that it's
                            # strictly monotonically increasing.  Make
                            # a note that this dimension will need
                            # flipping later
                            index = index[::-1]
                            flip.append(i)
                            step = -step
                        #--- End: if

                        if envelope:
                            # Create an envelope slice for a parsed
                            # index of a numpy array of integers
                            compressed_indices.append(index)

                            step = numpy_sign(step)
                            if step > 0:
                                stop = index[-1] + 1
                            else:
                                stop = index[-1] - 1
                                if stop < 0:
                                    stop = None
                                    
                            index = slice(index[0], stop, step)
                            is_slice = True
                else:
                    raise IndexError(
                        "Invalid indices {0} for array with shape {1}".format(
                            parsed_indices, shape))                
            #--- End: if
        #--- End: if
        
        if is_slice:
            if reverse and index.step < 0:              
                # If the slice step is negative, then transform
                # the original slice to a new slice with a
                # positive step such that the result of the new
                # slice is the reverse of the result of the
                # original slice.
                #
                # For example, if the original slice is
                # slice(6,0,-2) then the new slice will be
                # slice(2,7,2):
                #
                # >>> a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                # >>> a[slice(6, 0, -2)]
                # [6, 4, 2]
                # >>> a[slice(2, 7, 2)]
                # [2, 4, 6]
                # a[slice(6, 0, -2)] == list(reversed(a[slice(2, 7, 2)]))
                # True
                start, stop, step = index.indices(size)
                step    *= -1
                div, mod = divmod(start-stop-1, step)
                div_step = div*step
                start   -= div_step
                stop     = start + div_step + 1
                
                index = slice(start, stop, step)
                flip.append(i)         
            #--- End: if      

            # If step is greater than one then make sure that
            # index.stop isn't bigger than it needs to be
            if cyclic and index.step > 1:
                start, stop, step = index.indices(size)
                div, mod = divmod(stop-start-1, step)
                stop     = start + div*step + 1
                index    = slice(start, stop, step)
            #--- End: if      

            # 
            if envelope: 
                # Create an envelope slice for a parsed
                # index of a numpy array of integers                        
                compressed_indices.append(index)
                index = slice(start, stop, (1 if reverse else numpy_sign(step)))
        #--- End: if
                    
        parsed_indices[i] = index    
    #--- End: for

    if not (cyclic or reverse or envelope):
        return parsed_indices

    out = [parsed_indices]
    if cyclic:
        out.append(roll)
    if reverse:
        out.append(flip)
    if envelope:
        out.append(compressed_indices)
    return out
#--- End: def

def get_subspace(array, indices):
    '''

:Parameters:

    array : numpy array

    indices : list

Subset the input numpy array with the given indices. Indexing is similar to
that of a numpy array. The differences to numpy array indexing are:

1. An integer index i takes the i-th element but does not reduce the rank of
   the output array by one.

2. When more than one dimension's slice is a 1-d boolean array or 1-d sequence
   of integers then these indices work independently along each dimension
   (similar to the way vector subscripts work in Fortran).

indices must contain an index for each dimension of the input array.
'''
    gg = [i for i, x in enumerate(indices) if not isinstance(x, slice)]
    len_gg = len(gg)

    if len_gg < 2:
        # ------------------------------------------------------------
        # At most one axis has a list-of-integers index so we can do a
        # normal numpy subspace
        # ------------------------------------------------------------
        return array[tuple(indices)]

    else:
        # ------------------------------------------------------------
        # At least two axes have list-of-integers indices so we can't
        # do a normal numpy subspace
        # ------------------------------------------------------------
        if numpy_ma_isMA(array):
            take = numpy_ma_take
        else:
            take = numpy_take

        indices = indices[:]
        for axis in gg:
            array = take(array, indices[axis], axis=axis)
            indices[axis] = slice(None)
        #--- End: for

        if len_gg < len(indices):
            array = array[tuple(indices)]

        return array
    #--- End: if

#--- End: def

def set_subspace(array, indices, value):
    '''
'''
    gg = [i for i, x in enumerate(indices) if not isinstance(x, slice)]

    if len(gg) < 2: 
        # ------------------------------------------------------------
        # At most one axis has a list-of-integers index so we can do a
        # normal numpy assignment
        # ------------------------------------------------------------
        array[tuple(indices)] = value
    else:
        # ------------------------------------------------------------
        # At least two axes have list-of-integers indices so we can't
        # do a normal numpy assignment
        # ------------------------------------------------------------
        indices1 = indices[:]
        for i, x in enumerate(indices):
            if i in gg:
                y = []
                args = [iter(x)] * 2
                for start, stop in izip_longest(*args):
                    if not stop:
                        y.append(slice(start, start+1))
                    else:
                        step = stop - start
                        stop += 1
                        y.append(slice(start, stop, step))
                #--- End: for
                indices1[i] = y
            else:
                indices1[i] = (x,)
        #--- End: for
        
        if not numpy_ndim(value) :
            for i in itertools_product(*indices1):
                array[i] = value
                
        else:
            indices2 = []
            ndim_difference = array.ndim - numpy_ndim(value)
            for i, n in enumerate(numpy_shape(value)):
                if n == 1:
                    indices2.append((slice(None),))
                elif i + ndim_difference in gg:
                    y = []
                    start = 0
                    while start < n:
                        stop = start + 2
                        y.append(slice(start, stop))
                        start = stop
                    #--- End: while
                    indices2.append(y)
                else:
                    indices2.append((slice(None),))
            #--- End: for

            for i, j in izip(itertools_product(*indices1),
                             itertools_product(*indices2)):
                array[i] = value[j]
#--- End: def

def ATOL(*arg):
    '''

The value of absolute tolerance for testing numerically tolerant
equality.

.. seealso:: `cf.RTOL`

:Parameters:

    arg : int, optional
        The new value of absolute tolerance. The default is to not
        change the current value.

:Returns:

    out: `float`
        The value prior to the change, or the current value if no
        new value was specified.

:Examples:

>>> cf.ATOL()
1e-08
>>> old = cf.ATOL(1e-10)
>>> cf.ATOL(old)
1e-10
>>> cf.ATOL()
1e-08

'''
    old = CONSTANTS['ATOL']
    if arg:
        CONSTANTS['ATOL'] = arg[0]

    return old
#--- End: def

def RTOL(*arg):    
    '''

The value of relative tolerance for testing numerically
tolerant equality.

.. seealso:: `cf.ATOL`

:Parameters:

    arg : int, optional
        The new value of relative tolerance. The default is to not
        change the current value.

:Returns:

    out: `float`
        The value prior to the change, or the current value if no
        new value was specified.

:Examples:

>>> cf.RTOL()
1.0000000000000001e-05
>>> old = cf.RTOL(1e-10)
>>> cf.RTOL(old)
1e-10
>>> cf.RTOL()
1.0000000000000001e-05

'''
    old = CONSTANTS['RTOL']
    if arg:
        CONSTANTS['RTOL'] = arg[0]

    return old
#--- End: def

def equals(x, y, rtol=None, atol=None, ignore_fill_value=False,
           traceback=False):
    '''

True if and only if two objects are logically equal.

If the first argument, *x*, has an :meth:`equals` method then it is
used, and in this case ``equals(x, y)`` is equivalent to
``x.equals(y)``. Else if the second argument, *y*, has an
:meth:`equals` method then it is used, and in this case ``equals(x,
y)`` is equivalent to ``y.equals(x)``.

:Parameters:

    x, y :
        The objects to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    ignore_fill_value : bool, optional
        If True then `cf.Data` arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        objects differ.

:Returns: 

    out: `bool`
        Whether or not the two objects are equal.

:Examples:

>>> f
<CF Field: rainfall_rate(latitude(10), longitude(20)) kg m2 s-1>
>>> cf.equals(f, f)
True

>>> cf.equals(1.0, 1.0)
True
>>> cf.equals(1.0, 33)
False

>>> cf.equals('a', 'a')
True
>>> cf.equals('a', 'b')
False

>>> type(x), x.dtype
(<type 'numpy.ndarray'>, dtype('int64'))
>>> y = x.copy()
>>> cf.equals(x, y)
True
>>> cf.equals(x, x+1)
False

>>> class A(object):
...     pass
...
>>> a = A()
>>> b = A()
>>> cf.equals(a, a)
True
>>> cf.equals(a, b)
False

'''
    eq = getattr(x, 'equals', None)
    if callable(eq):
        # x has a callable equals method
        return eq(y, rtol=rtol, atol=atol,
                  ignore_fill_value=ignore_fill_value,
                  traceback=traceback)

    eq = getattr(y, 'equals', None)
    if callable(eq):
        # y has a callable equals method
        return eq(x, rtol=rtol, atol=atol,
                  ignore_fill_value=ignore_fill_value,
                  traceback=traceback)

    if isinstance(x, numpy_ndarray):
        if isinstance(y, numpy_ndarray):
            if x.shape != y.shape:
                return False

            if rtol is None:
                rtol = RTOL()
            if atol is None:
                atol = ATOL()
                    
            return _numpy_allclose(x, y, rtol=rtol, atol=atol)
        else:
            return False
    elif isinstance(y, numpy_ndarray):
        return False

    else:
        return x == y
#--- End: def

def set_equals(x, y, rtol=None, atol=None, ignore_fill_value=False,
               traceback=False):
    '''
'''    
    eq = getattr(x, 'set_equals', None)
    if callable(eq):
        # x has a callable set_equals method
        return eq(y, rtol=rtol, atol=atol,
                  ignore_fill_value=ignore_fill_value,
                  traceback=traceback)

    eq = getattr(y, 'set_equals', None)
    if callable(eq):
        # y has a callable set_equals method
        return eq(x, rtol=rtol, atol=atol,
                  ignore_fill_value=ignore_fill_value,
                  traceback=traceback)

    return equals(x, y, rtol=rtol, atol=atol,
                  ignore_fill_value=ignore_fill_value,
                  traceback=traceback)
#--- End: def

def equivalent(x, y, rtol=None, atol=None, traceback=False):
    '''

True if and only if two objects are logically equivalent.

If the first argument, *x*, has an `!equivalent` method then it is
used, and in this case ``equivalent(x, y)`` is the same as
``x.equivalent(y)``.

:Parameters:

    x, y :
        The objects to compare for equivalence.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        objects differ.

:Returns: 

    out: `bool`
        Whether or not the two objects are equivalent.

:Examples:

>>> f
<CF Field: rainfall_rate(latitude(10), longitude(20)) kg m2 s-1>
>>> cf.equivalent(f, f)
True

>>> cf.equivalent(1.0, 1.0)
True
>>> cf.equivalent(1.0, 33)
False

>>> cf.equivalent('a', 'a')
True
>>> cf.equivalent('a', 'b')
False

>>> cf.equivalent(cf.Data(1000, units='m'), cf.Data(1, units='km'))
True

For a field, ``f``:

>>> cf.equivalent(f, f.transpose())
True


'''

    if rtol is None:
        rtol = RTOL()
    if atol is None:
        atol = ATOL()

    eq = getattr(x, 'equivalent', None)
    if callable(eq):
        # x has a callable equivalent method
        return eq(y, rtol=rtol, atol=atol, traceback=traceback)

    eq = getattr(y, 'equivalent', None)
    if callable(eq):
        # y has a callable equivalent method
        return eq(x, rtol=rtol, atol=atol, traceback=traceback)

    return equals(x, y, rtol=rtol, atol=atol, ignore_fill_value=True,
                  traceback=traceback)
#--- End: def

def flat(x):
    '''

Return an iterator over an arbitrarily nested sequence.

:Parameters:

    x : scalar or arbitrarily nested sequence
        The arbitrarily nested sequence to be flattened. Note that a
        If *x* is a string or a scalar then this is equivalent to
        passing a single element sequence containing *x*.

:Returns:

    out: generator
        An iterator over flattened sequence.

:Examples:

>>> print cf.flat([1, [2, [3, 4]]])
<generator object flat at 0x3649cd0>

>>> print list(cf.flat([1, (2, [3, 4])]))
[1, 2, 3, 4]

>>> import numpy
>>> print list(cf.flat((1, [2, numpy.array([[3, 4], [5, 6]])]))
[1, 2, 3, 4, 5, 6]

>>> for a in cf.flat([1, [2, [3, 4]]]):
...     print a,
1 2 3 4

>>> for a in cf.flat(['a', ['bc', ['def', 'ghij']]]):
...     print a, ' ',
a bc def ghij

>>> for a in cf.flat(2004):
...     print a
2004

>>> for a in cf.flat('abcdefghij'):
...     print a
abcdefghij

>>> f
<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>
>>> for a in cf.flat(f):
...     print repr(a)
<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>

>>> for a in cf.flat([f, [f, [f, f]]]):
...     print repr(a)
<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>
<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>
<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>
<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>

>>> fl = cf.FieldList(cf.flat([f, [f, [f, f]]])
>>> fl
[<CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>,
 <CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>,
 <CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>,
 <CF Field: eastward_wind(air_pressure(5), latitude(110), longitude(106)) m s-1>]

'''
    if not isinstance(x, Iterable) or isinstance(x, basestring):
        x = (x,)

    for a in x:
        if not isinstance(a, basestring) and isinstance(a, Iterable):
            for sub in flat(a):
                yield sub
        else:
            yield a
#--- End: def

def pickle(x, filename, overwrite=False):
    '''

Write a binary pickled representation of an object to a file.

Note that Field and FieldList objects are picklable and their pickle
file size will be very small if their data arrays contain file
pointers as opposed to numpy arrays.

The pickling is equivalent to::

   import cPickle
   fh = open('file.pkl', 'wb')
   cPickle.dump(x, fh, 2)
   fh.close()

.. seealso:: `cf.unpickle`

:Parameters:

    x : 
        The object to be pickled.

    filename : str
        The name of the file in which to write the pickled
        representation of *x*.

    overwrite : bool, optional
        If True a pre-existing output file is over written. By default
        an exception is raised if the output file pre-exists.

:Returns:

    None

:Raises:

    IOError :
        If *overwrite* is False and the output file pre-exists.

    PickleError :
        If the object is not picklable.

:Examples:

For any picklable object, x:

>>> cf.pickle(x, 'file.pkl')
>>> y = cf.unpickle('file.pkl')
>>> cf.equals(x, y)
True

'''
    if not overwrite and os_path_isfile(filename):
        raise IOError(
            "Can't pickle to an existing file unless overwrite=True")

    fh = open(filename, 'wb')
    try:
        cPickle.dump(x, fh, 2)
    except:
        fh.close()
        raise cPickle.PickleError("Failed whilst pickling %s" % repr(x))

    fh.close()
#--- End: def

def unpickle(filename):
    '''

Return the reconstituted (unpickled) object from a binary pickle file.

Any binary pickle file may be used as input.

The unpickling is equivalent to::

   import cPickle
   fh = open('file.pkl', 'rb')
   x = cPickle.load(fh)
   fh.close()

.. seealso:: `cf.pickle`

:Parameters:

    filename : str
        The name of the file containing the pickled object.

:Returns:

    out: 
        The reconstituted object.

:Raises:

    UnpicklingError :
        If the file can not be unpickled. In particular, this might be
        raised when attempting to unpickle fields which were pickled
        with a different, incompatible version of cf.

:Examples:

For any picklable object, x:

>>> cf.pickle(x, 'file.pkl')
>>> y = cf.unpickle('file.pkl')
>>> cf.equals(x, y)
True

'''
    fh = open(filename, 'rb')

    try:
        x = cPickle.load(fh)
    except:
        # Failed unpickling can throw up any type of error, so trap
        # them all, but raise an informative UnpicklingError.
        fh.close()
        raise cPickle.UnpicklingError(
            "Failed whilst unpickling file '%s'" % filename)
    
    fh.close()
    return x
#--- End: def

_d = {'char': numpy_dtype('S1')}

def string_to_numpy_data_type(string):
    '''
'''

    try:
        return numpy_dtype(string)
    except TypeError:
        try:
            return _d[string]
        except KeyError:
            raise TypeError("asdasd  kkasdhahsjj734654376")
#--- End: def

def abspath(filename):
    '''

Return a normalized absolute version of a file name.

If a string containing URL is provided then it is returned unchanged.

.. seealso:: `cf.dirname`, `cf.pathjoin`, `cf.relpath`

:Parameters:

    filename: `str`
        The name of the file.

:Returns:

    out: `str`
        The normalized absolutized version of *filename*.
 
:Examples:

>>> import os
>>> os.getcwd()
'/data/archive'
>>> cf.abspath('file.nc')
'/data/archive/file.nc'
>>> cf.abspath('..//archive///file.nc')
'/data/archive/file.nc'
>>> cf.abspath('http://data/archive/file.nc')
'http://data/archive/file.nc'

'''
    u = urlparse_urlparse(filename)
    if u.scheme != '':
        return filename

    return os_path_abspath(filename)
#--- End: def

def relpath(filename, start=None):
    '''

Return a relative filepath to a file.

The filepath is relative either from the current directory or from an
optional start point.

If a string containing URL is provided then it is returned unchanged.

.. seealso:: `cf.abspath`, `cf.dirname`, `cf.pathjoin`

:Parameters:

    filename: `str`
        The name of the file.

    start: `str`, optional
        The start point for the relative path. By default the current
        directoty is used.

:Returns:

    out: `str`
        The relative path.

:Examples:

>>> cf.relpath('/data/archive/file.nc')
'../file.nc'
>>> cf.relpath('/data/archive///file.nc', start='/data')
'archive/file.nc'
>>> cf.relpath('http://data/archive/file.nc')
'http://data/archive/file.nc'

'''
    u = urlparse_urlparse(filename)
    if u.scheme != '':
        return filename

    if start is not None:
        return os_path_relpath(filename, start)

    return os_path_relpath(filename)
#--- End: def

def dirname(filename):
    '''

Return the directory name of a file.

If a string containing URL is provided then everything up to, but not
including, the last slash (/) is returned.

.. seealso:: `cf.abspath`, `cf.pathjoin`, `cf.relpath`

:Parameters:

    filename: `str`
        The name of the file.

:Returns:

    out: `str`
        The directory name.

:Examples:

>>> cf.dirname('/data/archive/file.nc')
'/data/archive'
>>> cf.dirname('..//file.nc')
'..'
>>> cf.dirname('http://data/archive/file.nc')
'http://data/archive'

'''
    u = urlparse_urlparse(filename)
    if u.scheme != '':
        return filename.rpartition('/')[0]

    return os_path_dirname(filename)
#--- End: def

def pathjoin(path1, path2):
    '''

Join two file path components intelligently.

If either of the paths is a URL then a URL will be returned

.. seealso:: `cf.abspath`, `cf.dirname`, `cf.relpath`

:Parameters:

    path1: `str`
        The first component of the path.

    path2: `str`
        The second component of the path.

:Returns:

    out: `str`
        The joined paths.

:Examples:

>>> cf.pathjoin('/data/archive', '../archive/file.nc')
'/data/archive/../archive/file.nc'
>>> cf.pathjoin('/data/archive', '../archive/file.nc')
'/data/archive/../archive/file.nc'
>>> cf.abspath(cf.pathjoin('/data/', 'archive/')
'/data/archive'
>>> cf.pathjoin('http://data', 'archive/file.nc')
'http://data/archive/file.nc'

'''
    u = urlparse_urlparse(path1)
    if u.scheme != '':
        return urlparse_urljoin(path1, path2)

    return os_path_join(path1, path2)
#--- End: def

def hash_array(array):
    '''

Return the hash value of a numpy array.

The hash value is dependent on the data type, shape of the data
array. If the array is a masked array then the hash value is
independent of the fill value and of data array values underlying any
masked elements.

The hash value is not guaranteed to be portable across versions of
Python, numpy and cf.

:Parameters:

    array: `numpy.ndarray`
        The numpy array to be hashed. May be a masked array.

:Returns:

    out: `int`
        The hash value

:Examples:

>>> print array
[[0 1 2 3]]
>>> cf.hash_array(array)
-8125230271916303273
>>> array[1, 0] = numpy.ma.masked
>>> print array
[[0 -- 2 3]]
>>> cf.hash_array(array)
791917586613573563
>>> array.hardmask = False
>>> array[0, 1] = 999
>>> array[0, 1] = numpy.ma.masked
>>> cf.hash_array(array)
791917586613573563
>>> array.squeeze()
>>> print array
[0 -- 2 3]
>>> cf.hash_array(array)
-7007538450787927902
>>> array.dtype = float
>>> print array
[0.0 -- 2.0 3.0]
>>> cf.hash_array(array)
-4816859207969696442

'''
    h = hashlib_md5()
    
    h_update = h.update
    
    h_update(marshal_dumps(array.dtype.name))
    h_update(marshal_dumps(array.shape))
    
    if numpy_ma_isMA(array):        
        if numpy_ma_is_masked(array):
            mask = array.mask
            if not mask.flags.c_contiguous:               
                mask = numpy_ascontiguousarray(mask)

            h_update(mask)
            array = array.copy()
            array.set_fill_value()
            array = array.filled()
        else:
            array = array.data
    #--- End: if

    if not array.flags.c_contiguous:               
#        array = array.copy()
        array = numpy_ascontiguousarray(array)
        
    h_update(array)
    
    return hash(h.digest())
#--- End: def

def inspect(self):
    '''

Inspect the attributes of an object.

:Returns: 

    out: `str`

:Examples:

>>> print x.inspect
<CF CoordinateReference: rotated_latitude_longitude>
----------------------------------------------------
_dict: {'grid_north_pole_latitude': 38.0, 'grid_north_pole_longitude': 190.0}
coord_terms: set([])
coords: set(['dim2', 'dim1', 'aux2', 'aux3'])
name: 'rotated_latitude_longitude'
ncvar: 'rotated_latitude_longitude'
type: 'grid_mapping'

'''
    name = repr(self)
    out = [name, ''.ljust(len(name), '-')]
    
    if hasattr(self, '__dict__'):
        for key, value in sorted(self.__dict__.items()):
            out.append('%s: %s' % (key, repr(value)))
        
    return '\n'.join(out)
#--- End: def

def broadcast_array(array, shape):
    '''

Broadcast an array to a given shape.
    
It is assumed that ``numpy.ndim(array) <= len(shape)`` and that the
array is broadcastable to the shape by the normal numpy broadcasting
rules, but neither of these things is checked.
    
For example, ``a[...] = broadcast_array(a, b.shape)`` is equivalent to
``a[...] = b``.
    
:Parameters:
  
    a: numpy array-like
    
    shape: `tuple`
    
:Returns:

    out: `numpy.ndarray`
    
:Examples:


>>> a = numpy.arange(8).reshape(2, 4)
[[0 1 2 3]
 [4 5 6 7]]

>>> print cf.broadcast_array(a, (3, 2, 4))
[[[0 1 2 3]
  [4 5 6 0]]

 [[0 1 2 3]
  [4 5 6 0]]

 [[0 1 2 3]
  [4 5 6 0]]]

>>> a = numpy.arange(8).reshape(2, 1, 4)
[[[0 1 2 3]]

 [[4 5 6 7]]]

>>> print cf.broadcast_array(a, (2, 3, 4))
[[[0 1 2 3]
  [0 1 2 3]
  [0 1 2 3]]

 [[4 5 6 7]
  [4 5 6 7]
  [4 5 6 7]]]

>>> a = numpy.ma.arange(8).reshape(2, 4)
>>> a[1, 3] = numpy.ma.masked
>>> print a
[[0 1 2 3]
 [4 5 6 --]]

>>> cf.broadcast_array(a, (3, 2, 4))
[[[0 1 2 3]
  [4 5 6 --]]

 [[0 1 2 3]
  [4 5 6 --]]

 [[0 1 2 3]
  [4 5 6 --]]]

'''
    a_shape = numpy_shape(array)
    if a_shape == shape:
        return array

    tile = [(m if n == 1 else 1)
            for n, m in zip(a_shape[::-1], shape[::-1])]
    tile = shape[0:len(shape)-len(a_shape)] + tuple(tile[::-1])
    
    return numpy_tile(array, tile)
#--- End: def

def allclose(x, y, rtol=None, atol=None):
    '''

Returns True if two broadcastable arrays have equal values to within
numerical tolerance, False otherwise.

The tolerance values are positive, typically very small numbers. The
relative difference (``rtol * abs(b)``) and the absolute difference
``atol`` are added together to compare against the absolute difference
between ``a`` and ``b``.

:Parameters:

    x, y: array_like
        Input arrays to compare.

    atol: `float`, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol: `float`, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

:Returns:

    out: `bool`
        Returns True if the arrays are equal, otherwise False.

:Examples:

'''    
    if rtol is None:
        rtol = RTOL()
    if atol is None:
        atol = ATOL()

    allclose = getattr(x, 'allclose', None)
    if callable(allclose):
        # x has a callable allclose method
       return allclose(y, rtol=rtol, atol=atol)

    allclose = getattr(y, 'allclose', None)
    if callable(allclose):
        # y has a callable allclose method
       return allclose(x, rtol=rtol, atol=atol)

    # x nor y has a callable allclose method
    return _numpy_allclose(x, y, rtol=rtol, atol=atol)
#--- End: def

def _section(o, axes=None, data=False, stop=None, chunks=False,
             min_step=1, **kwargs):
    '''Return a list of m dimensional sections of a Field of n dimensions or
a dictionary of m dimensional sections of a Data object of n
dimensions, where m <= n. In the case of a Data object the keys of the
dictionary are the indicies of the sections in the original Data
object. The m dimensions that are not sliced are marked with None as a
placeholder making it possible to reconstruct the original data
object. The corresponding values are the resulting sections of type
`cf.Data`.

:Parameters:

    axes: *optional*
        In the case of a Field this is a query for the m axes that
        define the sections of the Field as accepted by the Field
        object's axes method. The keyword arguments are also passed to
        this method. See `cf.Field.axes` for details. If an axis is
        returned that is not a data axis it is ignored, since it is
        assumed to be a dimension coordinate of size 1. In the case of
        a Data object this should be a tuple or a list of the m
        indices of the m axes that define the sections of the Data
        object. If axes is None (the default) all axes are selected.
    
    data: `bool`, optional
        If True this indicates that a data object has been passed, if
        False it indicates that a field object has been passed. By
        default it is False.

    stop: `int`, optional
        Stop after taking this number of sections and return. If stop
        is None all sections are taken.
    
    chunks: `bool`, optional
        If True return sections that are of the maximum possible size
        that will fit in one chunk of memory instead of sectioning
        into slices of size 1 along the dimensions that are being
        sectioned.
    
    min_step: `int`, optional
        The minimum step size when making chunks. By default this is
        1. Can be set higher to avoid size 1 dimensions, which are
        problematic for bilinear regridding.

:Returns:

    out: `list` or `dict`
        The list of m dimensional sections of the Field or the
        dictionary of m dimensional sections of the Data object.

:Examples:

Section a field into 2D longitude/time slices, checking the units:

>>> _section(f, {None: 'longitude', units: 'radians'},
...             {None: 'time',
...              'units': 'days since 2006-01-01 00:00:00'})

Section a field into 2D longitude/latitude slices, requiring exact
names:

>>> _section(f, ['latitude', 'longitude'], exact=True)

    '''
    
    # retrieve the index of each axis defining the sections
    if data:
        if axes == None:
            axis_indices = range(o.ndim)
        else:
            axis_indices = axes
    else:
        axis_keys = o.axes(axes, **kwargs)
        axis_indices = list()
        for key in axis_keys:
            try:
                axis_indices.append(o.data_axes().index(key))
            except ValueError:
                pass
        #--- End: for
    #--- End: if
    
    # find the size of each dimension
    sizes = o.shape
    
    if chunks:
        steps = list(sizes)
        
        # Define the factor which, when multiplied by the size of the
        # data array, determines how many chunks are in the data array.
        factor = (o.dtype.itemsize + 1.0)/CHUNKSIZE()
        
        # n_chunks = number of equal sized bits the partition
        #            needs to be split up into so that each bit's
        #            size is less than ther chunk size.
        n_chunks = int(math_ceil(o.size*factor))
        
        for (index, axis_size) in enumerate(sizes):
            if int(math_ceil(float(axis_size)/min_step)) <= n_chunks:
                n_chunks = int(math_ceil(n_chunks/float(axis_size)*min_step))
                steps[index] = min_step
                
            else:
                steps[index] = int(axis_size/n_chunks)                
                break
        #--- End: for
    else:
        steps = [1] * len(sizes)
    
    # use recursion to slice out each 2D horizontal section
    if data:
        d = dict()
    else:
        fl = []
    
    indices = [slice(None)] * len(sizes)
    
    nl_vars = {'count': 0}
    def loop_over_index(current_index):
        # Expects an index to loop over in the list indices. If this is less
        # than 0 the horizontal slice defined by indices is appended to the
        # FieldList fl, if it is the specified axis indices the value in
        # indices is left as slice(None) and it calls itself recursively with
        # the next index, otherwise each index is looped over. In this loop
        # the routine is called recursively with the next index. If the count
        # of the number of slices taken is greater than or equal to stop
        # it returns before taking any more slices.
        
        if current_index < 0:
            if data:
                d[tuple([x.start for x in indices])] = o[tuple(indices)]
            else:
                fl.append(o[tuple(indices)])

            nl_vars['count'] += 1
            return
        #--- End: if
        
        if current_index in axis_indices:
            loop_over_index(current_index - 1)
            return
        
        for i in range(0, sizes[current_index], steps[current_index]):
            if not stop is None and nl_vars['count'] >= stop:
                return
            indices[current_index] = slice(i, i + steps[current_index])
            loop_over_index(current_index - 1)
        #--- End: for
    #--- End: def
    
    current_index = len(sizes) - 1
    loop_over_index(current_index)
    
    if data:
        return d
    else:
        return fl
#--- End: def

def environment(display=True):
    '''Return the names and versions of cf-python dependencies.

:Parameters:

    display: `bool`, optional
        If False then return the description of the environment as a
        string. By default the description is printed.

:Returns:

    out: `None` or `str`
        If *display* is True then the description of the environment
        is printed and `None` is returned. Otherwise the description
        is returned as a string.

:Examples:

>>> cf.environment()
Platform: Linux-4.4.0-53-generic-x86_64-with-debian-stretch-sid
HDF5 library: 1.8.17
netcdf library: 4.4.1
python: 2.7.13 /home/space/anaconda2/bin/python
netCDF4: 1.2.4 /home/space/anaconda2/lib/python2.7/site-packages/netCDF4/__init__.pyc
numpy: 1.11.3 /home/space/anaconda2/lib/python2.7/site-packages/numpy/__init__.pyc
psutil: 5.0.1 /home/space/anaconda2/lib/python2.7/site-packages/psutil/__init__.pyc
matplotlib: 1.5.1 /home/space/anaconda2/lib/python2.7/site-packages/matplotlib/__init__.pyc
ESMF: 7.0.0 /home/space/anaconda2/lib/python2.7/site-packages/ESMF/__init__.pyc
cfplot: 2.1.10 /home/space/anaconda2/lib/python2.7/site-packages/cfplot/__init__.pyc
cf: 2.0.2 /home/space/cf-python/cf/__init__.pyc

    '''
    out = []
    out.append('Platform: ' + str(platform()))
    out.append('HDF5 library: ' + str(netCDF4. __hdf5libversion__))
    out.append('netcdf library: ' + str(netCDF4.__netcdf4libversion__))
    out.append('python: ' + str(python_version() + ' ' + str(sys_executable)))
    out.append('netCDF4: ' + str(netCDF4.__version__) + ' ' + str(os_path_abspath(netCDF4.__file__)))
    out.append('numpy: ' + str(numpy__version__) + ' ' + str(os_path_abspath(numpy__file__)))
    out.append('psutil: ' + str(psutil.__version__) + ' ' + str(os_path_abspath(psutil.__file__)))

    try:
        import matplotlib
    except:
        out.append('matplotlib: not available')
    else:
        out.append('matplotlib: ' + str(matplotlib.__version__) + ' ' + str(os_path_abspath(matplotlib.__file__)))

    try:
        import ESMF
    except:
        out.append('ESMF: not available')
    else:
        out.append('ESMF: ' + str(ESMF.__version__) + ' ' + str(os_path_abspath(ESMF.__file__)))

    try:
        import cfplot
    except ImportError:
        out.append('cfplot: not available')
    else:
        out.append('cfplot: ' + str(cfplot.__version__) + ' ' + str(os_path_abspath(cfplot.__file__)))
            
    out.append('cf: ' + str(__version__) + ' ' + str(os_path_abspath(__file__)))
    
    out = '\n'.join(out)

    if display:
        print out
    else:
        return out
#--- End: def
