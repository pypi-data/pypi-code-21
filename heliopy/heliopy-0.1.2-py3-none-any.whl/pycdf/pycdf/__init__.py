#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This package provides a Python interface to the Common Data Format (CDF)
library used for many NASA missions, available at http://cdf.gsfc.nasa.gov/.
It is targeted at Python 2.6+ and should work without change on either
Python 2 or Python 3.

The interface is intended to be 'pythonic' rather than reproducing the
C interface. To open or close a CDF and access its variables, see the :class:`CDF`
class. Accessing data within the variables is via the :class:`Var`
class. The :data:`lib` object provides access to some routines
that affect the functionality of the library in general. The
:mod:`~spacepy.pycdf.const` module contains constants useful for accessing
the underlying library.


The CDF C library must be properly installed in order to use this package.
The CDF distribution provides scripts meant to be called in a user's
login scripts, ``definitions.B`` for bash and ``definitions.C`` for C-shell
derivatives. (See the installation instructions which come with the CDF library.)
These will set environment variables specifying the location
of the library; pycdf will respect these variables if they are set. Otherwise
it will search the standard system library path and the default installation
locations for the CDF library.

If pycdf has trouble finding the library, try setting ``CDF_LIB`` before importing
the module, e.g. if the library is in ``CDF/lib`` in the user's home directory:

>>> import os
>>> os.environ["CDF_LIB"] = "~/CDF/lib"
>>> from spacepy import pycdf

If this works, make the environment setting permanent. Note that on OSX,
using plists to set the environment may not carry over to Python terminal
sessions; use ``.cshrc`` or ``.bashrc`` instead.

Authors: Jon Niehof

Institution: University of New Hampshire

Contact: Jonathan.Niehof@unh.edu


Copyright 2010-2015 Los Alamos National Security, LLC.

"""

__contact__ = 'Jon Niehof, Jonathan.Niehof@unh.edu'

import collections
import ctypes
import ctypes.util
import datetime
import operator
import os
import os.path
import shutil
import sys
import tempfile
import warnings
import weakref

import numpy
import numpy.ma
from pycdf import datamodel

#Import const AFTER library loaded, so failed load doesn't leave half-imported
#from pycdf import const

try:
    str_classes = (str, bytes, unicode)
except NameError:
    str_classes = (str, bytes)


class Library(object):
    """
    Abstraction of the base CDF C library and its state.

    Not normally intended for end-user use. An instance of this class
    is created at package load time as the :data:`~spacepy.pycdf.lib` variable, providing
    access to the underlying C library if necessary. The CDF library itself
    is described in section 2.1 of the CDF user's guide, as well as the CDF
    C reference manual.

    Calling the C library directly requires knowledge of
    :mod:`ctypes`.

    Instantiating this object loads the C library, see :doc:`/pycdf` docs
    for details.

    .. autosummary::

        ~Library.call
        ~Library.check_status
        ~Library.datetime_to_epoch
        ~Library.datetime_to_epoch16
        ~Library.datetime_to_tt2000
        ~Library.epoch_to_datetime
        ~Library.epoch_to_epoch16
        ~Library.epoch_to_num
        ~Library.epoch_to_tt2000
        ~Library.epoch16_to_datetime
        ~Library.epoch16_to_epoch
        ~Library.epoch16_to_tt2000
        ~Library.set_backward
        supports_int8
        ~Library.tt2000_to_datetime
        ~Library.tt2000_to_epoch
        ~Library.tt2000_to_epoch16
        v_datetime_to_epoch
        v_datetime_to_epoch16
        v_datetime_to_tt2000
        v_epoch_to_datetime
        v_epoch_to_tt2000
        v_epoch16_to_datetime
        v_epoch16_to_tt2000
        v_tt2000_to_datetime
        v_tt2000_to_epoch
        v_tt2000_to_epoch16
        libpath
        version

    .. automethod:: call
    .. automethod:: check_status
    .. automethod:: datetime_to_epoch
    .. automethod:: datetime_to_epoch16
    .. automethod:: datetime_to_tt2000
    .. automethod:: epoch_to_datetime
    .. automethod:: epoch_to_epoch16
    .. automethod:: epoch_to_num
    .. automethod:: epoch_to_tt2000
    .. automethod:: epoch16_to_datetime
    .. automethod:: epoch16_to_epoch
    .. automethod:: epoch16_to_tt2000
    .. automethod:: set_backward

    .. attribute:: supports_int8

       True if this library supports INT8 and TIME_TT2000 types; else False.

    .. automethod:: tt2000_to_datetime
    .. automethod:: tt2000_to_epoch
    .. automethod:: tt2000_to_epoch16

    .. method:: v_datetime_to_epoch(datetime)

        A vectorized version of :meth:`datetime_to_epoch` which takes a
        numpy array of datetimes as input and returns an array of epochs.

    .. method:: v_datetime_to_epoch16(datetime)

        A vectorized version of :meth:`datetime_to_epoch16` which takes a
        numpy array of datetimes as input and returns an array of epoch16.

    .. method:: v_datetime_to_tt2000(datetime)

        A vectorized version of :meth:`datetime_to_tt2000` which takes a
        numpy array of datetimes as input and returns an array of TT2000.

    .. method:: v_epoch_to_datetime(epoch)

        A vectorized version of :meth:`epoch_to_datetime` which takes a
        numpy array of epochs as input and returns an array of datetimes.

    .. method:: v_epoch_to_tt2000(epoch)

        A vectorized version of :meth:`epoch_to_tt2000` which takes a
        numpy array of epochs as input and returns an array of tt2000s.

    .. method:: v_epoch16_to_datetime(epoch0, epoch1)

        A vectorized version of :meth:`epoch16_to_datetime` which takes
        a numpy array of epoch16 as input and returns an array of datetimes.
        An epoch16 is a pair of doubles; the input array's last dimension
        must be two (and the returned array will have one fewer dimension).

    .. method:: v_epoch16_to_tt2000(epoch16)

        A vectorized version of :meth:`epoch16_to_tt2000` which takes
        a numpy array of epoch16 as input and returns an array of tt2000s.
        An epoch16 is a pair of doubles; the input array's last dimension
        must be two (and the returned array will have one fewer dimension).

    .. method:: v_tt2000_to_datetime(tt2000)

        A vectorized version of :meth:`tt2000_to_datetime` which takes
        a numpy array of tt2000 as input and returns an array of datetimes.

    .. method:: v_tt2000_to_epoch(tt2000)

        A vectorized version of :meth:`tt2000_to_epoch` which takes
        a numpy array of tt2000 as input and returns an array of epochs.

    .. method:: v_tt2000_to_epoch16(tt2000)

        A vectorized version of :meth:`tt2000_to_epoch16` which takes
        a numpy array of tt2000 as input and returns an array of epoch16.

    .. attribute:: libpath

       The path where pycdf found the CDF C library, potentially useful in
       debugging. If this contains just the name of a file (with no path
       information), then the system linker found the library for pycdf.
       On Linux, ``ldconfig -p`` may be useful for displaying the system's
       library resolution.

    .. attribute:: version

       Version of the CDF library, (version, release, increment, subincrement)
    """
    def __init__(self, libpath=None, library=None):
        """Load the CDF C library.

        Searches for the library in the order:
            1. Appropriately-named file in CDF_LIB
            2. Appropriately-named file in CDF_BASE
            3. Standard library search path
        @raise CDFError: BAD_DATA_TYPE if can't map types properly
        """

        if not 'CDF_TMP' in os.environ:
            os.environ['CDF_TMP'] = tempfile.gettempdir()

        if not library:
            if not libpath:
                self._library, self.libpath = self._find_lib()
            else:
                self._library = ctype.CDLL(libpath)
                self.libpath = libpath
        else:
            self._library = library
            self.libpath = libpath
        self._library.CDFlib.restype = ctypes.c_long #commonly used, so set it up here
        self._library.EPOCHbreakdown.restype = ctypes.c_long
        self._library.computeEPOCH.restype = ctypes.c_double
        self._library.computeEPOCH.argtypes = [ctypes.c_long] * 7
        self._library.computeEPOCH16.restype = ctypes.c_double
        self._library.computeEPOCH16.argtypes = [ctypes.c_long] * 10 + \
            [ctypes.POINTER(ctypes.c_double * 2)]
        if hasattr(self._library, 'CDFsetFileBackward'):
            self._library.CDFsetFileBackward.restype = None
            self._library.CDFsetFileBackward.argtypes = [ctypes.c_long]
        if hasattr(self._library, 'CDF_TT2000_from_UTC_parts'):
            self._library.CDF_TT2000_from_UTC_parts.restype = ctypes.c_longlong
            self._library.CDF_TT2000_from_UTC_parts.argtypes = \
                [ctypes.c_double] *9
        if hasattr(self._library, 'CDF_TT2000_to_UTC_parts'):
            self._library.CDF_TT2000_to_UTC_parts.restype = None
            self._library.CDF_TT2000_to_UTC_parts.argtypes = \
                [ctypes.c_longlong] + [ctypes.POINTER(ctypes.c_double)] * 9
        if hasattr(self._library, 'CDF_TT2000_to_UTC_EPOCH'):
            self._library.CDF_TT2000_to_UTC_EPOCH.restype = ctypes.c_double
            self._library.CDF_TT2000_to_UTC_EPOCH.argtypes = [ctypes.c_longlong]
        if hasattr(self._library, 'CDF_TT2000_from_UTC_EPOCH'):
            self._library.CDF_TT2000_from_UTC_EPOCH.restype = ctypes.c_longlong
            self._library.CDF_TT2000_from_UTC_EPOCH.argtypes = [ctypes.c_double]
        if hasattr(self._library, 'CDF_TT2000_to_UTC_EPOCH16'):
            self._library.CDF_TT2000_to_UTC_EPOCH16.restype = None
            self._library.CDF_TT2000_to_UTC_EPOCH16.argtypes = \
                [ctypes.c_longlong, ctypes.POINTER(ctypes.c_double * 2)]
        if hasattr(self._library, 'CDF_TT2000_from_UTC_EPOCH16'):
            self._library.CDF_TT2000_from_UTC_EPOCH16.restype = \
                ctypes.c_longlong
            self._library.CDF_TT2000_from_UTC_EPOCH16.argtypes = \
                [ctypes.POINTER(ctypes.c_double * 2)]

        #Get CDF version information
        ver = ctypes.c_long(0)
        rel = ctypes.c_long(0)
        inc = ctypes.c_long(0)
        sub = ctypes.c_char(b' ')
        self.call(const.GET_, const.LIB_VERSION_, ctypes.byref(ver),
                  const.GET_, const.LIB_RELEASE_, ctypes.byref(rel),
                  const.GET_, const.LIB_INCREMENT_, ctypes.byref(inc),
                  const.GET_, const.LIB_subINCREMENT_, ctypes.byref(sub))
        ver = ver.value
        rel = rel.value
        inc = inc.value
        sub = sub.value
        self.version = (ver, rel, inc, sub)
        self._del_middle_rec_bug = ver < 3 or (ver == 3 and
                                               (rel < 4 or
                                                (rel == 4 and inc < 1)))
        self.supports_int8 = (ver > 3 or (ver == 3 and rel >=4))

        self.cdftypenames = {const.CDF_BYTE.value: 'CDF_BYTE',
                             const.CDF_CHAR.value: 'CDF_CHAR',
                             const.CDF_INT1.value: 'CDF_INT1',
                             const.CDF_UCHAR.value: 'CDF_UCHAR',
                             const.CDF_UINT1.value: 'CDF_UINT1',
                             const.CDF_INT2.value: 'CDF_INT2',
                             const.CDF_UINT2.value: 'CDF_UINT2',
                             const.CDF_INT4.value: 'CDF_INT4',
                             const.CDF_UINT4.value: 'CDF_UINT4',
                             const.CDF_INT8.value: 'CDF_INT8',
                             const.CDF_FLOAT.value: 'CDF_FLOAT',
                             const.CDF_REAL4.value: 'CDF_REAL4',
                             const.CDF_DOUBLE.value: 'CDF_DOUBLE',
                             const.CDF_REAL8.value: 'CDF_REAL8',
                             const.CDF_EPOCH.value: 'CDF_EPOCH',
                             const.CDF_EPOCH16.value: 'CDF_EPOCH16',
                             const.CDF_TIME_TT2000.value: 'CDF_TIME_TT2000',
                             }
        self.numpytypedict = {const.CDF_BYTE.value: numpy.int8,
                              const.CDF_CHAR.value: numpy.int8,
                              const.CDF_INT1.value: numpy.int8,
                              const.CDF_UCHAR.value: numpy.uint8,
                              const.CDF_UINT1.value: numpy.uint8,
                              const.CDF_INT2.value: numpy.int16,
                              const.CDF_UINT2.value: numpy.uint16,
                              const.CDF_INT4.value: numpy.int32,
                              const.CDF_UINT4.value: numpy.uint32,
                              const.CDF_INT8.value: numpy.int64,
                              const.CDF_FLOAT.value: numpy.float32,
                              const.CDF_REAL4.value: numpy.float32,
                              const.CDF_DOUBLE.value: numpy.float64,
                              const.CDF_REAL8.value: numpy.float64,
                              const.CDF_EPOCH.value: numpy.float64,
                              const.CDF_EPOCH16.value:
                              numpy.dtype((numpy.float64, 2)),
                              const.CDF_TIME_TT2000.value: numpy.int64,
                              }
        self.timetypes = [const.CDF_EPOCH.value,
                          const.CDF_EPOCH16.value,
                          const.CDF_TIME_TT2000.value]
        if not self.supports_int8:
            del self.cdftypenames[const.CDF_INT8.value]
            del self.numpytypedict[const.CDF_INT8.value]
            del self.cdftypenames[const.CDF_TIME_TT2000.value]
            del self.numpytypedict[const.CDF_TIME_TT2000.value]

        v_epoch16_to_datetime = numpy.frompyfunc(
            self.epoch16_to_datetime, 2, 1)
        self.v_epoch16_to_datetime = \
            lambda x: v_epoch16_to_datetime(x[..., 0], x[..., 1])
        self.v_epoch_to_datetime = numpy.frompyfunc(
            self.epoch_to_datetime, 1, 1)
        self.v_tt2000_to_datetime = numpy.frompyfunc(
            self.tt2000_to_datetime, 1, 1)
        self.v_datetime_to_epoch = numpy.vectorize(
            self.datetime_to_epoch, otypes=[numpy.float64])
        v_datetime_to_epoch16 = numpy.frompyfunc(
            self.datetime_to_epoch16, 1, 2)
        #frompyfunc returns a TUPLE of the returned values,
        #implicitly the 0th dimension. We want everything from one
        #call paired, so this rolls the 0th dimension to the last
        #(via the second-to-last)
        def _v_datetime_to_epoch16(x):
            retval = numpy.require(v_datetime_to_epoch16(x),
                                      dtype=numpy.float64)
            if len(retval.shape) > 1:
                return numpy.rollaxis(
                    numpy.rollaxis(retval, 0, -1),
                    -1, -2)
            else:
                return retval
        self.v_datetime_to_epoch16 = _v_datetime_to_epoch16
        self.v_datetime_to_tt2000 = numpy.vectorize(
            self.datetime_to_tt2000, otypes=[numpy.int64])
        self.v_epoch_to_tt2000 = numpy.vectorize(
            self.epoch_to_tt2000, otypes=[numpy.int64])
        self.v_tt2000_to_epoch = numpy.vectorize(
            self.tt2000_to_epoch, otypes=[numpy.float64])
        v_epoch16_to_tt2000 = numpy.frompyfunc(
            self.epoch16_to_tt2000, 2, 1)
        self.v_epoch16_to_tt2000 = \
            lambda x: v_epoch16_to_tt2000(x[..., 0], x[..., 1])
        v_tt2000_to_epoch16 = numpy.frompyfunc(
            self.tt2000_to_epoch16, 1, 2)
        #frompyfunc returns a TUPLE of the returned values,
        #implicitly the 0th dimension. We want everything from one
        #call paired, so this rolls the 0th dimension to the last
        #(via the second-to-last)
        def _v_tt2000_to_epoch16(x):
            retval = numpy.require(v_tt2000_to_epoch16(x),
                                      dtype=numpy.float64)
            if len(retval.shape) > 1:
                return numpy.rollaxis(
                    numpy.rollaxis(retval, 0, -1),
                    -1, -2)
            else:
                return retval
        self.v_tt2000_to_epoch16 = _v_tt2000_to_epoch16
        if not self.supports_int8:
            self.datetime_to_tt2000 = self._bad_tt2000
            self.tt2000_to_datetime = self._bad_tt2000
            self.v_datetime_to_tt2000 = self._bad_tt2000
            self.v_tt2000_to_datetime = self._bad_tt2000
            self.epoch_to_tt2000 = self._bad_tt2000
            self.v_epoch_to_tt2000 = self._bad_tt2000
            self.tt2000_to_epoch = self._bad_tt2000
            self.v_tt2000_to_epoch = self._bad_tt2000
            self.epoch_16_to_tt2000 =  self._bad_tt2000
            self.v_epoch16_to_tt2000 = self._bad_tt2000
            self.tt2000_to_epoch16 = self._bad_tt2000
            self.v_tt2000_to_epoch16 = self._bad_tt2000

        #Default to V2 CDF
        self.set_backward(True)

    @staticmethod
    def _find_lib():
        """
        Search for the CDF library
        """
        failed = []
        for libpath in Library._lib_paths():
            try:
                lib = ctypes.CDLL(libpath)
            except:
                failed.append(libpath)
            else:
                return libpath, lib
        raise Exception(('Cannot load CDF C library from {0}.'
                        'Try os.environ["CDF_LIB"] = library_directory '
                        'before import.').format(', '.join(failed)))

    @staticmethod
    def _lib_paths():
        """Find candidate paths for the CDF library

        Does not check that the library is actually in any particular directory,
        just returns a list of possible locations, in priority order.

        Returns
        =======
        out : generator of str
            paths that look like the CDF library
        """
        #What the library might be named
        names = { 'win32': ['dllcdf.dll'],
                  'darwin': ['libcdf.dylib', 'cdf.dylib', 'libcdf.so'],
                  'linux2': ['libcdf.so'],
                  'linux': ['libcdf.so'],
                  }
        names = names.get(sys.platform, ['libcdf.so'])
        #All existing CDF-library-like paths within a directory
        search_dir = lambda x: \
            [os.path.join(x, fname) for fname in names
             if os.path.exists(os.path.join(x, fname))]
        #Search the environment-specified places first
        if 'CDF_LIB' in os.environ:
            for p in search_dir(os.environ['CDF_LIB']):
                yield p
        if 'CDF_BASE' in os.environ:
            for p in search_dir(os.path.join(os.environ['CDF_BASE'], 'lib')):
                yield p
        ctypespath = ctypes.util.find_library(
            'dllcdf.dll' if sys.platform == 'win32' else 'cdf')
        if ctypespath:
            yield ctypespath
        #LD_LIBRARY_PATH specifies runtime library search paths
        if 'LD_LIBRARY_PATH' in os.environ:
            for d in os.environ['LD_LIBRARY_PATH'].split(os.pathsep):
                for p in search_dir(d):
                    yield p
        #Finally, defaults places CDF gets installed uner
        #CDF_BASE is usually a subdir of these (with "cdf" in the name)
        #Searched in order given here!
        cdfdists = { 'win32': ['c:\\CDF Distribution\\'],
                    'darwin': ['/Applications/', '/usr/local/',
                               os.path.expanduser('~')],
                    'linux2': ['/usr/local/', os.path.expanduser('~')],
                    'linux': ['/usr/local/', os.path.expanduser('~')],
                    }
        if sys.platform in cdfdists:
            for cdfdist in cdfdists[sys.platform]:
                if os.path.isdir(cdfdist):
                    cand = []
                    for d in os.listdir(cdfdist):
                        if d[0:3].lower() == 'cdf':
                            #checking src in case BUILT but not INSTALLED
                            for subdir in ['lib', os.path.join('src', 'lib')]:
                                libdir = os.path.join(cdfdist, d, subdir)
                                if os.path.isdir(libdir):
                                    cand.append(libdir)
                    #Sort reverse, so new versions are first FOR THIS cdfdist
                    for d in sorted(cand)[::-1]:
                        for p in search_dir(d):
                            yield p

    def check_status(self, status, ignore=()):
        """
        Raise exception or warning based on return status of CDF call

        Parameters
        ==========
        status : int
            status returned by the C library

        Other Parameters
        ================
        ignore : sequence of ctypes.c_long
            CDF statuses to ignore. If any of these is returned by CDF library,
            any related warnings or exceptions will *not* be raised.
            (Default none).

        Raises
        ======
        CDFError : if status < CDF_WARN, indicating an error

        Warns
        =====
        CDFWarning : if CDF_WARN <= status < CDF_OK, indicating a warning.

        Returns
        =======
        out : int
            status (unchanged)
        """
        if status == const.CDF_OK or status in ignore:
            return status
        if status < const.CDF_WARN:
            raise CDFError(status)
        else:
            warning = CDFWarning(status)
            warning.warn()
            return status

    def call(self, *args, **kwargs):
        """
        Call the CDF internal interface

        Passes all parameters directly through to the CDFlib routine of the
        CDF library's C internal interface. Checks the return value with
        :meth:`check_status`.

        Terminal NULL is automatically added to args.

        Parameters
        ==========
        args : various, see :mod:`ctypes`
            Passed directly to the CDF library interface. Useful
            constants are defined in the :mod:`~pycdf.const` module.

        Other Parameters
        ================
        ignore : sequence of CDF statuses
            sequence of CDF statuses to ignore. If any of these
            is returned by CDF library, any related warnings or
            exceptions will *not* be raised.

        Returns
        =======
        out : int
            CDF status from the library

        Raises
        ======
        CDFError : if CDF library reports an error

        Warns
        =====
        CDFWarning : if CDF library reports a warning
        """
        if 'ignore' in kwargs:
            return self.check_status(self._library.CDFlib(
                *(args + (const.NULL_, ))
                ), kwargs['ignore'])
        else:
            return self.check_status(self._library.CDFlib(
                *(args + (const.NULL_, ))
                ))

    def set_backward(self, backward=True):
        """
        Set backward compatibility mode for new CDFs

        Unless backward compatible mode is set, CDF files created by
        the version 3 library can not be read by V2.

        Parameters
        ==========
        backward : boolean
            Set backward compatible mode if True; clear it if False.

        Raises
        ======
        ValueError : if backward=False and underlying CDF library is V2
        """
        if self.version[0] < 3:
            if not backward:
                raise ValueError(
                    'Cannot disable backward-compatible mode for CDF version 2.')
            else:
                return
        self._library.CDFsetFileBackward(const.BACKWARDFILEon if backward
                                         else const.BACKWARDFILEoff)

    def epoch_to_datetime(self, epoch):
        """
        Converts a CDF epoch value to a datetime

        Parameters
        ==========
        epoch : float
            epoch value from CDF

        Returns
        =======
        out : :class:`datetime.datetime`
            date and time corresponding to epoch. Invalid values are set to
            usual epoch invalid value, i.e. last moment of year 9999.

        See Also
        ========
        v_epoch_to_datetime
        """
        yyyy = ctypes.c_long(0)
        mm = ctypes.c_long(0)
        dd = ctypes.c_long(0)
        hh = ctypes.c_long(0)
        min = ctypes.c_long(0)
        sec = ctypes.c_long(0)
        msec = ctypes.c_long(0)
        self._library.EPOCHbreakdown(ctypes.c_double(epoch),
                                     ctypes.byref(yyyy), ctypes.byref(mm),
                                     ctypes.byref(dd),
                                     ctypes.byref(hh), ctypes.byref(min),
                                     ctypes.byref(sec), ctypes.byref(msec))
        if yyyy.value <= 0:
            return datetime.datetime(9999, 12, 13, 23, 59, 59, 999000)
        else:
            return datetime.datetime(yyyy.value, mm.value, dd.value,
                                     hh.value, min.value, sec.value,
                                     msec.value * 1000)

    def datetime_to_epoch(self, dt):
        """
        Converts a Python datetime to a CDF Epoch value

        Parameters
        ==========
        dt : :class:`datetime.datetime`
            date and time to convert

        Returns
        =======
        out : float
            epoch corresponding to dt

        See Also
        ========
        v_datetime_to_epoch
        """
        if dt.tzinfo != None and dt.utcoffset() != None:
            dt = dt - dt.utcoffset()
        dt.replace(tzinfo=None)
        micro = dt.microsecond % 1000
        if micro >= 500 and dt.year < 9999:
            dt += datetime.timedelta(0, 0, 1000)
        return self._library.computeEPOCH(dt.year, dt.month, dt.day, dt.hour,
                                          dt.minute, dt.second,
                                          int(dt.microsecond / 1000))

    def epoch16_to_datetime(self, epoch0, epoch1):
        """
        Converts a CDF epoch16 value to a datetime

        .. note::
            The call signature has changed since SpacePy 0.1.2. Formerly
            this method took a single argument with two values; now it
            requires two arguments (one for each value). To convert existing
            code, replace ``epoch16_to_datetime(epoch)`` with
            ``epoch16_to_datetime(*epoch)``.

        Parameters
        ==========
        epoch0 : float
            epoch16 value from CDF, first half
        epoch1 : float
            epoch16 value from CDF, second half

        Raises
        ======
        EpochError : if input invalid

        Returns
        =======
        out : :class:`datetime.datetime`
            date and time corresponding to epoch. Invalid values are set to
            usual epoch invalid value, i.e. last moment of year 9999.

        See Also
        ========
        v_epoch16_to_datetime
        """
        yyyy = ctypes.c_long(0)
        mm = ctypes.c_long(0)
        dd = ctypes.c_long(0)
        hh = ctypes.c_long(0)
        min = ctypes.c_long(0)
        sec = ctypes.c_long(0)
        msec = ctypes.c_long(0)
        usec = ctypes.c_long(0)
        nsec = ctypes.c_long(0)
        psec = ctypes.c_long(0)
        self._library.EPOCH16breakdown((ctypes.c_double * 2)(epoch0, epoch1),
                                     ctypes.byref(yyyy), ctypes.byref(mm),
                                     ctypes.byref(dd),
                                     ctypes.byref(hh), ctypes.byref(min),
                                     ctypes.byref(sec), ctypes.byref(msec),
                                     ctypes.byref(usec), ctypes.byref(nsec),
                                     ctypes.byref(psec))
        if yyyy.value <= 0:
            return datetime.datetime(9999, 12, 13, 23, 59, 59, 999999)
        micro = int(float(msec.value) * 1000 + float(usec.value) +
                    float(nsec.value) / 1000 + float(psec.value) / 1e6 + 0.5)
        if micro < 1000000:
            return datetime.datetime(yyyy.value, mm.value, dd.value,
                                     hh.value, min.value, sec.value,
                                     micro)
        else:
            add_sec = int(micro / 1000000)
            try:
                return datetime.datetime(yyyy.value, mm.value, dd.value,
                                         hh.value, min.value, sec.value,
                                         micro - add_sec * 1000000) + \
                                         datetime.timedelta(seconds=add_sec)
            except OverflowError:
                return datetime.datetime(datetime.MAXYEAR, 12, 31,
                                         23, 59, 59,
                                         999999)

    def datetime_to_epoch16(self, dt):
        """
        Converts a Python datetime to a CDF Epoch16 value

        Parameters
        ==========
        dt :  :class:`datetime.datetime`
            date and time to convert

        Returns
        =======
        out : list of float
            epoch16 corresponding to dt

        See Also
        ========
        v_datetime_to_epoch16
        """
        if dt.tzinfo != None and dt.utcoffset() != None:
            dt = dt - dt.utcoffset()
        dt.replace(tzinfo=None)
        epoch16 = (ctypes.c_double * 2)(0.0, 0.0)
        self._library.computeEPOCH16(dt.year, dt.month, dt.day, dt.hour,
                                     dt.minute, dt.second,
                                     int(dt.microsecond / 1000),
                                     dt.microsecond % 1000, 0, 0,
                                     epoch16)
        return (epoch16[0], epoch16[1])

    def epoch_to_epoch16(self, epoch):
        """
        Converts a CDF EPOCH to a CDF EPOCH16 value

        Parameters
        ==========
        epoch : double
            EPOCH to convert. Lists and numpy arrays are acceptable.

        Returns
        =======
        out : (double, double)
            EPOCH16 corresponding to epoch
        """
        e = numpy.require(epoch, numpy.float64)
        s = numpy.trunc(e / 1000.0)
        #ugly numpy stuff, probably a better way....
        res = numpy.hstack((s, (e - s * 1000.0) * 1e9))
        if len(res) <= 2:
            return res
        newshape = list(res.shape[0:-2])
        newshape.append(res.shape[-1] // 2)
        newshape.append(2)
        return numpy.rollaxis(res.reshape(newshape), -1, -2)

    def epoch_to_num(self, epoch):
        """
        Convert CDF EPOCH to matplotlib number.

        Same output as :func:`~matplotlib.dates.date2num` and useful for
        plotting large data sets without converting the times through datetime.

        Parameters
        ==========
        epoch : double
            EPOCH to convert. Lists and numpy arrays are acceptable.

        Returns
        =======
        out : double
            Floating point number representing days since 0001-01-01.
        """
        #date2num day 1 is 1/1/1 00UT
        #epoch 1/1/1 00UT is 31622400000.0 (millisecond)
        return (epoch - 31622400000.0) / (24 * 60 * 60 * 1000.0) + 1.0

    def epoch16_to_epoch(self, epoch16):
        """
        Converts a CDF EPOCH16 to a CDF EPOCH value

        Parameters
        ==========
        epoch16 : (double, double)
            EPOCH16 to convert. Lists and numpy arrays are acceptable.
            LAST dimension should be 2: the two pairs of EPOCH16

        Returns
        =======
        out : double
            EPOCH corresponding to epoch16
        """
        e = numpy.require(epoch16, numpy.float64)
        return e[..., 0] * 1000.0 + numpy.round(e[..., 1] / 1e9)

    def tt2000_to_datetime(self, tt2000):
        """
        Converts a CDF TT2000 value to a datetime

        .. note::
            Although TT2000 values support leapseconds, Python's datetime
            object does not. Any times after 23:59:59.999999 will
            be truncated to 23:59:59.999999.


        Parameters
        ==========
        tt2000 : int
            TT2000 value from CDF

        Raises
        ======
        EpochError : if input invalid

        Returns
        =======
        out : :class:`datetime.datetime`
            date and time corresponding to epoch. Invalid values are set to
            usual epoch invalid value, i.e. last moment of year 9999.

        See Also
        ========
        v_tt2000_to_datetime
        """
        yyyy = ctypes.c_double(0)
        mm = ctypes.c_double(0)
        dd = ctypes.c_double(0)
        hh = ctypes.c_double(0)
        min = ctypes.c_double(0)
        sec = ctypes.c_double(0)
        msec = ctypes.c_double(0)
        usec = ctypes.c_double(0)
        nsec = ctypes.c_double(0)
        self._library.CDF_TT2000_to_UTC_parts(
            ctypes.c_longlong(tt2000),
            ctypes.byref(yyyy), ctypes.byref(mm), ctypes.byref(dd),
            ctypes.byref(hh), ctypes.byref(min), ctypes.byref(sec),
            ctypes.byref(msec), ctypes.byref(usec), ctypes.byref(nsec))
        if yyyy.value <= 0:
            return datetime.datetime(9999, 12, 13, 23, 59, 59, 999999)
        sec = int(sec.value)
        if sec >= 60:
            return datetime.datetime(
                int(yyyy.value), int(mm.value), int(dd.value),
                int(hh.value), int(min.value), 59, 999999)
        micro = int(msec.value * 1000 + usec.value + nsec.value / 1000 + 0.5)
        if micro < 1000000:
            return datetime.datetime(
                int(yyyy.value), int(mm.value), int(dd.value),
                int(hh.value), int(min.value), sec, micro)
        else:
            add_sec = int(micro / 1000000)
            try:
                return datetime.datetime(
                    int(yyyy.value), int(mm.value), int(dd.value),
                    int(hh.value), int(min.value), sec,
                    micro - add_sec * 1000000) + \
                    datetime.timedelta(seconds=add_sec)
            except OverflowError:
                return datetime.datetime(datetime.MAXYEAR, 12, 31,
                                         23, 59, 59, 999999)

    def datetime_to_tt2000(self, dt):
        """
        Converts a Python datetime to a CDF TT2000 value

        Parameters
        ==========
        dt :  :class:`datetime.datetime`
            date and time to convert

        Returns
        =======
        out : int
            tt2000 corresponding to dt

        See Also
        ========
        v_datetime_to_tt2000
        """
        if dt.tzinfo != None and dt.utcoffset() != None:
            dt = dt - dt.utcoffset()
        dt.replace(tzinfo=None)
        return self._library.CDF_TT2000_from_UTC_parts(
            dt.year, dt.month, dt.day, dt.hour,
            dt.minute, dt.second,
            int(dt.microsecond / 1000),
            dt.microsecond % 1000, 0)

    def epoch_to_tt2000(self, epoch):
        """
        Converts a CDF EPOCH to a CDF TT2000 value

        Parameters
        ==========
        epoch : double
            EPOCH to convert

        Returns
        =======
        out : int
            tt2000 corresponding to epoch

        See Also
        ========
        v_epoch_to_tt2000
        """
        return self._library.CDF_TT2000_from_UTC_EPOCH(epoch)

    def tt2000_to_epoch(self, tt2000):
        """
        Converts a CDF TT2000 value to a CDF EPOCH

        .. note::
            Although TT2000 values support leapseconds, CDF EPOCH values
            do not. Times during leapseconds are rounded up to beginning
            of the next day.


        Parameters
        ==========
        tt2000 : int
            TT2000 value from CDF

        Raises
        ======
        EpochError : if input invalid

        Returns
        =======
        out : double
            EPOCH corresponding to the TT2000 input time

        See Also
        ========
        v_tt2000_to_epoch
        """
        return self._library.CDF_TT2000_to_UTC_EPOCH(tt2000)

    def epoch16_to_tt2000(self, epoch0, epoch1):
        """
        Converts a CDF epoch16 value to TT2000

        .. note::
            Because TT2000 does not support picoseconds, the picoseconds
            value in epoch is ignored (i.e., truncated.)

        Parameters
        ==========
        epoch0 : float
            epoch16 value from CDF, first half
        epoch1 : float
            epoch16 value from CDF, second half

        Raises
        ======
        EpochError : if input invalid

        Returns
        =======
        out : long
            TT2000 corresponding to epoch.

        See Also
        ========
        v_epoch16_to_tt2000
        """
        return self._library.CDF_TT2000_from_UTC_EPOCH16(
            (ctypes.c_double * 2)(epoch0, epoch1))

    def tt2000_to_epoch16(self, tt2000):
        """
        Converts a CDF TT2000 value to a CDF EPOCH16

        .. note::
            Although TT2000 values support leapseconds, CDF EPOCH16 values
            do not. Times during leapseconds are rounded up to beginning
            of the next day.

        Parameters
        ==========
        tt2000 : int
            TT2000 value from CDF

        Raises
        ======
        EpochError : if input invalid

        Returns
        =======
        out : double, double
            EPOCH16 corresponding to the TT2000 input time

        See Also
        ========
        v_tt2000_to_epoch16
        """
        epoch16 = numpy.empty((2,), dtype=numpy.float64)
        self._library.CDF_TT2000_to_UTC_EPOCH16(
            tt2000, numpy.ctypeslib.as_ctypes(epoch16))
        #without this, vectorized version breaks
        str(epoch16)
        return (epoch16[0], epoch16[1])

    def _bad_tt2000(*args, **kwargs):
        """Convenience function for complaining that TT2000 not supported"""
        raise NotImplementedError(
            'TT2000 functions require CDF library 3.4.0 or later')


try:
    _libpath, _library = Library._find_lib()
except:
    if 'sphinx' in sys.argv[0]:
        warnings.warn('CDF library did not load. '
                      'You appear to be building docs, so ignoring this error.')
    else:
        raise
from . import const
lib = Library(_libpath, _library)
"""Module global library object.

Initalized at module load time so all classes have ready
access to the CDF library and a common state. E.g:
    >>> from spacepy import pycdf
    >>> pycdf.lib.version
        (3, 3, 0, ' ')
"""


class CDFException(Exception):
    """
    Base class for errors or warnings in the CDF library.

    Not normally used directly, but in subclasses :class:`CDFError`
    and :class:`CDFWarning`.

    Error messages provided by this class are looked up from the underlying
    C library.
    """
    def __init__(self, status):
        """
        Create a CDF Exception

        Uses CDF C library to look up an appropriate error message.

        Parameters
        ==========
        status : ctypes.c_long
            CDF status
        """
        self.status = status
        self.string = 'CDF error ' + repr(status) + ', unable to get details.'
        message = ctypes.create_string_buffer(const.CDF_STATUSTEXT_LEN + 1)
        try:
            retval = lib._library.CDFlib(const.SELECT_, const.CDF_STATUS_,
                                         ctypes.c_long(status),
                                         const.GET_, const.STATUS_TEXT_, message,
                                         const.NULL_)
            if retval == const.CDF_OK:
                if isinstance(message.value, str):
                    self.string = message.value
                elif isinstance(message.value, bytes):
                    self.string = message.value.decode()
        except:
            pass

    def __str__(self):
        """
        Error string associated with the library error.

        Returns
        =======
        out : str
            Error message from the CDF library.
        """
        return self.string


class CDFError(CDFException):
    """Raised for an error in the CDF library."""
    pass


class CDFWarning(CDFException, UserWarning):
    """Used for a warning in the CDF library."""

    def warn(self, level=4):
        """
        Issues a warning based on the information stored in my exception

        Intended for use in check_status or similar wrapper function.

        Other Parameters
        ================
        level : int
            optional (default 3), how far up the stack the warning should
            be reported. Passed directly to :class:`warnings.warn`.
        """
        warnings.warn(self, self.__class__, level)


class EpochError(Exception):
    """Used for errors in epoch routines"""
    pass


def _compress(obj, comptype=None, param=None):
    """Set or check the compression of a :py:class:`pycdf.CDF` or :py:class:`pycdf.Var`

    @param obj: object on which to set or check compression
    @type obj: :py:class:`pycdf.CDF` or :py:class:`pycdf.Var`
    @param comptype: type of compression to change to, see CDF C reference
                     manual section 4.10. Constants for this parameter
                     are in :py:mod:`pycdf.const`. If not specified, will not change
                     compression.
    @type comptype: ctypes.c_long
    @param param: Compression parameter, see CDF CRM 4.10 and :py:mod:`pycdf.const`.
                  If not specified, will choose reasonable default (5 for
                  gzip; other types have only one possible parameter.)
    @type param: ctypes.c_long
    @return: (comptype, param) currently in effect
    @rtype: tuple
    """
    if isinstance(obj, CDF):
        COMPRESSION_ = const.CDF_COMPRESSION_
    elif isinstance(obj, Var):
        COMPRESSION_ = const.zVAR_COMPRESSION_
    else:
        raise ValueError('Must specify a CDF or Var type.')

    validparams = {const.NO_COMPRESSION.value: [ctypes.c_long(0)],
                   const.RLE_COMPRESSION.value: [const.RLE_OF_ZEROs],
                   const.HUFF_COMPRESSION.value:
                       [const.OPTIMAL_ENCODING_TREES],
                   const.AHUFF_COMPRESSION.value:
                       [const.OPTIMAL_ENCODING_TREES],
                   const.GZIP_COMPRESSION.value: [ctypes.c_long(5),
                                                  ctypes.c_long(1),
                                                  ctypes.c_long(2),
                                                  ctypes.c_long(3),
                                                  ctypes.c_long(4),
                                                  ctypes.c_long(6),
                                                  ctypes.c_long(7),
                                                  ctypes.c_long(8),
                                                  ctypes.c_long(9),
                                                  ],
                   }
    comptypes = [const.NO_COMPRESSION, const.RLE_COMPRESSION,
                 const.HUFF_COMPRESSION, const.AHUFF_COMPRESSION,
                 const.GZIP_COMPRESSION]
    comptypevalues = [i.value for i in comptypes]

    if comptype != None:
        if not hasattr(comptype, 'value'):
            comptype = ctypes.c_long(comptype)
        if param is None:
            if not comptype.value in validparams:
                raise CDFError(const.BAD_COMPRESSION)
            param = validparams[comptype.value][0]
        paramlist = (ctypes.c_long * 1)(param)
        obj._call(const.PUT_, COMPRESSION_,
                   comptype, paramlist)
    params = (ctypes.c_long *
              const.CDF_MAX_PARMS)(*([0] * const.CDF_MAX_PARMS))
    comptype = ctypes.c_long(0)
    percent = ctypes.c_long(0)
    obj._call(const.GET_, COMPRESSION_,
               ctypes.byref(comptype), ctypes.byref(params),
               ctypes.byref(percent))
    param = params[0]
    if not comptype.value in comptypevalues:
        raise CDFError(const.BAD_COMPRESSION)
    validparamvalues = [i.value for i in validparams[comptype.value]]
    if not param in validparamvalues:
        raise CDFError(const.BAD_COMPRESSION_PARM)
    comptype = comptypes[comptypevalues.index(comptype.value)]
    if comptype in (const.RLE_COMPRESSION, const.HUFF_COMPRESSION,
                    const.AHUFF_COMPRESSION):
        param = validparams[comptype.value][validparamvalues.index(param)]
    return (comptype, param)


class CDF(collections.MutableMapping):
    """
    Python object representing a CDF file.

    Open or create a CDF file by creating an object of this class.

    Parameters
    ==========
    pathname : string
        name of the file to open or create
    masterpath : string
        name of the master CDF file to use in creating
        a new file. If not provided, an existing file is
        opened; if provided but evaluates to ``False``
        (e.g., ``''``), an empty new CDF is created.

    Raises
    ======
    CDFError
        if CDF library reports an error

    Warns
    =====
    CDFWarning
        if CDF library reports a warning and interpreter
        is set to error on warnings.

    Examples
    ========
    Open a CDF by creating a CDF object, e.g.:

        >>> cdffile = pycdf.CDF('cdf_filename.cdf')

    Be sure to :meth:`close` or :meth:`save` when
    done.

    .. note::
        Existing CDF files are opened read-only by default, see
        :meth:`readonly` to change.

    CDF supports the `with
    <http://docs.python.org/tutorial/inputoutput.html#methods-of-file-objects>`_
    keyword, like other file objects, so:

        >>> with pycdf.CDF('cdf_filename.cdf') as cdffile:
        ...     #do brilliant things with the CDF

    will open the CDF, execute the indented statements, and close the CDF when
    finished or when an error occurs. The `python docs
    <http://docs.python.org/reference/compound_stmts.html#with>`_ include more
    detail on this 'context manager' ability.

    CDF objects behave like a python `dictionary
    <http://docs.python.org/tutorial/datastructures.html#dictionaries>`_,
    where the keys are names of variables in the CDF, and the values,
    :class:`Var` objects. As a dictionary, they are also `iterable
    <http://docs.python.org/tutorial/classes.html#iterators>`_ and it is easy
    to loop over all of the variables in a file. Some examples:

        #. List the names of all variables in the open CDF ``cdffile``:

               >>> cdffile.keys()
               >>> for k in cdffile: #Alternate
               ...     print(k)

        #. Get a :class:`Var` object for the variable named ``Epoch``:

               >>> epoch = cdffile['Epoch']

        #. Determine if a CDF contains a variable named ``B_GSE``:

               >>> if 'B_GSE' in cdffile:
               ...     print('B_GSE is in the file')
               ... else:
               ...     print('B_GSE is not in the file')

        #. Find how many variables are in the file:

               >>> print(len(cdffile))

        #. Delete the variable ``Epoch`` from the open CDF file ``cdffile``:

              >>> del cdffile['Epoch']

        #. Display a summary of variables and types in open CDF file ``cdffile``:

              >>> print(cdffile)

        #. Open the CDF named ``cdf_filename.cdf``, read *all* the data from
           all variables into dictionary ``data``, and close it when done or
           if an error occurs:

               >>> with pycdf.CDF('cdf_filename.cdf') as cdffile:
               ...     data = cdffile.copy()


    This last example can be very inefficient as it reads the entire CDF.
    Normally it's better to treat the CDF as a dictionary and access only
    the data needed, which will be pulled transparently from disc. See
    :class:`Var` for more subtle examples.

    Potentially useful dictionary methods and related functions:

      - `in <http://docs.python.org/reference/expressions.html#in>`_
      - `keys <http://docs.python.org/tutorial/datastructures.html#dictionaries>`_
      - :py:func:`len`
      - `list comprehensions
        <http://docs.python.org/tutorial/datastructures.html#list-comprehensions>`_
      - :py:func:`sorted`
      - :py:func:`~spacepy.toolbox.dictree`

    The CDF user's guide section 2.2 has more background information on CDF
    files.

    The :attr:`~CDF.attrs` Python attribute acts as a dictionary
    referencing CDF attributes (do not confuse the two); all the
    dictionary methods above also work on the attribute dictionary.
    See :class:`gAttrList` for more on the dictionary of global
    attributes.

    Creating a new CDF from a master (skeleton) CDF has similar syntax to
    opening one:

        >>> cdffile = pycdf.CDF('cdf_filename.cdf', 'master_cdf_filename.cdf')

    This creates and opens ``cdf_filename.cdf`` as a copy of
    ``master_cdf_filename.cdf``.

    Using a skeleton CDF is recommended over making a CDF entirely from
    scratch, but this is possible by specifying a blank master:

        >>> cdffile = pycdf.CDF('cdf_filename.cdf', '')

    When CDFs are created in this way, they are opened read-write, see
    :py:meth:`readonly` to change.

    By default, new CDFs (without a master) are created in version 2
    (backward-compatible) format. To create a version 3 CDF, use
    :meth:`Library.set_backward`:

        >>> pycdf.lib.set_backward(False)
        >>> cdffile = pycdf.CDF('cdf_filename.cdf', '')

    Add variables by direct assignment, which will automatically set type
    and dimension based on the data provided:

        >>> cdffile['new_variable_name'] = [1, 2, 3, 4]

    or, if more control is needed over the type and dimensions, use
    :py:meth:`new`.

    .. autosummary::

        ~CDF.attrs
        ~CDF.backward
        ~CDF.checksum
        ~CDF.clone
        ~CDF.close
        ~CDF.col_major
        ~CDF.compress
        ~CDF.copy
        ~CDF.from_data
        ~CDF.new
        ~CDF.raw_var
        ~CDF.readonly
        ~CDF.save
        ~CDF.version

    .. attribute:: CDF.attrs

       Global attributes for this CDF in a dict-like format.
       See :class:`gAttrList` for details.

    .. attribute:: CDF.backward

       True if this CDF was created in backward-compatible mode
       (for opening with CDF library before 3.x)

    .. automethod:: checksum
    .. automethod:: clone
    .. automethod:: close
    .. automethod:: col_major
    .. automethod:: compress
    .. automethod:: copy
    .. automethod:: from_data
    .. automethod:: new
    .. automethod:: raw_var
    .. automethod:: readonly
    .. automethod:: save
    .. automethod:: version
    """
    def __init__(self, pathname, masterpath=None):
        """Open or create a CDF file.

        Parameters
        ==========
        pathname : string
            name of the file to open or create
        masterpath : string
            name of the master CDF file to use in creating
            a new file. If not provided, an existing file is
            opened; if provided but evaluates to ``False``
            (e.g., ``''``), an empty new CDF is created.

        Raises
        ======
        CDFError
            if CDF library reports an error
        CDFWarning
            if CDF library reports a warning and interpreter
            is set to error on warnings.

        Examples
        ========
        Open a CDF by creating a CDF object, e.g.:
            >>> cdffile = pycdf.CDF('cdf_filename.cdf')
        Be sure to :py:meth:`pycdf.CDF.close` or :py:meth:`pycdf.CDF.save`
        when done.
        """
        try:
            self.pathname = pathname.encode()
        except AttributeError:
            raise ValueError(
                'pathname must be string-like: {0}'.format(pathname))
        self._handle = ctypes.c_void_p(None)
        self._opened = False
        if masterpath is None:
            self._open()
        elif masterpath:
            self._from_master(masterpath.encode())
        else:
            self._create()
        lib.call(const.SELECT_, const.CDF_zMODE_, ctypes.c_long(2))
        self._attrlistref = weakref.ref(gAttrList(self))
        self.backward = self.version()[0] < 3

    def __del__(self):
        """Destructor; called when CDF object is destroyed.

        Close CDF file if there is still a valid handle.
        .. note::
            To avoid data loss, explicitly call :py:meth:`pycdf.CDF.close`
            or :py:meth:`pycdf.CDF.save`.
        """
        if self._opened:
            self.close()

    def __delitem__(self, name):
        """Delete a zVariable in this CDF, by name or number

        Parameters
        ==========
        name : string or int
            Name or number of the CDF variable
        .. note:
            Variable numbers may change if variables are added or removed.

        Examples
        ========
        Delete the variable ``Epoch`` from the open CDF file ``cdffile``.
            >>> del cdffile['Epoch']
        """
        self[name]._delete()

    def __enter__(self):
        """Context manager entrance function."""
        return self

    def __exit__(self, type, value, traceback):
        """Context manager exit function.

        Close CDF file.
        """
        self.close()

    def __getitem__(self, name):
        """Gets a zVariable in this CDF, by name or number

        The CDF acts like a dict

        @param name: Name or number of the CDF variable
        @type name: string or int
        @return: CDF variable named or numbered L{name}
        @rtype: :py:class:`pycdf.Var`
        @raise KeyError: for pretty much any problem in lookup
        @note: variable numbers may change if variables are added or removed.
        """
        try:
            return Var(self, name)
        except CDFException as e:
            raise KeyError('{0}: {1}'.format(name, e))

    def __setitem__(self, name, data):
        """Writes data to a zVariable in this CDF

        If the zVariable does not exist, will create one matching
        L{data}. If it does exist, will attempt to write L{data}
        to it without changing the type or dimensions.

        @param name: name or number of the variable to write
        @type name: str or int
        @param data: data to write, or a :py:class:`pycdf.Var` to copy
        """
        if isinstance(data, Var):
            self.clone(data, name)
        elif name in self:
            self[name][...] = data
            if hasattr(data, 'attrs'):
                self[name].attrs.clone(data.attrs)
        else:
            self.new(name, data)

    def __iter__(self, current = 0):
        """Iterates over zVars in CDF

        Iterators for dicts return keys
        @note: Returned in variable-number order
        """
        while current < self.__len__():
            name = self[current].name()
            value = (yield name)
            if value is None:
                current += 1
            else:
                current = self[value]._num()
                current += 1

    def __len__(self):
        """Implements 'length' of CDF (number of zVars)

        @return: number of zVars in the CDF
        @rtype: int
        """
        count = ctypes.c_long(0)
        self._call(const.GET_, const.CDF_NUMzVARS_, ctypes.byref(count))
        return count.value

    def __contains__(self, key):
        """Determines whether a particular variable name is in the CDF

        @note: Essentially an efficiency function; L{__iter__} is called
               if this isn't defined
        @param key: key/variable name to check
        @type key: string
        @return: True if L{key} is the name of a variable in CDF, else False
        @rtype: Boolean
        """
        try:
            foo = self[key]
            return True
        except KeyError as e:
            expected = str(key) + \
               ": NO_SUCH_VAR: Named variable not found in this CDF."
            if expected in e.args:
                return False
            raise

    def __repr__(self):
        """Returns representation of CDF

        Cannot return anything that can be eval'd to create a copy of the
        CDF, so just wrap the informal representation in angle brackets.
        @return: all the data in this list of attributes
        @rtype: str
        """
        return '<CDF:\n' + str(self) + '\n>'

    def __str__(self):
        """Returns a string representation of the CDF

        This is an 'informal' representation in that it cannot be evaluated
        directly to create a :py:class:`pycdf.CDF`, just the names, types, and sizes of all
        variables. (Attributes are not listed.)

        @return: description of the variables in the CDF
        @rtype: str
        """
        if self._opened:
            return '\n'.join([key + ': ' + str(value)
                              for (key, value) in sorted(self.items())])
            #can get away with this sort because second value in tuple isn't
            #compared unless first are different, and variable name is unique.
        else:
            if isinstance(self.pathname, str):
                return 'Closed CDF {0}'.format(self.pathname)
            else:
                return 'Closed CDF {0}'.format(self.pathname.decode('ascii'))

    def _open(self):
        """Opens the CDF file (called on init)

        Will open an existing CDF file read/write.

        Raises
        ======
        CDFError : if CDF library reports an error
        CDFWarning : if CDF library reports a warning and interpreter
                     is set to error on warnings.
        .. note:
            Not intended for direct call; pass parameters to
            :py:class:`pycdf.CDF` constructor.
        """

        lib.call(const.OPEN_, const.CDF_, self.pathname, ctypes.byref(self._handle))
        self._opened = True
        self.readonly(True)

    def _create(self):
        """Creates (and opens) a new CDF file

        Created at ``pathname``.
        Assumes zero-dimension r variables

        Raises
        ======
        CDFError : if CDF library reports an error
        CDFWarning : if CDF library reports a warning and interpreter
                     is set to error on warnings.
        .. note:
            Not intended for direct call; pass parameters to
            :py:class:`pycdf.CDF` constructor.
        """

        lib.call(const.CREATE_, const.CDF_, self.pathname, ctypes.c_long(0),
                              (ctypes.c_long * 1)(0), ctypes.byref(self._handle))
        self._opened = True

    def _from_master(self, master_path):
        """Creates a new CDF from a master CDF file

        ``master_path`` is copied to ``pathname`` and opened.

        Parameters
        ==========
        master_path : string
            location of the master CDF file

        Raises
        ======
        CDFError : if CDF library reports an error
        CDFWarning : if CDF library reports a warning and interpreter
                     is set to error on warnings.
        .. note:
            Not intended for direct call; pass parameters to
            :py:class:`pycdf.CDF` constructor.
        """

        if os.path.exists(self.pathname):
            raise CDFError(const.CDF_EXISTS)
        shutil.copy2(master_path, self.pathname)
        self._open()
        self._opened = True
        self.readonly(False)

    @classmethod
    def from_data(cls, filename, sd):
        """Create a new CDF file from a SpaceData object or similar

        The CDF named ``filename`` is created, opened, filled with the
        contents of ``sd`` (including attributes), and closed.

        ``sd`` should be a dictionary-like object; each key will be made
        into a variable name. An attribute called ``attrs``, if it exists,
        will be made into global attributes for the CDF.

        Each value of ``sd`` should be array-like and will be used as
        the contents of the variable; an attribute called ``attrs``, if
        it exists, will be made into attributes for that variable.

        Parameters
        ----------
        filename : string
            name of the file to create
        sd : datamodel.SpaceData
            data to put in the CDF. This structure cannot be nested,
            i.e., it must contain only :class:`~datamodel.dmarray`
            and no :class:`~datamodel.Spacedata` objects.
        """
        with cls(filename, '') as cdffile:
            for k in sd:
                cdffile[k] = sd[k]
            cdffile.attrs.clone(sd.attrs)

    def _call(self, *args, **kwargs):
        """Select this CDF as current and call the CDF internal interface

        Adds call to select this CDF to L{args} and passes all parameters
        directly through to the CDFlib routine of the CDF library's C internal
        interface. Checks the return value with L{Library.check_status}.

        Parameters
        ==========
        args : various, see :py:mod:`ctypes`.
            Passed directly to the CDF library interface. Useful
            constants are defined in the :doc:`const <pycdf_const>`
            module of this package.

        Returns
        =======
        out : ctypes.c_long
            CDF status from the library

        .. note:
            Terminal NULL_ is automatically added to ``args``.
        Raises
        ======
        CDFError : if CDF library reports an error
        CDFWarning : if CDF library reports a warning and interpreter
                     is set to error on warnings.
        """
        return lib.call(const.SELECT_, const.CDF_, self._handle,
                        *args, **kwargs)

    def clone(self, zVar, name=None, data=True):
        """
        Clone a zVariable (from another CDF or this) into this CDF

        Parameters
        ==========
        zVar : :py:class:`Var`
            variable to clone

        Other Parameters
        ================
        name : str
            Name of the new variable (default: name of the original)
        data : boolean (optional)
            Copy data, or only type, dimensions, variance, attributes?
            (default: True, copy data as well)

        Returns
        =======
        out : :py:class:`Var`
            The newly-created zVar in this CDF
        """
        if name is None:
            name = zVar.name()
        if name in self:
            del self[name]
        self.new(name, type=zVar.type(), recVary=zVar.rv(),
                 dimVarys=zVar.dv(), dims=zVar._dim_sizes(),
                 n_elements=zVar._nelems())
        self[name].compress(*zVar.compress())
        self[name].attrs.clone(zVar.attrs)
        if data:
            r = zVar._raw
            zVar._raw = True
            self.raw_var(name)[...] = zVar[...]
            zVar._raw = r
        return zVar

    def col_major(self, new_col=None):
        """
        Finds the majority of this CDF file

        Other Parameters
        ================
        new_col : boolean
            Specify True to change to column-major, False to change to
            row major, or do not specify to check the majority
            rather than changing it.
            (default is check only)

        Returns
        =======
        out : boolean
            True if column-major, false if row-major
        """
        if new_col != None:
            new_maj = const.COLUMN_MAJOR if new_col else const.ROW_MAJOR
            self._call(const.PUT_, const.CDF_MAJORITY_, new_maj)
        maj = ctypes.c_long(0)
        self._call(const.GET_, const.CDF_MAJORITY_, ctypes.byref(maj))
        if not maj.value in (const.ROW_MAJOR.value, const.COLUMN_MAJOR.value):
            raise CDFError(const.BAD_MAJORITY)
        return maj.value == const.COLUMN_MAJOR.value

    def readonly(self, ro=None):
        """
        Sets or check the readonly status of this CDF

        If the CDF has been changed since opening, setting readonly mode
        will have no effect.

        Other Parameters
        ================
        ro : Boolean
            True to set the CDF readonly, False to set it read/write,
            or leave out to check only.

        Returns
        =======
        out : Boolean
            True if CDF is read-only, else False

        Raises
        ======
        CDFError : if bad mode is set
        """
        if ro == True:
            self._call(const.SELECT_, const.CDF_READONLY_MODE_,
                       const.READONLYon)
        elif ro == False:
            self._call(const.SELECT_, const.CDF_READONLY_MODE_,
                       const.READONLYoff)
        mode = ctypes.c_long(0)
        self._call(const.CONFIRM_, const.CDF_READONLY_MODE_,
                   ctypes.byref(mode))
        if mode.value == const.READONLYon.value:
            return True
        elif mode.value == const.READONLYoff.value:
            return False
        else:
            raise CDFError(const.BAD_READONLY_MODE.value)

    def checksum(self, new_val=None):
        """
        Set or check the checksum status of this CDF. If checksums
        are enabled, the checksum will be verified every time the file
        is opened.

        Other Parameters
        ================
        new_val : boolean
            True to enable checksum, False to disable, or leave out
            to simply check.

        Returns
        =======
        out : boolean
            True if the checksum is enabled or False if disabled
        """
        if new_val != None:
            self._call(const.PUT_, const.CDF_CHECKSUM_,
                       const.MD5_CHECKSUM if new_val else const.NO_CHECKSUM)
        chk = ctypes.c_long(0)
        self._call(const.GET_, const.CDF_CHECKSUM_, ctypes.byref(chk))
        if not chk.value in (const.MD5_CHECKSUM.value,
                             const.NO_CHECKSUM.value):
            raise CDFError(const.BAD_CHECKSUM)
        return chk.value == const.MD5_CHECKSUM.value

    def close(self):
        """
        Closes the CDF file

        Although called on object destruction (:meth:`~CDF.__del__`),
        to ensure all data are saved, the user should explicitly call
        :meth:`~CDF.close` or :meth:`~CDF.save`.

        Raises
        ======
        CDFError : if CDF library reports an error

        Warns
        =====
        CDFWarning : if CDF library reports a warning
        """

        self._call(const.CLOSE_, const.CDF_)
        self._opened = False

    def compress(self, comptype=None, param=None):
        """
        Set or check the compression of this CDF

        Sets compression on entire *file*, not per-variable.

        See section 2.6 of the CDF user's guide for more information on
        compression.

        Other Parameters
        ================
        comptype : ctypes.c_long
            type of compression to change to, see CDF C reference manual
            section 4.10. Constants for this parameter are in
            :mod:`~spacepy.pycdf.const`. If not specified, will not change
            compression.
        param : ctypes.c_long
            Compression parameter, see CDF CRM 4.10 and
            :mod:`~spacepy.pycdf.const`.
            If not specified, will choose reasonable default (5 for gzip;
            other types have only one possible parameter.)

        Returns
        =======
        out : tuple
            (comptype, param) currently in effect

        See Also
        ========
        :meth:`Var.compress`

        Examples
        ========
        Set file ``cdffile`` to gzip compression, compression level 9:
            >>> cdffile.compress(pycdf.const.GZIP_COMPRESSION, 9)
        """
        return _compress(self, comptype, param)

    def new(self, name, data=None, type=None, recVary=True, dimVarys=None,
            dims=None, n_elements=None, compress=None, compress_param=None):
        """
        Create a new zVariable in this CDF

        .. note::
            Either ``data`` or ``type`` must be specified. If type is not
            specified, it is guessed from ``data``.

        Parameters
        ==========
        name : str
            name of the new variable

        Other Parameters
        ================
        data
            data to store in the new variable. If this has a an ``attrs``
            attribute (e.g., :class:`~datamodel.dmarray`), it
            will be used to populate attributes of the new variable.
        type : ctypes.c_long
            CDF type of the variable, from :mod:`~spacepy.pycdf.const`.
            See section 2.5 of the CDF user's guide for more information on
            CDF data types.
        recVary : boolean
            record variance of the variable (default True)
        dimVarys : list of boolean
            dimension variance of each dimension, default True for all
            dimensions.
        dims : list of int
            size of each dimension of this variable, default zero-dimensional.
            Note this is the dimensionality as defined by CDF, i.e., for
            record-varying variables it excludes the leading record dimension.
            See :py:class:`Var`.
        n_elements : int
            number of elements, should be 1 except for CDF_CHAR,
            for which it's the length of the string.
        compress : ctypes.c_long
            Compression to apply to this variable, default None.
            See :py:meth:`Var.compress`.
        compress_param : ctypes.c_long
            Compression parameter if compression used; reasonable default
            is chosen. See :py:meth:`Var.compress`.

        Returns
        =======
        out : :py:class:`Var`
            the newly-created zVariable

        Raises
        ======
        ValueError : if neither data nor sufficient typing information
                     is provided.

        Notes
        =====
        Any given data may be representable by a range of CDF types; if
        the type is not specified, pycdf will guess which
        the CDF types which can represent this data. This breaks down to:

            #. If input data is a numpy array, match the type of that array
            #. Proper kind (numerical, string, time)
            #. Proper range (stores highest and lowest number provided)
            #. Sufficient resolution (EPOCH16 required if datetime has
               microseconds or below.)

        If more than one value satisfies the requirements, types are returned
        in preferred order:

            #. Type that matches precision of data first, then
            #. integer type before float type, then
            #. Smallest type first, then
            #. signed type first, then
            #. specifically-named (CDF_BYTE) vs. generically named (CDF_INT1)

        So for example, EPOCH_16 is preferred over EPOCH if ``data`` specifies
        below the millisecond level (rule 1), but otherwise EPOCH is preferred
        (rule 2).

        For floats, four-byte is preferred unless eight-byte is required:

            #. absolute values between 0 and 3e-39
            #. absolute values greater than 1.7e38

        This will switch to an eight-byte double in some cases where four bytes
        would be sufficient for IEEE 754 encoding, but where DEC formats would
        require eight.
        """
        if type in (const.CDF_EPOCH16, const.CDF_INT8, const.CDF_TIME_TT2000) \
                and self.backward:
            raise ValueError('Cannot use EPOCH16, INT8, or TIME_TT2000 '
                             'in backward-compatible CDF')
        if not lib.supports_int8 and \
                type in (const.CDF_INT8, const.CDF_TIME_TT2000):
            raise ValueError('INT8 and TIME_TT2000 require CDF library 3.4.0')
        if data is None:
            if type is None:
                raise ValueError('Must provide either data or a CDF type.')
            if dims is None:
                dims = []
            if n_elements is None:
                n_elements = 1
        else:
            (guess_dims, guess_types, guess_elements) = _Hyperslice.types(data)
            if dims is None:
                if recVary:
                    if guess_dims == ():
                        raise ValueError(
                            'Record-varying data cannot be scalar. '
                            'Specify NRV with CDF.new() or put data in array.')
                    dims = guess_dims[1:]
                else:
                    dims = guess_dims
            if type is None:
                type = guess_types[0]
                if type == const.CDF_EPOCH16.value and self.backward:
                    type = const.CDF_EPOCH
            if n_elements is None:
                n_elements = guess_elements
        if dimVarys is None:
            dimVarys = [True for i in dims]
        recVary = const.VARY if recVary else const.NOVARY
        dimVarys = [const.VARY if dimVary else const.NOVARY
                    for dimVary in dimVarys]
        if not hasattr(type, 'value'):
            type = ctypes.c_long(type)
        if type.value == const.CDF_INT8.value and not lib.supports_int8:
            raise ValueError(
                '64-bit integer support require CDF library 3.4.0')
        if type.value in (const.CDF_EPOCH16.value, const.CDF_INT8.value,
                    const.CDF_TIME_TT2000.value) \
                and self.backward:
            raise ValueError('Data requires EPOCH16, INT8, or TIME_TT2000; '
                             'incompatible with backward-compatible CDF')
        new_var = Var(self, name, type, n_elements, dims, recVary, dimVarys)
        if compress != None:
            new_var.compress(compress, compress_param)
        if data is not None:
            new_var[...] = data
            if hasattr(data, 'attrs'):
                new_var.attrs.clone(data.attrs)
        return new_var

    def raw_var(self, name):
        """
        Get a "raw" :class:`Var` object.

        Normally a :class:`Var` will perform translation of values for
        certain types (to/from Unicode for CHAR variables on Py3k,
        and to/from datetime for all time types). A "raw" object
        does not perform this translation, on read or write.

        This does *not* affect the data on disk, and in fact it
        is possible to maintain multiple Python objects with access
        to the same zVariable.

        Parameters
        ==========
        name : str
            name or number of the zVariable
        """
        v = self[name]
        v._raw = True
        return v

    def save(self):
        """
        Saves the CDF file but leaves it open.

        If closing the CDF, :meth:`close` is sufficient;
        there is no need to call
        :meth:`save` before :meth:`close`.

        .. note::
            Relies on an undocumented call of the CDF C library, which is
            also used in the Java interface.

        Raises
        ======
        CDFError : if CDF library reports an error

        Warns
        =====
        CDFWarning : if CDF library reports a warning
        """

        self._call(const.SAVE_, const.CDF_)

    def copy(self):
        """
        Make a copy of all data and attributes in this CDF

        Returns
        =======
        out : :py:class:`CDFCopy`
            :class:`~datamodel.SpaceData`-like object of all data
        """
        return CDFCopy(self)

    def version(self):
        """
        Get version of library that created this CDF

        Returns
        =======
        out : tuple
            version of CDF library, in form (version, release, increment)
        """
        ver = ctypes.c_long(0)
        rel = ctypes.c_long(0)
        inc = ctypes.c_long(0)
        self._call(const.GET_, const.CDF_VERSION_, ctypes.byref(ver),
                   const.GET_, const.CDF_RELEASE_, ctypes.byref(rel),
                   const.GET_, const.CDF_INCREMENT_, ctypes.byref(inc))
        return (ver.value, rel.value, inc.value)

    def _get_attrs(self):
        """Get attribute list

        Provide access to the CDF's attribute list without holding a
        strong reference, as the attribute list has a (strong)
        back-reference to its parent.

        Either deref a weak reference (to try and keep the object the same),
        or make a new AttrList instance and assign it to the weak reference
        for next time.
        """
        al = self._attrlistref()
        if al is None:
            al = gAttrList(self)
        self._attrlistref = weakref.ref(al)
        return al

    def _set_attrs(self, value):
        """Assign to the attribute list

        Clears all elements of the attribute list and copies from value
        """
        self.attrs.clone(value)

    attrs = property(
        _get_attrs, _set_attrs, None,
        """Global attributes for this CDF in a dict-like format.
        See :class:`gAttrList` for details.
        """)

class CDFCopy(datamodel.SpaceData):
    """
    A dictionary-like copy of all data and attributes in a :py:class:`CDF`

    Data are :class:`VarCopy` objects, keyed by variable name.
    CDF attributes are in :attr:`attrs`. (I.e.,
    data are accessed much like from a :class:`CDF`).

    Do not instantiate this class directly; use :meth:`~CDF.copy`
    on an existing :class:`CDF`.

    Examples
    --------
    >>> from spacepy import pycdf
    >>> with pycdf.CDF('test.cdf') as cdffile:
    ...     data = cdffile.copy()

    .. attribute:: attrs

       Python dictionary containing attributes copied from the CDF.
    """

    def __init__(self, cdf):
        """Copies all data and attributes from a CDF

        @param cdf: CDF to take data from
        @type cdf: :py:class:`pycdf.CDF`
        """
        super(CDFCopy, self).__init__(((key, var.copy())
                                      for (key, var) in cdf.items()),
                                      attrs = cdf.attrs.copy())


class Var(collections.MutableSequence):
    """
    A CDF variable.

    This object does not directly store the data from the CDF; rather,
    it provides access to the data in a format that much like a Python
    list or numpy :class:`~numpy.ndarray`.
    General list information is available in the python docs:
    `1 <http://docs.python.org/tutorial/introduction.html#lists>`_,
    `2 <http://docs.python.org/tutorial/datastructures.html#more-on-lists>`_,
    `3 <http://docs.python.org/library/stdtypes.html#typesseq>`_.

    The CDF user's guide, section 2.3, provides background on variables.

    .. note::
        Not intended to be created directly; use methods of :class:`CDF` to gain access to a variable.

    A record-varying variable's data are viewed as a hypercube of dimensions
    n_dims+1 (the extra dimension is the record number). They are indexed in
    row-major fashion, i.e. the last index changes most frequently / is
    contiguous in memory. If the CDF is column-major, the data are
    transformed to row-major before return.

    Non record-varying variables are similar, but do not have the extra
    dimension of record number.

    Variables can be subscripted by a multidimensional index to return the
    data. Indices are in row-major order with the first dimension
    representing the record number. If the CDF is column major,
    the data are reordered to row major. Each dimension is specified
    by standard Python
    `slice <http://docs.python.org/tutorial/introduction.html#strings>`_
    notation, with dimensions separated by commas. The ellipsis fills in
    any missing dimensions with full slices. The returned data are
    lists; Python represents multidimensional arrays as nested lists.
    The innermost set of lists represents contiguous data.

    .. note::
        numpy 'fancy indexing' is *not* supported.

    Degenerate dimensions are 'collapsed', i.e. no list of only one
    element will be returned if a single subscript is specified
    instead of a range. (To avoid this, specify a slice like 1:2,
    which starts with 1 and ends before 2).

    Two special cases:

      1. requesting a single-dimension slice for a
         record-varying variable will return all data for that
         record number (or those record numbers) for that variable.
      2. Requests for multi-dimensional variables may skip the record-number
         dimension and simply specify the slice on the array itself. In that
         case, the slice of the array will be returned for all records.

    In the event of ambiguity (e.g., single-dimension slice on a one-dimensional
    variable), case 1 takes priority.
    Otherwise, mismatch between the number of dimensions specified in
    the slice and the number of dimensions in the variable will cause
    an :exc:`~exceptions.IndexError` to be thrown.

    This all sounds very complicated but it is essentially attempting
    to do the 'right thing' for a range of slices.

    An unusual case is scalar (zero-dimensional) non-record-varying variables.
    Clearly they cannot be subscripted normally. In this case, use the
    ``[...]`` syntax meaning 'access all data.':

    >>> from spacepy import pycdf
    >>> testcdf = pycdf.CDF('test.cdf', '')
    >>> variable = testcdf.new('variable', recVary=False,
    ...     type=pycdf.const.CDF_INT4)
    >>> variable[...] = 10
    >>> variable
    <Var:
    CDF_INT4 [] NRV
    >
    >>> variable[...]
    10

    As a list type, variables are also `iterable
    <http://docs.python.org/tutorial/classes.html#iterators>`_; iterating
    over a variable returns a single complete record at a time.

    This is all clearer with examples. Consider a variable ``B_GSM``, with
    three elements per record (x, y, z components) and fifty records in
    the CDF. Then:

      1. ``B_GSM[0, 1]`` is the y component of the first record.
      2. ``B_GSM[10, :]`` is a three-element list, containing x, y, and z
         components of the 11th record. As a shortcut, if only one dimension
         is specified, it is assumed to be the record number, so this
         could also be written ``B_GSM[10]``.
      3. ``B_GSM[...]`` reads all data for ``B_GSM`` and returns it as a
         fifty-element list, each element itself being a three-element
         list of x, y, z components.

    Multidimensional example: consider fluxes stored as a function of
    pitch angle and energy. Such a variable may be called Flux and
    stored as a two-dimensional array, with the first dimension
    representing (say) ten energy steps and the second, eighteen
    pitch angle bins (ten degrees wide, centered from 5 to 175 degrees).
    Assume 100 records stored in the CDF (i.e. 100 different times).

      1. ``Flux[4]`` is a list of ten elements, one per energy step,
         each element being a list of 18 fluxes, one per pitch bin.
         All are taken from the fifth record in the CDF.
      2. ``Flux[4, :, 0:4]`` is the same record, all energies, but
         only the first four pitch bins (roughly, field-aligned).
      3. ``Flux[..., 0:4]`` is a 100-element list (one per record),
         each element being a ten-element list (one per energy step),
         each containing fluxes for the first four pitch bins.

    This slicing notation is very flexible and allows reading
    specifically the desired data from the CDF.

    All data are, on read, converted to appropriate Python data
    types; EPOCH, EPOCH16, and TIME_TT2000 types are converted to
    :class:`~datetime.datetime`. Data are returned in numpy arrays.

    .. note::
        Although pycdf supports TIME_TT2000 variables, the Python
        :class:`~datetime.datetime` object does not support leap
        seconds. Thus, on read, any seconds past 59 are truncated
        to 59.999999 (59 seconds, 999 milliseconds, 999 microseconds).

    Potentially useful list methods and related functions:
      - `count <http://docs.python.org/tutorial/datastructures.html#more-on-lists>`_
      - `in <http://docs.python.org/reference/expressions.html#in>`_
      - `index <http://docs.python.org/tutorial/datastructures.html#more-on-lists>`_
      - `len <http://docs.python.org/library/functions.html#len>`_
      - `list comprehensions
        <http://docs.python.org/tutorial/datastructures.html#list-comprehensions>`_
      - `sorted <http://docs.python.org/library/functions.html#sorted>`_

    The topic of array majority can be very confusing; good background material
    is available at `IDL Array Storage and Indexing
    <http://www.dfanning.com/misc_tips/colrow_major.html>`_. In brief,
    *regardless of the majority stored in the CDF*, pycdf will always present
    the data in the native Python majority, row-major order, also known as
    C order. This is the default order in `NumPy
    <http://docs.scipy.org/doc/numpy/reference/arrays.ndarray.html
    #internal-memory-layout-of-an-ndarray>`_.
    However, packages that render image data may expect it in column-major
    order. If the axes seem 'swapped' this is likely the reason.

    The :attr:`~Var.attrs` Python attribute acts as a dictionary referencing
    zAttributes (do not confuse the two); all the dictionary methods above
    also work on the attribute dictionary. See :class:`zAttrList` for more on
    the dictionary of attributes.

    With writing, as with reading, every attempt has been made to match the
    behavior of Python lists. You can write one record, many records, or even
    certain elements of all records. There is one restriction: only the record
    dimension (i.e. dimension 0) can be resized by write, as all records
    in a variable must have the same dimensions. Similarly, only whole
    records can be deleted.

    .. note::
        Unusual error messages on writing data usually mean that pycdf is
        unable to interpret the data as a regular array of a single type
        matching the type and shape of the variable being written.
        A 5x4 array is supported; an irregular array where one row has
        five columns and a different row has six columns is not. Error messages
        of this type include:

          - ``Data must be well-formed, regular array of number, string, or datetime``
          - ``setting an array element with a sequence.``
          - ``shape mismatch: objects cannot be broadcast to a
            single shape``

    For these examples, assume Flux has 100 records and dimensions [2, 3].

    Rewrite the first record without changing the rest:

    >>> Flux[0] = [[1, 2, 3], [4, 5, 6]]

    Writes a new first record and delete all the rest:

    >>> Flux[...] = [[1, 2, 3], [4, 5, 6]]

    Write a new record in the last position and add a new record after:

    >>> Flux[99:] = [[[1, 2, 3], [4, 5, 6]],
    ...              [[11, 12, 13], [14, 15, 16]]]

    Insert two new records between the current number 5 and 6:

    >>> Flux[5:6] = [[[1, 2, 3], [4, 5, 6]],  [[11, 12, 13],
    ...               [14, 15, 16]]]

    This operation can be quite slow, as it requires reading and
    rewriting the entire variable. (CDF does not directly support
    record insertion.)

    Change the first element of the first two records but leave other
    elements alone:

    >>> Flux[0:2, 0, 0] = [1, 2]

    Remove the first record:

    >>> del Flux[0]

    Removes record 5 (the sixth):

    >>> del Flux[5]

    Due to the need to work around a bug in the CDF library, this operation
    can be quite slow.

    Delete *all data* from ``Flux``, but leave the variable definition intact:

    >>> del Flux[...]

    .. note::
        Although this interface only directly supports zVariables, zMode is
        set on opening the CDF so rVars appear as zVars. See p.24 of the
        CDF user's guide; pyCDF uses zMode 2.


    .. autosummary::

        ~Var.attrs
        ~Var.compress
        ~Var.copy
        ~Var.dtype
        ~Var.dv
        ~Var.insert
        ~Var.name
        ~Var.rename
        ~Var.rv
        ~Var.shape
        ~Var.type
    .. attribute:: Var.attrs

       zAttributes for this zVariable in a dict-like format.
       See :class:`zAttrList` for details.
    .. automethod:: compress
    .. automethod:: copy
    .. autoattribute:: dtype
    .. automethod:: dv
    .. automethod:: insert
    .. automethod:: name
    .. automethod:: rename
    .. automethod:: rv
    .. autoattribute:: shape
    .. automethod:: type
    """
    def __init__(self, cdf_file, var_name, *args):
        """Create or locate a variable

        Parameters
        ==========
        cdf_file : :py:class:`pycdf.CDF`
            CDF file containing this variable
        var_name : string
            name of this variable

        Other Parameters
        ================
        args
            additional arguments passed to :py:meth:`_create`. If none,
            opens an existing variable. If provided, creates a
            new one.

        Raises
        ======
        CDFError
            if CDF library reports an error

        Warns
        =====
        CDFWarning
            if CDF library reports a warning
        """
        self.cdf_file = cdf_file
        self._name = None
        self._type = None #CDF type (long)
        self._raw = False #Raw access (skip all conversions)
        if len(args) == 0:
            self._get(var_name)
        else:
            self._create(var_name, *args)
        #Weak reference to attribute list (use attrs instead)
        #This avoids a reference loop
        self._attrlistref = weakref.ref(zAttrList(self))

    def __getitem__(self, key):
        """Returns a slice from the data array. Details under :py:class:`pycdf.Var`.

        @return: The data from this variable
        @rtype: list-of-lists of appropriate type.
        @raise IndexError: if L{key} is out of range, mismatches dimensions,
                           or simply unparseable.
        @raise CDFError: for errors from the CDF library
        """
        hslice = _Hyperslice(self, key)
        result = hslice.create_array()
        if hslice.counts[0] != 0:
            hslice.select()
            lib.call(const.GET_, const.zVAR_HYPERDATA_,
                     result.ctypes.data_as(ctypes.c_void_p))
        return hslice.convert_input_array(result)

    def __delitem__(self, key):
        """Removes a record (or set of records) from the CDF

        Only whole records can be deleted, so the del call must either specify
        only one dimension or it must specify all elements of the non-record
        dimensions. This is *not* a way to resize a variable!

        Deleting records from the middle of a variable may be very slow in
        some circumstances. To work around a bug in CDF library versions
        3.4.0 and before, all the data must be read in, the requested deletions
        done, and then all written back out.

        @param key: index or slice to delete
        @type key: int or slice
        @raise TypeError: if an attempt is made to delete from a non
                          record-varying variable, or to delete below
                          the record level
        """
        if not self.rv():
            raise TypeError('Cannot delete records from non-record-varying '
                            'variable.')
        hslice = _Hyperslice(self, key)
        if hslice.dims > 1 and (hslice.counts[1:] != hslice.dimsizes[1:]).any():
            raise TypeError('Can only delete entire records.')
        if hslice.counts[0] == 0:
            return
        start = hslice.starts[0]
        count = hslice.counts[0]
        interval = hslice.intervals[0]
        dimsize = hslice.dimsizes[0]

        self._call()
        dangerous_delete = False
        if lib._del_middle_rec_bug and \
               (interval != 1 or (start != 0 and start + count < dimsize)):
            #delete from middle is dangerous if only have one index entry
            entries = ctypes.c_long(0)
            lib.call(const.GET_, const.zVAR_nINDEXENTRIES_,
                     ctypes.byref(entries))
            dangerous_delete = (entries.value == 1)

        if dangerous_delete:
            data = self[...]
            data = numpy.delete(
                data,
                numpy.arange(start, start + count * interval, interval),
                0)
            self[0:dimsize - count] = data
            first_rec = dimsize - count
            last_rec = dimsize - 1
            lib.call(const.DELETE_, const.zVAR_RECORDS_,
                     ctypes.c_long(first_rec), ctypes.c_long(last_rec))
        elif interval == 1:
            first_rec = ctypes.c_long(start)
            last_rec = ctypes.c_long(start + count - 1)
            lib.call(const.DELETE_, const.zVAR_RECORDS_,
                     first_rec, last_rec)
        else:
            self._call()
            #delete from end to avoid renumbering of records
            for recno in range(start + (count - 1) * interval,
                               start - 1, -1 * interval):
                lib.call(const.DELETE_, const.zVAR_RECORDS_,
                         ctypes.c_long(recno), ctypes.c_long(recno))

    def __setitem__(self, key, data):
        """Puts a slice into the data array. Details under :py:class:`pycdf.Var`.

        @param key: index or slice to store
        @type key: int or slice
        @param data: data to store
        @type data: numpy.array
        @raise IndexError: if L{key} is out of range, mismatches dimensions,
                           or simply unparseable. IndexError will
        @raise CDFError: for errors from the CDF library
        """
        hslice = _Hyperslice(self, key)
        n_recs = hslice.counts[0]
        hslice.expand(data)
        cdf_type = self.type()
        if cdf_type == const.CDF_EPOCH16.value:
            if not self._raw:
                try:
                    data = lib.v_datetime_to_epoch16(data)
                except AttributeError:
                    pass
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.float64)
        elif cdf_type == const.CDF_EPOCH.value:
            if not self._raw:
                try:
                    data = lib.v_datetime_to_epoch(data)
                except AttributeError:
                    pass
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.float64)
        elif cdf_type == const.CDF_TIME_TT2000.value:
            if not self._raw:
                try:
                    data = lib.v_datetime_to_tt2000(data)
                except AttributeError:
                    pass
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.int64)
        else:
             data = numpy.require(data, requirements=('C', 'A', 'W'),
                                  dtype=self._np_type())
        if cdf_type == const.CDF_EPOCH16.value:
            datashape = data.shape[:-1]
        else:
            datashape = data.shape
        #Check data sizes
        if datashape != tuple(hslice.expected_dims()):
             raise ValueError('attempt to assign data of dimensions ' +
                              str(datashape) + ' to slice of dimensions ' +
                              str(tuple(hslice.expected_dims())))
        #Flip majority and reversed dimensions, see convert_input_array
        data = hslice.convert_output_array(data)
        #Handle insertions and similar weirdness
        if hslice.counts[0] > n_recs and \
               hslice.starts[0] + n_recs < hslice.dimsizes[0]:
            #Specified slice ends before last record, so insert in middle
            saved_data = self[hslice.starts[0] + n_recs:]
        if hslice.counts[0] > 0:
            hslice.select()
            lib.call(const.PUT_, const.zVAR_HYPERDATA_,
                     data.ctypes.data_as(ctypes.c_void_p))
        if hslice.counts[0] < n_recs:
            first_rec = hslice.starts[0] + hslice.counts[0]
            last_rec = hslice.dimsizes[0] - 1
            lib.call(const.DELETE_, const.zVAR_RECORDS_,
                     ctypes.c_long(first_rec), ctypes.c_long(last_rec))
        elif hslice.counts[0] > n_recs and \
               hslice.starts[0] + n_recs < hslice.dimsizes[0]:
            #Put saved data in after inserted data
            self[hslice.starts[0] + hslice.counts[0]:] = saved_data

    def extend(self, data):
        """
        Append multiple values to the end of this variable

        This is an efficiency function which overrides the base implementation
        in MutableSequence.

        Parameters
        ----------
        data :
            the data to append
        """
        self[len(self):] = data

    def insert(self, index, data):
        """
        Inserts a *single* record before an index

        Parameters
        ----------
        index : int
            index before which to insert the new record
        data :
            the record to insert
        """
        self[index:index] = [data]

    def _create(self, var_name, datatype, n_elements = 1, dims = (),
               recVary = const.VARY, dimVarys = None):
        """Creates a new zVariable

        @param var_name: name of this variable
        @type var_name: string
        @param datatype: CDF data type
        @type datatype: ctypes.c_long
        @param n_elements: number of elements (should be 1 except for
                           CDF_CHAR variables).
        @type n_elements: long
        @param dims: size of each dimension for multi-dimensional variable,
                     or empty for a zero-dimensional
        @type dims: sequence of long
        @param recVary: record variance for this variable (VARY/NOVARY)
        @type recVary: long
        @param dimVarys: array of VARY or NOVARY, variance for each dimension
        @type dimVarys: sequence of long
        @return: new variable with this name
        @rtype: :py:class:`pycdf.Var`
        @raise CDFError: if CDF library reports an error
        @raise CDFWarning: if CDF library reports a warning and interpreter
                           is set to error on warnings.
        @note: Not intended to be used directly; use L{CDF.new}.
        """

        dim_array = (ctypes.c_long * len(dims))(*dims)
        enc_name = var_name.encode('ascii')
        if dimVarys is None:
            dim_vary_array = (ctypes.c_long * (len(dims) if len(dims) > 0 else 1))(const.VARY)
        else:
            dim_vary_array = (ctypes.c_long * len(dims))(*dimVarys)
        varNum = ctypes.c_long(0)
        self.cdf_file._call(const.CREATE_, const.zVAR_, enc_name, datatype,
                 ctypes.c_long(n_elements), ctypes.c_long(len(dims)), dim_array,
                 recVary, dim_vary_array, ctypes.byref(varNum))
        self._name = enc_name

    def _delete(self):
        """Removes this zVariable from the CDF

        @raise CDFError: if CDF library reports an error
        @raise CDFWarning: if CDF library reports a warning and interpreter
                           is set to error on warnings.
        """

        self.cdf_file._call(const.SELECT_, const.zVAR_NAME_, self._name,
                 const.DELETE_, const.zVAR_)
        self._name = None

    def _get(self, var_name):
        """Gets an existing zVariable

        @param var_name: name of this variable
        @type var_name: string
        @return: variable with this name
        @rtype: :py:class:`pycdf.Var`
        @raise CDFError: if CDF library reports an error
        @raise CDFWarning: if CDF library reports a warning and interpreter
                           is set to error on warnings.
        @note: Not intended to be used directly; use L{CDF.__getitem__}.
        """

        if isinstance(var_name, str_classes):
            try:
                enc_name = var_name.encode('ascii').rstrip()
            except AttributeError:
                enc_name = var_name.rstrip() #already in ASCII
            #This call simply 'touches' the CDF to cause an error if the name isn't there
            varNum = ctypes.c_long(0)
            self.cdf_file._call(const.GET_, const.zVAR_NUMBER_, enc_name, ctypes.byref(varNum))
            self._name = enc_name
        else:
            name = ctypes.create_string_buffer(const.CDF_VAR_NAME_LEN256+1)
            self.cdf_file._call(const.SELECT_, const.zVAR_, ctypes.c_long(var_name),
                     const.GET_, const.zVAR_NAME_, name)
            self._name = name.value.rstrip()

    def _num(self):
        """Returns the zVar number for this variable

        @return: number of this zVar
        @rtype: int
        """
        varNum = ctypes.c_long(0)
        self.cdf_file._call(const.GET_, const.zVAR_NUMBER_, self._name, ctypes.byref(varNum))
        return varNum.value

    def __len__(self):
        """Get number of records for this variable in this file

        @return: Number of records
        @rtype: long
        @raise CDFError: if CDF library reports an error
        @raise CDFWarning: if CDF library reports a warning and interpreter
                           is set to error on warnings.
        """
        count = ctypes.c_long(0)
        self._call(const.GET_, const.zVAR_MAXREC_, ctypes.byref(count))
        return (count.value + 1)

    def __repr__(self):
        """Returns representation of the variable

        Cannot return anything that can be eval'd to create a copy,
        so just wrap the informal representation in angle brackets.
        @return: info on this zVar
        @rtype: str
        """
        return '<Var:\n' + str(self) + '\n>'

    def __str__(self):
        """Returns a string representation of the variable

        This is an 'informal' representation in that it cannot be evaluated
        directly to create a :py:class:`pycdf.Var`.

        @return: info on this zVar, CDFTYPE [dimensions] NRV
                 (if not record-varying)
        @rtype: str
        """
        if self.cdf_file._opened:
            cdftype = self.type()
            chartypes = (const.CDF_CHAR.value, const.CDF_UCHAR.value)
            rv = self.rv()
            typestr = lib.cdftypenames[cdftype] + \
                      ('*' + str(self._nelems()) if cdftype in chartypes else '' )
            if rv:
                sizestr = str([len(self)] + self._dim_sizes())
            else:
                sizestr = str(self._dim_sizes())
            return typestr + ' ' + sizestr + ('' if rv else ' NRV')
        else:
            if isinstance(self._name, str):
                return 'zVar "{0}" in closed CDF {1}'.format(
                    self._name, self.cdf_file.pathname)
            else:
                return 'zVar "{0}" in closed CDF {1}'.format(
                    self._name.decode('ascii'),
                    self.cdf_file.pathname.decode('ascii'))

    def _n_dims(self):
        """Get number of dimensions for this variable

        @return: the number of dimensions
        @rtype: long
        """
        n_dims = ctypes.c_long(0)
        self._call(const.GET_, const.zVAR_NUMDIMS_, ctypes.byref(n_dims))
        return n_dims.value

    def _dim_sizes(self):
        """Get the dimension sizes for this variable

        @return: sequence of sizes
        @rtype: sequence of long
        @note: This will always be in Python order (i.e. row major, last index
        iterates most quickly), *regardless* of the majority of the CDF.
        """
        sizes = (ctypes.c_long * const.CDF_MAX_DIMS)(0)
        self._call(const.GET_, const.zVAR_DIMSIZES_, sizes)
        sizes = sizes[0:self._n_dims()]
        return sizes

    def rv(self, new_rv=None):
        """
        Gets or sets whether this variable has record variance

        If the variance is unknown, True is assumed
        (this replicates the apparent behavior of the CDF library on
        variable creation).

        Other Parameters
        ================
        new_rv : boolean
            True to change to record variance, False to change to NRV,
            unspecified to simply check variance.

        Returns
        =======
        out : Boolean
            True if record varying, False if NRV
        """
        if new_rv != None:
            self._call(const.PUT_, const.zVAR_RECVARY_,
                       const.VARY if new_rv else const.NOVARY)
        vary = ctypes.c_long(0)
        self._call(const.GET_, const.zVAR_RECVARY_, ctypes.byref(vary))
        return vary.value != const.NOVARY.value

    def dv(self, new_dv=None):
        """
        Gets or sets dimension variance of each dimension of variable.

        If the variance is unknown, True is assumed
        (this replicates the apparent behavior of the
        CDF library on variable creation).

        Parameters
        ==========
        new_dv : list of boolean
            Each element True to change that dimension to dimension
            variance, False to change to not dimension variance.
            (Unspecified to simply check variance.)

        Returns
        =======
        out : list of boolean
            True if that dimension has variance, else false.
        """
        ndims = self._n_dims()
        if new_dv != None:
            if len(new_dv) != ndims:
                raise ValueError('Must specify variance for ' +
                                 str(ndims) + 'dimensions.')
            varies = (ctypes.c_long * ndims)(
                *[const.VARY if dv else const.NOVARY for dv in new_dv])
            self._call(const.PUT_, const.zVAR_DIMVARYS_,
                       varies)
        if ndims == 0:
            return []
        varies = (ctypes.c_long * const.CDF_MAX_DIMS)()
        self._call(const.GET_, const.zVAR_DIMVARYS_, varies)
        return [dv != const.NOVARY.value for dv in varies[0:ndims]]

    def _call(self, *args, **kwargs):
        """Select this CDF and variable and call the CDF internal interface

        Adds call to select this CDF to L{args} and passes all parameters
        directly through to the CDFlib routine of the CDF library's C internal
        interface. Checks the return value with L{Library.check_status}.

        @param args: Passed directly to the CDF library interface. Useful
                     constants are defined in the :py:mod:`pycdf.const` module of this package.
        @type args: various, see :py:mod:`ctypes`.
        @return: CDF status from the library
        @rtype: ctypes.c_long
        @note: Terminal NULL_ is automatically added to L{args}.
        @raise CDFError: if CDF library reports an error
        @raise CDFWarning: if CDF library reports a warning and interpreter
                           is set to error on warnings.
        """
        return self.cdf_file._call(const.SELECT_, const.zVAR_NAME_, self._name,
                                   *args, **kwargs)

    def _np_type(self):
        """Returns the numpy type of this variable

        This is the numpy type that will come directly out of the CDF;
        see :meth:`dtype` for the representation post-conversion.

        Raises
        ======
        CDFError : for library-reported error or failure to find numpy type

        Returns
        =======
        out : dtype
            numpy dtype that will hold value from this variable

        """
        cdftype = self.type()
        if cdftype == const.CDF_CHAR.value or cdftype == const.CDF_UCHAR.value:
            return numpy.dtype('S' + str(self._nelems()))
        try:
            return lib.numpytypedict[cdftype]
        except KeyError:
            raise CDFError(const.BAD_DATA_TYPE)

    def type(self, new_type=None):
        """
        Returns or sets the CDF type of this variable

        Parameters
        ==========
        new_type : ctypes.c_long
            the new type from :mod:`~spacepy.pycdf.const`

        Returns
        =======
        out : int
            CDF type
        """
        if new_type != None:
            if not hasattr(new_type, 'value'):
                new_type = ctypes.c_long(new_type)
            n_elements = ctypes.c_long(self._nelems())
            self._call(const.PUT_, const.zVAR_DATASPEC_,
                       new_type, n_elements)
            self._type = None
        if self._type is None:
            cdftype = ctypes.c_long(0)
            self._call(const.GET_, const.zVAR_DATATYPE_,
                       ctypes.byref(cdftype))
            self._type = cdftype.value
        return self._type

    def _nelems(self):
        """Number of elements for each value in this variable

        This is the length of strings for CHAR and UCHAR,
        should be 1 otherwise.
        @return: length of strings
        @rtype: int
        """
        nelems = ctypes.c_long(0)
        self._call(const.GET_, const.zVAR_NUMELEMS_, ctypes.byref(nelems))
        return nelems.value

    def name(self):
        """
        Returns the name of this variable

        Returns
        =======
        out : str
            variable's name
        """
        if isinstance(self._name, str):
            return self._name
        elif isinstance(self._name, bytes):
            return self._name.decode()

    def compress(self, comptype=None, param=None):
        """
        Set or check the compression of this variable

        Compression may not be changeable on variables with data already
        written; even deleting the data may not permit the change.

        See section 2.6 of the CDF user's guide for more information on
        compression.

        Other Parameters
        ================
        comptype : ctypes.c_long
            type of compression to change to, see CDF C reference
            manual section 4.10. Constants for this parameter
            are in :mod:`~spacepy.pycdf.const`. If not specified, will not
            change compression.
        param : ctypes.c_long
            Compression parameter, see CDF CRM 4.10 and
            :mod:`~spacepy.pycdf.const`.
            If not specified, will choose reasonable default (5 for
            gzip; other types have only one possible parameter.)

        Returns
        =======
        out : tuple
            the (comptype, param) currently in effect
        """
        return _compress(self, comptype, param)

    def copy(self):
        """
        Copies all data and attributes from this variable

        Returns
        =======
        out : :class:`VarCopy`
            list of all data in record order
        """
        return VarCopy(self)

    def rename(self, new_name):
        """
        Renames this variable

        Parameters
        ==========
        new_name : str
            the new name for this variable
        """
        try:
            enc_name = new_name.encode('ascii')
        except AttributeError:
            enc_name = new_name
        if len(enc_name) > const.CDF_VAR_NAME_LEN256:
            raise CDFError(const.BAD_VAR_NAME)
        self._call(const.PUT_, const.zVAR_NAME_, enc_name)
        self._name = enc_name

    @property
    def shape(self):
        """
        Provides the numpy array-like shape of this variable.

        Returns a tuple; first element is number of records (RV variable
        only) And the rest provide the dimensionality of the variable.

        .. note::
            Assigning to this attribute will not change the shape.
        """
        if self.rv():
            return tuple([len(self)] + self._dim_sizes())
        else:
            return tuple(self._dim_sizes())

    @property
    def dtype(self):
        """
        Provide the numpy dtype equivalent to the CDF type of this variable.

        Data from this variable will be returned in numpy arrays of this type.

        See Also
        --------
        type
        """
        cdftype = self.type()
        if cdftype in (const.CDF_CHAR.value, const.CDF_UCHAR.value) and \
           str is not bytes and not self._raw:
            return numpy.dtype('U' + str(self._nelems()))
        if cdftype in (const.CDF_EPOCH.value, const.CDF_EPOCH16.value,
                       const.CDF_TIME_TT2000.value) and not self._raw:
            return numpy.dtype('O')
        return self._np_type()

    def _get_attrs(self):
        """Get attribute list

        Provide access to the zVar's attribute list without holding a
        strong reference, as the attribute list has a (strong)
        back-reference to its parent.

        Either deref a weak reference (to try and keep the object the same),
        or make a new AttrList instance and assign it to the weak reference
        for next time.
        """
        al = self._attrlistref()
        if al is None:
            al = zAttrList(self)
        self._attrlistref = weakref.ref(al)
        return al

    def _set_attrs(self, value):
        """Assign to the attribute list

        Clears all elements of the attribute list and copies from value
        """
        self.attrs.clone(value)

    attrs = property(
        _get_attrs, _set_attrs, None,
        """zAttributes for this zVariable in a dict-like format.
        See :class:`zAttrList` for details.
        """)


class VarCopy(datamodel.dmarray):
    """
    A list-like copy of the data and attributes in a :class:`Var`

    Data are in the list elements. CDF attributes are in a dict,
    accessed through :attr:`attrs`. (I.e.,
    data and attributes are accessed like in a :class:`Var`.)

    Do not instantiate this class directly; use :meth:`~Var.copy`
    on an existing :class:`Var`.

    .. attribute:: attrs

       Python dictionary containing attributes copied from the zVar
    """

    def __new__(cls, zVar):
        """Copies all data and attributes from a zVariable

        @param zVar: variable to take data from
        @type zVar: :py:class:`pycdf.Var`
        """
        return super(VarCopy, cls).__new__(cls, zVar[...], zVar.attrs.copy())


class _Hyperslice(object):
    """Represents a CDF 'slice' used for the hyper CDF functions

    For internal module use only.

    @ivar dims: number of dimensions to this slice, usually
                number of dimensions to the variable plus one
                for the record, which represents the 0th
                (least rapidly varying) dimension.
    @type dims: int
    @ivar dimsizes: size of each dimension (0th is number of records)
    @type dimsizes: list of int
    @ivar starts: index of the start value for each dimension
                  ('dimension indices' in CDF speak)
    @type starts: list of int
    @ivar counts: number of values to get from each dimension.
                  Final result will be the product of everything
                  in counts.
                  ('dimension counts' in CDF speak)
    @type counts: numpy.array
    @ivar intervals: interval between successive indices
                     to use for each dimension.
                     ('dimension invervals' in CDF speak)
    @type intervals: list of int
    @ivar degen: is this dimension degenerate, i.e. should be
                 removed in the returned dataset. A 3D array
                 with one dimension degenerate will be returned
                 as a 2D array (i.e. list-of-lists.)
    @type degen: numpy.array
    @ivar rev: should this dimension be returned in reverse order?
    @type rev: numpy.array
    @ivar column: is this slice in column-major mode (if false, row-major)
    @type column: boolean
    @ivar zvar: what CDF variable this object slices on
    @type zvar: :py:class:`pycdf.Var`
    @ivar expanded_key: fully-expanded version of the key passed to the
                        constructor (all dimensions filled in)
    @type expanded_key: tuple
    @note: All dimension-related variables are stored row-major
           (Python order)
    """

    def __init__(self, zvar, key):
        """Create a Hyperslice

        @param zvar: zVariable that this slices
        @type zvar: :py:class:`pycdf.Var`
        @param key: Python multi-dimensional slice as passed to
                    __getitem__
        @type key: tuple of slice and/or int
        @raise IndexError: if slice is out of range, mismatches dimensions, or
                           otherwise unparsable.
        @raise ValueError: if slice has invalid values
        """

        self.zvar = zvar
        self.rv = self.zvar.rv()
        #dim of records, + 1 record dim (NRV always is record 0)
        self.dims = zvar._n_dims() + 1
        self.dimsizes = [len(zvar)] + \
                        zvar._dim_sizes()
        self.starts = [0] * self.dims
        self.counts = numpy.empty((self.dims,), dtype=numpy.int32)
        self.counts.fill(1)
        self.intervals = [1] * self.dims
        self.degen = numpy.zeros(self.dims, dtype=numpy.bool)
        self.rev = numpy.zeros(self.dims, dtype=numpy.bool)
        #key is:
        #1. a single value (integer or slice object) if called 1D
        #2. a tuple (of integers and/or slice objects) if called nD
        #3. Each item is either a single value (degenerate dim)
        #   or a slice object.

        if not hasattr(key, '__len__'): #Not a container object, pack in tuple
            key = (key, )
        if not self.rv:
            key = (0, ) + key #NRV, so always get 0th record (degenerate)
        key = self.expand_ellipsis(key, self.dims)
        if self.rv: #special-cases for RV variables
            if len(key) == 1: #get all data for this record(s)
                key = self.expand_ellipsis(key + (Ellipsis, ), self.dims)
            elif len(key) == self.dims - 1: #get same slice from each record
                key = (slice(None, None, None), ) + key
        if len(key) == self.dims:
            self.expanded_key = key
            for i in range(self.dims):
                idx = key[i]
                if hasattr(idx, 'start'): #slice
                    (self.starts[i], self.counts[i],
                     self.intervals[i], self.rev[i]) = \
                     self.convert_range(idx.start, idx.stop,
                                              idx.step, self.dimsizes[i])
                else: #Single degenerate value
                    if idx < 0:
                        idx += self.dimsizes[i]
                    if idx != 0 and (idx >= self.dimsizes[i] or idx < 0):
                        raise IndexError('list index out of range')
                    self.starts[i] = idx
                    self.degen[i] = True
        else:
            raise IndexError('Slice does not match dimensions for zVar ' +
                             str(zvar._name))

        self.column = zvar.cdf_file.col_major()

    def expected_dims(self, data=None):
        """Calculate size of non-degenerate dimensions

        Figures out size, in each dimension, of expected input data

        @return: size of each dimension for this slice, excluding degenerate
        @rtype: list of int
        """
        return [self.counts[i] for i in range(self.dims) if not self.degen[i]]

    def expand(self, data):
        """Expands the record dimension of this slice to hold a set of data

        If the length of data (outermost dimension) is larger than the record
        count (counts[0]) for this slice, expand the slice to hold all the data.
        This requires that the record dimension of the slice not be degenerate,
        and also that it not have been completely specified when the hyperslice
        was created (i.e. record dimension either ellipsis or no specified
        stop.)

        Does *not* expand any other dimension, since that's Very Hard in CDF.

        @param data: the data which are intended to be stored in this slice
        @type data: list
        """
        rec_slice = self.expanded_key[0]
        if not self.rv or isinstance(data, str_classes) or self.degen[0] or \
               not hasattr(rec_slice, 'stop'):
            return
        if len(data) < self.counts[0]: #Truncate to fit data
            if rec_slice.stop is None and rec_slice.step in (None, 1):
                self.counts[0] = len(data)
        elif len(data) > self.counts[0]: #Expand to fit data
            if rec_slice.step in (None, 1):
                self.counts[0] = len(data)

    def create_array(self):
        """Creates a numpy array to hold the data from this slice

        Returns
        =======
        out : numpy.array
            array sized, typed, and dimensioned to hold data from
            this slice
        """
        counts = self.counts
        degen = self.degen
        if self.column:
            counts = self.reorder(counts)
            degen = self.reorder(degen)
        #TODO: Forcing C order for now, revert to using self.column later
        array = numpy.empty(
            [counts[i] for i in range(len(counts)) if not degen[i]],
            self.zvar._np_type(), order='C')
        return numpy.require(array, requirements=('C', 'A', 'W'))

    def convert_input_array(self, buffer):
        """Converts a buffer of raw data from this slice

        EPOCH(16) variables always need to be converted.
        CHAR need converted to Unicode if py3k

        Parameters
        ==========
        buffer : numpy.array
            data as read from the CDF file

        Returns
        =======
        out : numpy.array
            converted data
        """
        result = self._flip_array(buffer)

        #Convert to derived types
        cdftype = self.zvar.type()
        if not self.zvar._raw:
            if cdftype in (const.CDF_CHAR.value, const.CDF_UCHAR.value) and \
                    str != bytes:
                dt = numpy.dtype('U{0}'.format(result.dtype.itemsize))
                result = numpy.require(numpy.char.array(result).decode(),
                                       dtype=dt)
            elif cdftype == const.CDF_EPOCH.value:
                result = lib.v_epoch_to_datetime(result)
            elif cdftype == const.CDF_EPOCH16.value:
                result = lib.v_epoch16_to_datetime(result)
            elif cdftype == const.CDF_TIME_TT2000.value:
                result = lib.v_tt2000_to_datetime(result)
        return result

    def convert_output_array(self, buffer):
        """Convert a buffer of data that will go into this slice

        Parameters
        ==========
        buffer : numpy.array
        data to go into the CDF file

        Returns
        =======
        out : numpy.array
        input with majority flipped and dimensions reversed to be
        suitable to pass directly to CDF library.
        """
        buffer = self._flip_array(buffer)
        return numpy.require(buffer, requirements=('C', 'A', 'W'))

    def _flip_array(self, data):
        """
        Operations for majority, etc. common between convert_input and _output
        """
        cdftype = self.zvar.type()
        #Flip majority if any non-degenerate dimensions exist
        if self.column and not min(self.degen):
            #Record-number dim degen, swap whole thing
            if self.degen[0]:
                if cdftype == const.CDF_EPOCH16.value:
                    #Maintain last dimension
                    data = data.transpose(
                        list(range(len(data.shape) - 2, 0, -1)) +
                        [len(data.shape) - 1]
                        )
                else:
                    data = data.transpose()
            #Record-number dimension is not degenerate, so keep it first
            else:
                if cdftype == const.CDF_EPOCH16.value:
                    data = data.transpose(
                        [0] + list(range(len(data.shape) - 2, 0, -1)) +
                        [len(data.shape) - 1]
                        )
                else:
                    data = data.transpose(
                        [0] + list(range(len(data.shape) - 1, 0, -1)))
        #Reverse non-degenerate dimensions in rev
        #Remember that the degenerate indices are already gone!
        if self.rev.any():
            sliced = [(slice(None, None, -1) if self.rev[i] else slice(None))
                      for i in range(self.dims) if not self.degen[i]]
            if cdftype == const.CDF_EPOCH16.value: #don't reverse last dim
                sliced.extend(slice(None))
            data = operator.getitem(data, sliced)
        return data

    def select(self):
        """Selects this hyperslice in the CDF

        Calls the CDF library to select the CDF, variable, records, and
        array elements corresponding to this slice.
        """
        args = (const.SELECT_, const.zVAR_RECNUMBER_, ctypes.c_long(self.starts[0]),
                const.SELECT_, const.zVAR_RECCOUNT_, ctypes.c_long(self.counts[0]),
                const.SELECT_, const.zVAR_RECINTERVAL_,
                ctypes.c_long(self.intervals[0]))
        if self.dims > 1:
            dims = self.dims - 1
            args += (const.SELECT_, const.zVAR_DIMINDICES_,
                     (ctypes.c_long * dims)(*self.starts[1:]),
                     const.SELECT_, const.zVAR_DIMCOUNTS_,
                     (ctypes.c_long * dims)(*self.counts[1:]),
                     const.SELECT_, const.zVAR_DIMINTERVALS_,
                     (ctypes.c_long * dims)(*self.intervals[1:]))
        self.zvar._call(*args)

    @staticmethod
    def expand_ellipsis(slices, n_dims):
        """Expands any ellipses into correct number of full-size slices

        @param slices: tuple of slices, integers, or ellipse objects
        @type slices: tuple
        @param n_dims: number of dimensions this slice is over
        @type n_dims: int
        @return: L{slices} with ellipses replaced by appropriate number of
                 full-dimension slices
        @rtype: tuple
        @raise IndexError: if ellipses specified when already have enough
                           dimensions
        """
        if slices is Ellipsis:
            return tuple([slice(None, None, None)
                          for i in range(n_dims)])
        #Elements might be numpy arrays, so can't use in/index
        idx = [i for i, v in enumerate(slices) if v is Ellipsis]
        if not idx: #no ellipsis
            return slices
        if len(idx) > 1: #multiples!
            raise IndexError('Ellipses can only be used once per slice.')
        idx = idx[0]

        #how many dims to expand ellipsis to
        #remember the ellipsis is in len(slices) and must be replaced!
        extra = n_dims - len(slices) + 1
        if extra < 0:
            raise IndexError('too many indices')
        result = slices[0:idx] + (slice(None), ) * extra + slices[idx+1:]
        return result

    @staticmethod
    def check_well_formed(data):
        """Checks if input data is well-formed, regular array"""
        d = numpy.asanyarray(data)
        if d.dtype == numpy.object: #this is probably going to be bad
            try:
                len(d.flat[0])
            except TypeError: #at least it's not a list
                pass
            else:
                raise ValueError(
                    'Data must be well-formed, regular array of number, '
                    'string, or datetime')

    @staticmethod
    def dimensions(data):
        """Finds the dimensions of a nested list-of-lists

        @param data: data of which dimensions are desired
        @type data: list (of lists)
        @return: dimensions of L{data}, in order outside-in
        @rtype: list of int
        @raise ValueError: if L{data} has irregular dimensions
        """
        d = numpy.asanyarray(data)
        _Hyperslice.check_well_formed(d)
        return d.shape

    @staticmethod
    def types(data, backward=False):
        """Find dimensions and valid types of a nested list-of-lists

        Any given data may be representable by a range of CDF types; infer
        the CDF types which can represent this data. This breaks down to:
          1. Proper kind (numerical, string, time)
          2. Proper range (stores highest and lowest number)
          3. Sufficient resolution (EPOCH16 required if datetime has
             microseconds or below.)

        If more than one value satisfies the requirements, types are returned
        in preferred order:
          1. Type that matches precision of data first, then
          2. integer type before float type, then
          3. Smallest type first, then
          4. signed type first, then
          5. specifically-named (CDF_BYTE) vs. generically named (CDF_INT1)
        So for example, EPOCH_16 is preferred over EPOCH if L{data} specifies
        below the millisecond level (rule 1), but otherwise EPOCH is preferred
        (rule 2).

        For floats, four-byte is preferred unless eight-byte is required:
          1. absolute values between 0 and 3e-39
          2. absolute values greater than 1.7e38
        This will switch to an eight-byte double in some cases where four bytes
        would be sufficient for IEEE 754 encoding, but where DEC formats would
        require eight.

        @param data: data for which dimensions and CDF types are desired
        @type data: list (of lists)
        @param backward: limit to pre-CDF3 types
        @type backward: bool
        @return: dimensions of L{data}, in order outside-in;
                 CDF types which can represent this data;
                 number of elements required (i.e. length of longest string)
        @rtype: 3-tuple of lists ([int], [ctypes.c_long], [int])
        @raise ValueError: if L{data} has irregular dimensions
        """
        d = numpy.asanyarray(data)
        dims = d.shape
        elements = 1
        types = []

        _Hyperslice.check_well_formed(d)
        if d.dtype.kind in ('S', 'U'): #it's a string
            types = [const.CDF_CHAR, const.CDF_UCHAR]
            elements = d.dtype.itemsize
            if d.dtype.kind == 'U': #UTF-8 uses 4 bytes per
                elements //= 4
        elif d.size and hasattr(numpy.ma.getdata(d).flat[0], 'microsecond'):
            if max((dt.microsecond % 1000 for dt in d.flat)) > 0:
                types = [const.CDF_EPOCH16, const.CDF_EPOCH,
                         const.CDF_TIME_TT2000]
            else:
                types = [const.CDF_EPOCH, const.CDF_EPOCH16,
                         const.CDF_TIME_TT2000]
            if backward:
                del types[types.index(const.CDF_EPOCH16)]
                del types[-1]
            if not lib.supports_int8:
                del types[-1]
        elif d is data: #numpy array came in, use its type
            types = [k for k in lib.numpytypedict
                     if lib.numpytypedict[k] == d.dtype
                     and not k in lib.timetypes]

        if not types: #not a numpy array, or can't parse its type
            if d.dtype.kind in ('i', 'u'): #integer
                minval = numpy.min(d)
                maxval = numpy.max(d)
                if minval < 0:
                    types = [const.CDF_BYTE, const.CDF_INT1,
                             const.CDF_INT2, const.CDF_INT4, const.CDF_INT8,
                             const.CDF_FLOAT, const.CDF_REAL4,
                             const.CDF_DOUBLE, const.CDF_REAL8]
                    cutoffs = [2 ** 7, 2 ** 7, 2 ** 15, 2 ** 31, 2 ** 63,
                               1.7e38, 1.7e38, 8e307, 8e307]
                else:
                    types = [const.CDF_BYTE, const.CDF_INT1, const.CDF_UINT1,
                             const.CDF_INT2, const.CDF_UINT2,
                             const.CDF_INT4, const.CDF_UINT4,
                             const.CDF_INT8,
                             const.CDF_FLOAT, const.CDF_REAL4,
                             const.CDF_DOUBLE, const.CDF_REAL8]
                    cutoffs = [2 ** 7, 2 ** 7, 2 ** 8,
                               2 ** 15, 2 ** 16, 2 ** 31, 2 ** 32, 2 ** 63,
                               1.7e38, 1.7e38, 8e307, 8e307]
                types = [t for (t, c) in zip(types, cutoffs) if c > maxval]
                if (not lib.supports_int8 or backward) \
                       and const.CDF_INT8 in types:
                    del types[types.index(const.CDF_INT8)]
            else: #float
                if dims is ():
                    if d != 0 and (abs(d) > 1.7e38 or abs(d) < 3e-39):
                        types = [const.CDF_DOUBLE, const.CDF_REAL8]
                    else:
                        types = [const.CDF_FLOAT, const.CDF_REAL4,
                                 const.CDF_DOUBLE, const.CDF_REAL8]
                else:
                    absolutes = numpy.abs(d[d != 0])
                    if len(absolutes) > 0 and \
                           (numpy.max(absolutes) > 1.7e38 or
                            numpy.min(absolutes) < 3e-39):
                        types = [const.CDF_DOUBLE, const.CDF_REAL8]
                    else:
                        types = [const.CDF_FLOAT, const.CDF_REAL4,
                                 const.CDF_DOUBLE, const.CDF_REAL8]
        types = [t.value if hasattr(t, 'value') else t for t in types]
        return (dims, types, elements)

    @staticmethod
    def reorder(seq):
        """Reorders seq to switch array majority

        Used to take an array of subscripts between row
        and column majority. First element is not touched,
        being the record number.

        @param seq: a sequence of *subscripts*
        @type seq: sequence of integers
        @return: seq with all but element 0 reversed in order
        @rtype: sequence of integers
        """
        return numpy.concatenate((seq[0:1],
                                  numpy.flipud(seq)[:-1]))

    @staticmethod
    def convert_range(start, stop, step, size):
        """Converts a start/stop/step range to start/count/interval

        (i.e. changes from Python-style slice to CDF-style)
        @param start: index to start a slice at, may be none or negative
        @type start: int
        @param stop: index at end of slice (one-past, standard Python),
                     may be none or negative
        @type stop: int
        @param step: interval for stepping through stlice
        @type step: int
        @param size: size of list to slice
        @type size: int
        @return: (start, count, interval, rev) where:
                   1. start is the start index, normalized to be within
                      the size of the list and negatives handled
                   2. count is the number of records in the slice,
                      guaranteed to stop before the end
                   3. interval is the skip between records
                   4. rev indicates whether the sequence should be reversed
        @rtype: (int, int, int, boolean)
        """
        (start, stop, step) = slice(start, stop, step).indices(size)
        if step < 0:
            step *= -1
            count = int((start - stop + step - 1) / step)
            start = start - (count - 1) * step
            rev = True
        else:
            count = int((stop - start + step - 1) / step)
            rev = False
        if count < 0:
            count = 0
            start = 0
        return (start, count, step, rev)


class Attr(collections.MutableSequence):
    """An attribute, g or z, for a CDF

    .. warning::
        This class should not be used directly, but only in its
        subclasses, :class:`gAttr` and :class:`zAttr`. The methods
        listed here are safe to use in the subclasses.

    Represents a CDF attribute, providing access to the Entries in a format
    that looks like a Python
    list. General list information is available in the python docs:
    `1 <http://docs.python.org/tutorial/introduction.html#lists>`_,
    `2 <http://docs.python.org/tutorial/datastructures.html#more-on-lists>`_,
    `3 <http://docs.python.org/library/stdtypes.html#typesseq>`_.

    An introduction to CDF attributes can be found in section 2.4 of
    the CDF user's guide.

    Each element of the list is a single Entry of the appropriate type.
    The index to the elements is the Entry number.

    Multi-dimensional slicing is *not* supported; an Entry with multiple
    elements will have all elements returned (and can thus be sliced itself).
    Example:

        >>> first_three = attribute[5, 0:3] #will fail
        >>> first_three = attribute[5][0:3] #first three elements of 5th Entry

    .. autosummary::

        ~Attr.has_entry
        ~Attr.max_idx
        ~Attr.new
        ~Attr.number
        ~Attr.rename
        ~Attr.type

    .. automethod:: has_entry
    .. automethod:: max_idx
    .. automethod:: new
    .. automethod:: number
    .. automethod:: rename
    .. automethod:: type
    """

    def __init__(self, cdf_file, attr_name, create=False):
        """Initialize this attribute

        @param cdf_file: CDF file containing this attribute
        @type cdf_file: :py:class:`pycdf.CDF`
        @param attr_name: Name of this attribute
        @type attr_name: str
        @param create: True to create attribute, False to look up existing.
        @type create: bool
        """
        self._cdf_file = cdf_file
        self._raw = False
        if isinstance(attr_name, str_classes):
            try:
                self._name = attr_name.encode('ascii')
            except AttributeError:
                self._name = attr_name
            if create:
                attrno = ctypes.c_long(0)
                self._cdf_file._call(const.CREATE_, const.ATTR_,
                                     self._name, self.SCOPE,
                                     ctypes.byref(attrno))
            else:
                self._cdf_file._call(const.CONFIRM_, const.ATTR_EXISTENCE_,
                                     self._name)
        else:
            name = ctypes.create_string_buffer(const.CDF_ATTR_NAME_LEN256 + 1)
            self._cdf_file._call(const.SELECT_, const.ATTR_,
                                 ctypes.c_long(attr_name))
            self._cdf_file._call(const.GET_, const.ATTR_NAME_, name)
            self._name = name.value.rstrip()

    def __getitem__(self, key):
        """Return a slice of Entries.

        Because Attributes may be sparse, a multi-element slice will return
        None for those elements which do not have associated Entries.

        @param key: index or range of Entry number to return
        @type key: slice or int
        @return: a list of entries, appropriate type.
        @raise IndexError: if L{key} is an int and that Entry number does not
                           exist.
        """
        if hasattr(key, 'indices'):
            idx = range(*key.indices(self.max_idx() + 1))
            return [self._get_entry(i) if self.has_entry(i) else None
                    for i in idx]
        else:
            if self.has_entry(key):
                return self._get_entry(key)
            else:
                raise IndexError('list index ' + str(key) + ' out of range.')

    def _check_other_entries(self, types):
        """Try to get the type of this entry from others in the Attribute

        For zAttrs, checks if all other Entries are the same type, and at
        least one doesn't match its zVar, i.e. Entry type dominates (otherwise
        assumption is the Var type dominates).

        For gAttrs, checks all other Entries, and gives priority to the
        one that's earliest in the possible type list and exists in other
        Entries.

        This is only one component of Entry type guessing!

        :param list types: CDF types that are candidates (match the data)
        :return: The type discerned from other Entries, or None
        """
        if self.ENTRY_ == const.zENTRY_:
            #If everything else is the same entry type,
            #and one is not the same as its var, probably
            #all entries should be of that type
            cand_et = None #The Entry type that might work
            one_var_diff = False #One Var has a type different from Entry
            for num in range(self.max_idx() + 1):
                if not self.has_entry(num):
                    continue
                vartype = self._cdf_file[num].type()
                entrytype = self.type(num)
                if vartype != entrytype:
                    one_var_diff = True
                if cand_et is None:
                    if not entrytype in types:
                        return None #One var has Entry with "impossible" type
                    cand_et = entrytype
                elif cand_et != entrytype:
                    return None #Two vars have Entries with different types
            if one_var_diff and cand_et is not None:
                return cand_et
        else:
            # Of those types which exist in other entries,
            # find the one which is earliest
            # in types, i.e. the preferred type
            entrytypes = [self.type(num) for num in
                          range(self.max_idx() + 1)
                          if self.has_entry(num)]
            entrytypes = [et for et in entrytypes if et in types]
            if entrytypes:
                return types[
                    min([types.index(et) for et in entrytypes])]
        return None

    def __setitem__(self, key, data):
        """Set a slice of Entries.

        @param key: index or range of Entry numbers to set
        @type key: slice or int
        @param data: the data to set these entries to. Normally each entry should
        be a sequence; if a scalar is provided, it is treated
        as a single-element list.
        @type data: scalar or list
        @raise ValueError: if size of {data} does not match size of L{key}
        @note: Attributes do not 'grow' or 'shrink' as entries are added
               or removed. Indexes of entries never change and there is no
               way to 'insert'.
        """
        if key is Ellipsis:
            key = slice(None, None, None)
        if not hasattr(key, 'indices'):
            #Single value, promote everything a dimension
            idx = (key, key + 1, 1)
            data = [data]
        else:
            idx = key.indices(self.max_idx() + 1)
            if key.step is None or key.step > 0:
                #Iterating forward, extend slice to match data
                if len(data) > len(range(*idx)):
                    idx = (idx[0], idx[0] + idx[2] * len(data), idx[2])

        #get, and check, types and sizes for all data
        #checks first so don't have error after changing half the Entries
        data_idx = -1
        typelist = []
        for i in range(*idx):
            data_idx += 1
            if data_idx >= len(data):
                continue
            datum = data[data_idx]
            if datum is None:
                typelist[i] = (None, None, None)
                continue
            (dims, types, elements) = _Hyperslice.types(
                datum, backward=self._cdf_file.backward)
            if len(types) <= 0:
                raise ValueError('Cannot find a matching CDF type.')
            if len(dims) > 1:
                raise ValueError('Entries must be scalar or 1D.')
            elif len(dims) == 1 and isinstance(datum[0], str_classes):
                raise ValueError('Entry strings must be scalar.')
            entry_type = None
            if self.has_entry(i): #If the entry already exists, match its type
                entry_type = self.type(i)
                if not entry_type in types:
                    entry_type = None
            if entry_type is None: #Check other entries for this attribute
                entry_type = self._check_other_entries(types)
            if entry_type is None and self.ENTRY_ == const.zENTRY_:
                #Fall back to zVar type
                vartype = self._cdf_file[i].type()
                if vartype in types:
                    entry_type = vartype
                else:
                    entry_type = types[0]
            elif entry_type is None:
                entry_type = types[0]
            if not entry_type in lib.numpytypedict:
                raise ValueError('Cannot find a matching numpy type.')
            typelist.append((dims, entry_type, elements))

        data_idx = -1
        for i in range(*idx):
            data_idx += 1
            if data_idx >= len(data) or data[data_idx] is None:
                if self.has_entry(i):
                    del self[i]
                continue
            datum = data[data_idx]
            (dims, entry_type, elements) = typelist[data_idx]
            self._write_entry(i, datum, entry_type, dims, elements)

    def __delitem__(self, key):
        """Delete a slice of Entries.

        @param key: index or range of Entry numbers to delete
        @type key: slice or int
        @note: Attributes do not 'grow' or 'shrink' as entries are added
               or removed. Indexes of entries never change and there is no
               way to 'insert'.
        """
        if key is Ellipsis:
            key = slice(None, None, None)
        if not hasattr(key, 'indices'):
            idx = (key, key + 1, 1)
        else:
            idx = key.indices(self.max_idx() + 1)
        for i in range(*idx):
            self._call(const.SELECT_, self.ENTRY_, ctypes.c_long(i),
                       const.DELETE_, self.ENTRY_)

    def __iter__(self, current=0):
        """Iterates over all entries in this Attribute

        Returns data from one entry at a time until reaches the end.
        @note: Returned in entry-number order.
        """
        while current <= self.max_idx():
            if self.has_entry(current):
                value = yield(self._get_entry(current))
                if value != None:
                    current = value
            current += 1

    def __reversed__(self, current=None):
        """Iterates over all entries in this Attribute

        Returns data from one entry at a time, starting at end and going
        to beginning.
        @note: Returned in entry-number order.
        """
        if current is None:
            current = self.max_idx()
        while current >= 0:
            if self.has_entry(current):
                value = yield(self._get_entry(current))
                if value != None:
                    current = value
            current -= 1

    def __len__(self):
        """Number of Entries for this Attr. NOT same as max Entry number.

        @return: Number of Entries
        @rtype: int
        """
        count = ctypes.c_long(0)
        self._call(const.GET_, self.ATTR_NUMENTRIES_, ctypes.byref(count))
        return count.value

    def __repr__(self):
        """Returns representation of an attribute

        Cannot return anything that can be eval'd to create a copy of the
        attribtute, so just wrap the informal representation in angle brackets.
        @return: all the data in this attribute
        @rtype: str
        """
        return '<\n' + str(self) + '\n>'

    def __str__(self):
        """Returns a string representation of the attribute

        This is an 'informal' representation in that it cannot be evaluated
        directly to create an L{Attr}.

        @return: all the data in this attribute
        @rtype: str
        """
        if self._cdf_file._opened:
            return '\n'.join([str(item) for item in self])
        else:
            if isinstance(self._name, str):
                return 'Attribute "{0}" in closed CDF {1}'.format(
                    self._name, self._cdf_file.pathname)
            else:
                return 'Attribute "{0}" in closed CDF {1}'.format(
                    self._name.decode('ascii'),
                    self._cdf_file.pathname.decode('ascii'))

    def insert(self, index, data):
        """Insert an entry at a particular number

        Entry numbers do not change on insertion/deletion, so this function
        cannot be implemented.
        @raise NotImplementedError: always
        """
        raise NotImplementedError

    def _call(self, *args, **kwargs):
        """Select this CDF and Attr and call the CDF internal interface

        @param args: Passed directly to the CDF library interface.
        @type args: various, see :py:mod:`ctypes`.
        @return: CDF status from the library
        @rtype: ctypes.c_long
        @note: Terminal NULL_ is automatically added to L{args}.
        @raise CDFError: if CDF library reports an error
        @raise CDFWarning: if CDF library reports a warning and interpreter
                           is set to error on warnings.
        """
        return self._cdf_file._call(
            const.SELECT_, const.ATTR_NAME_, self._name,
            *args, **kwargs)

    def _entry_len(self, number):
        """Number of elements in an Entry

        @param number: number of Entry
        @type number: int
        @return: number of elements
        @rtype: int
        """
        if not self.has_entry(number):
            raise IndexError('list index ' + str(number) + ' out of range.')
        count = ctypes.c_long(0)
        self._call(
            const.SELECT_, self.ENTRY_, number,
            const.GET_, self.ENTRY_NUMELEMS_, ctypes.byref(count))
        return count.value

    def type(self, number, new_type=None):
        """Find or change the CDF type of a particular Entry number

        Parameters
        ==========
        number : int
            number of Entry to check or change

        Other Parameters
        ================
        new_type
            type to change this Entry to, from :mod:`~spacepy.pycdf.const`.
            Omit to only check type.

        Returns
        =======
        out : int
            CDF variable type, see :mod:`~spacepy.pycdf.const`

        Notes
        =====
        If changing types, old and new must be equivalent, see CDF
        User's Guide section 2.5.5 pg. 57
        """
        if new_type != None:
            if not hasattr(new_type, 'value'):
                new_type = ctypes.c_long(new_type)
            size = ctypes.c_long(self._entry_len(number))
            status = self._call(const.SELECT_, self.ENTRY_, ctypes.c_long(number),
                                const.PUT_, self.ENTRY_DATASPEC_, new_type, size,
                                ignore=(const.NO_SUCH_ENTRY,))
            if status == const.NO_SUCH_ENTRY:
                raise IndexError('list index ' + str(number) + ' out of range.')
        cdftype = ctypes.c_long(0)
        status = self._call(const.SELECT_, self.ENTRY_, ctypes.c_long(number),
                            const.GET_, self.ENTRY_DATATYPE_, ctypes.byref(cdftype),
                            ignore=(const.NO_SUCH_ENTRY,))
        if status == const.NO_SUCH_ENTRY:
            raise IndexError('list index ' + str(number) + ' out of range.')
        return cdftype.value

    def has_entry(self, number):
        """Check if this attribute has a particular Entry number

        Parameters
        ==========
        number : int
            number of Entry to check or change

        Returns
        =======
        out : bool
            True if ``number`` is a valid entry number; False if not
        """
        status = self._call(const.CONFIRM_, self.ENTRY_EXISTENCE_,
                            ctypes.c_long(number),
                            ignore=(const.NO_SUCH_ENTRY, ))
        return not status == const.NO_SUCH_ENTRY

    def max_idx(self):
        """Maximum index of Entries for this Attr

        Returns
        =======
        out : int
            maximum Entry number
        """
        count = ctypes.c_long(0)
        self._call(const.GET_, self.ATTR_MAXENTRY_, ctypes.byref(count))
        return count.value

    def new(self, data, type=None, number=None):
        """Create a new Entry in this Attribute

        .. note:: If ``number`` is provide and an Entry with that number
                  already exists, it will be overwritten.

        Parameters
        ==========
        data
            data to put in the Entry

        Other Parameters
        ================
        type : int
            type of the new Entry, from :mod:`~spacepy.pycdf.const`
            (otherwise guessed from ``data``)
        number : int
            Entry number to write, default is lowest available number.
        """
        if number is None:
            number = 0
            while self.has_entry(number):
                number += 1
        (dims, types, elements) = _Hyperslice.types(
            data, backward=self._cdf_file.backward)
        if type is None:
            #Guess based on other entries
            type = self._check_other_entries(types)
        if type is None and self.ENTRY_ == const.zENTRY_:
            #Try to match variable type
                vartype = self._cdf_file[number].type()
                if vartype in types:
                    type = vartype
        if type is None:
            type = types[0]
        elif hasattr(type, 'value'):
            type = type.value
        self._write_entry(number, data, type, dims, elements)

    def number(self):
        """Find the attribute number for this attribute

        Returns
        =======
        out : int
            attribute number
        """
        no = ctypes.c_long(0)
        self._cdf_file._call(const.GET_, const.ATTR_NUMBER_,
                             self._name, ctypes.byref(no))
        return no.value

    def global_scope(self):
        """Determine scope of this attribute.

        Returns
        =======
        out : bool
            True if global (i.e. gAttr), False if zAttr
        """
        scope = ctypes.c_long(0)
        self._call(const.GET_, const.ATTR_SCOPE_, ctypes.byref(scope))
        if scope.value == const.GLOBAL_SCOPE.value:
            return True
        elif scope.value == const.VARIABLE_SCOPE.value:
            return False
        else:
            raise CDFError(const.BAD_SCOPE)

    def rename(self, new_name):
        """Rename this attribute

        Renaming a zAttribute renames it for *all* zVariables in this CDF!

        Parameters
        ==========
        new_name : str
             the new name of the attribute
        """
        try:
            enc_name = new_name.encode('ascii')
        except AttributeError:
            enc_name = new_name
        if len(enc_name) > const.CDF_ATTR_NAME_LEN256:
            raise CDFError(const.BAD_ATTR_NAME)
        self._call(const.PUT_, const.ATTR_NAME_, enc_name)
        self._name = enc_name

    def _get_entry(self, number):
        """Read an Entry associated with this L{Attr}

        @param number: number of Entry to return
        @type number: int
        @return: data from entry numbered L{number}
        @rtype: list or str
        """
        if not self.has_entry(number):
            raise IndexError('list index ' + str(number) + ' out of range.')
        #Make a big enough buffer
        length = self._entry_len(number)
        cdftype = self.type(number)
        if cdftype in (const.CDF_CHAR.value, const.CDF_UCHAR.value):
            buff = numpy.empty((), 'S{0}'.format(length), order='C')
        else:
            if not cdftype in lib.numpytypedict:
                raise CDFError(const.BAD_DATA_TYPE)
            buff = numpy.empty((length,), lib.numpytypedict[cdftype],
                               order='C')
        buff = numpy.require(buff, requirements=('C', 'A', 'W'))
        self._call(const.SELECT_, self.ENTRY_, number,
                   const.GET_, self.ENTRY_DATA_,
                   buff.ctypes.data_as(ctypes.c_void_p))

        #decode
        if cdftype in (const.CDF_CHAR.value, const.CDF_UCHAR.value):
            if str == bytes or self._raw: #Py2k, leave as bytes
                result = bytes(buff)
            else: #Py3k, make unicode
                result = str(numpy.char.array(buff).decode())
        else:
            if not self._raw:
                if cdftype == const.CDF_EPOCH.value:
                    result = lib.v_epoch_to_datetime(buff)
                elif cdftype == const.CDF_EPOCH16.value:
                    result = lib.v_epoch16_to_datetime(buff)
                elif cdftype == const.CDF_TIME_TT2000.value:
                    result = lib.v_tt2000_to_datetime(buff)
                else:
                    result = buff
            else:
                result = buff
            if length == 1:
                result = result[0]

        return result

    def _write_entry(self, number, data, cdf_type, dims, elements):
        """Write an Entry to this Attr.

        @param number: number of Entry to write
        @type number: int
        @param data: data to write
        @param cdf_type: the CDF type to write, from :py:mod:`pycdf.const`
        @param dims: dimensions of L{data}
        @type dims: list
        @param elements: number of elements in L{data}, 1 unless it is a string
        @type elements: int
        """
        if len(dims) == 0:
            n_write = 1
        else:
            n_write = dims[0]
        if cdf_type in (const.CDF_CHAR.value, const.CDF_UCHAR.value):
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.dtype('S' + str(elements)))
            n_write = elements
        elif cdf_type == const.CDF_EPOCH16.value:
            if not self._raw:
                try:
                    data = lib.v_datetime_to_epoch16(data)
                except AttributeError:
                    pass
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.float64)
        elif cdf_type == const.CDF_EPOCH.value:
            if not self._raw:
                try:
                    data = lib.v_datetime_to_epoch(data),
                except AttributeError:
                    pass
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.float64)
        elif cdf_type == const.CDF_TIME_TT2000.value:
            if not self._raw:
                try:
                    data = lib.v_datetime_to_tt2000(data)
                except AttributeError:
                    pass
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=numpy.int64)
        elif cdf_type in lib.numpytypedict:
            data = numpy.require(data, requirements=('C', 'A', 'W'),
                                 dtype=lib.numpytypedict[cdf_type])
        else:
            raise CDFError(const.BAD_DATA_TYPE)
        self._call(const.SELECT_, self.ENTRY_, ctypes.c_long(number),
                   const.PUT_, self.ENTRY_DATA_, ctypes.c_long(cdf_type),
                   ctypes.c_long(n_write),
                   data.ctypes.data_as(ctypes.c_void_p))

    def _delete(self):
        """Delete this Attribute

        Also deletes all Entries associated with it.
        """
        self._call(const.DELETE_, const.ATTR_)


class zAttr(Attr):
    """zAttribute for zVariables within a CDF.

    .. warning::
        Because zAttributes are shared across all variables in a CDF,
        directly manipulating them may have unexpected consequences.
        It is safest to operate on zEntries via :class:`zAttrList`.

    .. note::
        When accessing a zAttr, pyCDF exposes only the zEntry corresponding
        to the associated zVariable.

    See Also
    ========
    :class:`Attr`
    """

    def __init__(self, *args, **kwargs):
        """Initialize this attribute"""
        self.ENTRY_ = const.zENTRY_
        self.ENTRY_DATA_ = const.zENTRY_DATA_
        self.SCOPE = const.VARIABLE_SCOPE
        self.ENTRY_EXISTENCE_ = const.zENTRY_EXISTENCE_
        self.ATTR_NUMENTRIES_ = const.ATTR_NUMzENTRIES_
        self.ATTR_MAXENTRY_ = const.ATTR_MAXzENTRY_
        self.ENTRY_NUMELEMS_ = const.zENTRY_NUMELEMS_
        self.ENTRY_DATATYPE_ = const.zENTRY_DATATYPE_
        self.ENTRY_DATASPEC_ = const.zENTRY_DATASPEC_
        super(zAttr, self).__init__(*args, **kwargs)


class gAttr(Attr):
    """Global Attribute for a CDF

    Represents a CDF attribute, providing access to the gEntries in a format
    that looks like a Python list. General list information is available in
    the python docs:
    `1 <http://docs.python.org/tutorial/introduction.html#lists>`_,
    `2 <http://docs.python.org/tutorial/datastructures.html#more-on-lists>`_,
    `3 <http://docs.python.org/library/stdtypes.html#typesseq>`_.

    Normally accessed by providing a key to a :class:`gAttrList`:

        >>> attribute = cdffile.attrs['attribute_name']
        >>> first_gentry = attribute[0]

    Each element of the list is a single gEntry of the appropriate type.
    The index to the elements is the gEntry number.

    A gEntry may be either a single string or a 1D array of numerical type.
    Entries of numerical type (everything but CDF_CHAR and CDF_UCHAR)
    with a single element are returned as scalars; multiple-element entries
    are returned as a list. No provision is made for accessing below
    the entry level; the whole list is returned at once (but Python's
    slicing syntax can be used to extract individual items from that list.)

    Multi-dimensional slicing is *not* supported; an entry with multiple
    elements will have all elements returned (and can thus be sliced itself).
    Example:

        >>> first_three = attribute[5, 0:3] #will fail
        >>> first_three = attribute[5][0:3] #first three elements of 5th Entry

    gEntries are *not* necessarily contiguous; a gAttribute may have an
    entry 0 and entry 2 without an entry 1. :meth:`~Attr.len` will return the
    *number* of gEntries; use :meth:`~Attr.max_idx` to find the highest defined
    gEntry number and :meth:`~Attr.has_entry` to determine if a particular
    gEntry number exists. Iterating over all entries is also supported::

        >>> entrylist = [entry for entry in attribute]

    Deleting gEntries will leave a "hole":

        >>> attribute[0:3] = [1, 2, 3]
        >>> del attribute[1]
        >>> attribute.has_entry(1)
        False
        >>> attribute.has_entry(2)
        True
        >>> print attribute[0:3]
        [1, None, 3]

    Multi-element slices over nonexistent gEntries will return ``None`` where
    no entry exists. Single-element indices for nonexistent gEntries will
    raise ``IndexError``. Assigning ``None`` to a gEntry will delete it.

    When assigning to a gEntry, the type is chosen to match the data;
    subject to that constraint, it will try to match
    (in order):

        #. existing gEntry of the same number in this gAttribute
        #. other gEntries in this gAttribute
        #. data-matching constraints described in :meth:`CDF.new`.

    See Also
    ========
    :class:`Attr`
    """

    def __init__(self, *args, **kwargs):
        """Initialize this attribute"""
        self.ENTRY_ = const.gENTRY_
        self.ENTRY_DATA_ = const.gENTRY_DATA_
        self.SCOPE = const.GLOBAL_SCOPE
        self.ENTRY_EXISTENCE_ = const.gENTRY_EXISTENCE_
        self.ATTR_NUMENTRIES_ = const.ATTR_NUMgENTRIES_
        self.ATTR_MAXENTRY_ = const.ATTR_MAXgENTRY_
        self.ENTRY_NUMELEMS_ = const.gENTRY_NUMELEMS_
        self.ENTRY_DATATYPE_ = const.gENTRY_DATATYPE_
        self.ENTRY_DATASPEC_ = const.gENTRY_DATASPEC_
        super(gAttr, self).__init__(*args, **kwargs)


class AttrList(collections.MutableMapping):
    """Object representing a list of attributes.

    .. warning::
        This class should not be used directly, but only via its
        subclasses, :class:`gAttrList` and :class:`zAttrList`.
        Methods listed here are safe to use from the subclasses.

    .. autosummary::

        ~AttrList.clone
        ~AttrList.copy
        ~AttrList.from_dict
        ~AttrList.new
        ~AttrList.rename

    .. automethod:: clone
    .. automethod:: copy
    .. automethod:: from_dict
    .. automethod:: new
    .. automethod:: rename
    """

    def __init__(self, cdf_file, special_entry=None):
        """Initialize the attribute collection

        @param cdf_file: CDF these attributes are in
        @type cdf_file: :py:class:`pycdf.CDF`
        @param special_entry: callable which returns a "special" entry number,
        used to limit results for zAttrs to those which match the zVar
        @type special_entry: callable
        """
        self._cdf_file = cdf_file
        self.special_entry = special_entry

    def __getitem__(self, name):
        """Find an Attribute by name

        @param name: name of the Attribute to return
        @type name: str
        @return: attribute named L{name}
        @rtype: L{Attr}
        @raise KeyError: if there is no attribute named L{name}
        @raise CDFError: other errors in CDF library
        """
        try:
            attrib = self.AttrType(self._cdf_file, name)
        except CDFError:
            (t, v, tb) = sys.exc_info()
            if v.status == const.NO_SUCH_ATTR:
                raise KeyError(name + ': ' + str(v))
            else:
                raise
        if attrib.global_scope() != self.global_scope:
            raise KeyError(name + ': no ' + self.attr_name + ' by that name.')
        return attrib

    def __setitem__(self, name, data):
        """Create an Attribute or change its entries

        @param name: name of Attribute to change
        @type name: str
        @param data: Entries to populate this Attribute with.
                     Any existing Entries will be deleted!
                     Another C{Attr} may be specified, in which
                     case all its entries are copied.
        @type data: scalar, list, or L{Attr}
        """
        if isinstance(data, AttrList):
            if name in self:
                del self[name]
            attr = self._get_or_create(name)
            for entryno in range(data.max_idx()):
                if data.has_entry(entryno):
                    attr.new(data[entryno], data.type(entryno), entryno)
        else:
            attr = self._get_or_create(name)
            if isinstance(data, str_classes):
                data = [data]
            else:
                try:
                    junk = len(data)
                except TypeError:
                    data = [data]
            attr[:] = data
            del attr[len(data):]

    def __delitem__(self, name):
        """Delete an Attribute (and all its entries)

        @param name: name of Attribute to delete
        @type name: str
        """
        try:
            attr = self.AttrType(self._cdf_file, name)
        except CDFError:
            (t, v, tb) = sys.exc_info()
            if v.status == const.NO_SUCH_ATTR:
                raise KeyError(name + ': ' + str(v))
            else:
                raise
            if attr.global_scope() != self.global_scope:
                raise KeyError(name + ': not ' + self.attr_name)
        attr._delete()

    def __iter__(self, current=0):
        """Iterates over all Attr in this CDF or variable

        Returns name of one L{Attr} at a time until reaches the end.
        @note: Returned in number order.
        """
        count = ctypes.c_long(0)
        self._cdf_file._call(const.GET_, const.CDF_NUMATTRS_,
                             ctypes.byref(count))
        while current < count.value:
            candidate = self.AttrType(self._cdf_file, current)
            if candidate.global_scope() == self.global_scope:
                if self.special_entry is None or \
                        candidate.has_entry(self.special_entry()):
                    if str == bytes:
                        value = yield(candidate._name)
                    else:
                        value = yield(candidate._name.decode())
                    if value != None:
                        current = self[value].number()
            current += 1

    def __repr__(self):
        """Returns representation of attribute list

        Cannot return anything that can be eval'd to create a copy of the
        list, so just wrap the informal representation in angle brackets.
        @return: all the data in this list of attributes
        @rtype: str
        """
        return '<' + self.__class__.__name__ + ':\n' + str(self) + '\n>'

    def __str__(self):
        """Returns a string representation of the attribute list

        This is an 'informal' representation in that it cannot be evaluated
        directly to create an L{AttrList}.

        @return: all the data in this list of attributes
        @rtype: str
        """
        if self._cdf_file._opened:
            return '\n'.join([key + ': ' + (
                ('\n' + ' ' * (len(key) + 2)).join(
                [str(value[i]) + ' [' + lib.cdftypenames[value.type(i)] + ']'
                 for i in range(value.max_idx() + 1) if value.has_entry(i)])
                if isinstance(value, Attr)
                else str(value) +
                ' [' + lib.cdftypenames[self.type(key)] + ']'
                )
                for (key, value) in sorted(self.items())])
        else:
            if isinstance(self._cdf_file.pathname, str):
                return 'Attribute list in closed CDF {0}'.format(
                    self._cdf_file.pathname)
            else:
                return 'Attribute list in closed CDF {0}'.format(
                    self._cdf_file.pathname.decode('ascii'))

    def clone(self, master, name=None, new_name=None):
        """
        Clones another attribute list, or one attribute from it, into this
        list.

        Parameters
        ==========
        master : AttrList
            the attribute list to copy from. This can be any dict-like object.

        Other Parameters
        ================
        name : str (optional)
            name of attribute to clone (default: clone entire list)
        new_name : str (optional)
            name of the new attribute, default ``name``
        """
        if name is None:
            self._clone_list(master)
        else:
            self._clone_attr(master, name, new_name)

    def copy(self):
        """
        Create a copy of this attribute list

        Returns
        =======
        out : dict
            copy of the entries for all attributes in this list
        """
        return dict((key, value[:] if isinstance(value, Attr) else value)
                    for (key, value) in self.items())

    def new(self, name, data=None, type=None):
        """
        Create a new Attr in this AttrList

        Parameters
        ==========
        name : str
            name of the new Attribute

        Other Parameters
        ================
        data
            data to put into the first entry in the new Attribute
        type
            CDF type of the first entry from :mod:`~spacepy.pycdf.const`.
            Only used if data are specified.

        Raises
        ======
        KeyError : if the name already exists in this list
        """
        if name in self:
            raise KeyError(name + ' already exists.')
        attr = self._get_or_create(name)
        if data is not None:
            if self.special_entry is None:
                attr.new(data, type)
            else:
                attr.new(data, type, self.special_entry())

    def rename(self, old_name, new_name):
        """
        Rename an attribute in this list

        Renaming a zAttribute renames it for *all* zVariables in this CDF!

        Parameters
        ==========
        old_name : str
            the current name of the attribute
        new_name : str
            the new name of the attribute
        """
        AttrList.__getitem__(self, old_name).rename(new_name)

    def from_dict(self, in_dict):
        """
        Fill this list of attributes from a dictionary

        .. deprecated:: 0.1.5
           Use :meth:`~spacepy.pycdf.AttrList.clone` instead; it supports
           cloning from dictionaries.

        Parameters
        ==========
        in_dict : dict
            Attribute list is populated entirely from this dictionary;
            all existing attributes are deleted.
        """
        warnings.warn("from_dict is deprecated and will be removed. Use clone.",
                      DeprecationWarning)
        for k in in_dict:
            self[k] = in_dict[k]
        for k in list(self):
            if not k in in_dict:
                del self[k]

    def _clone_attr(self, master, name, new_name=None):
        """Clones a single attribute from one in this list or another

        Copies data and types from the master attribute to the new one

        @param master: attribute list to copy attribute from
        @type master: L{AttrList}
        @param name: name of attribute to copy
        @type name: str
        @param new_name: name of the new attribute, default L{name}
        @type new_name: str
        """
        if new_name is None:
            new_name = name
        self[new_name] = master[name]

    def _clone_list(self, master):
        """Clones this attribute list from another

        @param master: the attribute list to copy from
        @type master: L{AttrList}
        """
        for name in master:
            self._clone_attr(master, name)
        for name in list(self): #Can't iterate over a list we're changing
            if not name in master:
                del self[name]

    def _get_or_create(self, name):
        """Retrieve L{Attr} or create it if it doesn't exist

        @param name: name of the attribute to look up or create
        @type name: str
        @return: attribute with this name
        @rtype: L{Attr}
        """
        attr = None
        try:
            attr = self.AttrType(self._cdf_file, name)
        except CDFError:
            (t, v, tb) = sys.exc_info()
            if v.status != const.NO_SUCH_ATTR:
                raise
        if attr is None:
            attr = self.AttrType(self._cdf_file, name, True)
        elif attr.global_scope() != self.global_scope:
                raise KeyError(name + ': not ' + self.attr_name)
        return attr


class gAttrList(AttrList):
    """
    Object representing *all* the gAttributes in a CDF.

    Normally accessed as an attribute of an open :class:`CDF`:

        >>> global_attribs = cdffile.attrs

    Appears as a dictionary: keys are attribute names; each value is an
    attribute represented by a :class:`gAttr` object. To access the global
    attribute TEXT:

        >>> text_attr = cdffile.attrs['TEXT']

    See Also
    ========
    :class:`AttrList`
    """
    AttrType = gAttr
    attr_name = 'gAttribute'
    global_scope = True

    def __len__(self):
        """
        Number of gAttributes in this CDF

        Returns
        =======
        out : int
            number of gAttributes in the CDF
        """
        count = ctypes.c_long(0)
        self._cdf_file._call(const.GET_, const.CDF_NUMgATTRS_,
                             ctypes.byref(count))
        return count.value


class zAttrList(AttrList):
    """Object representing *all* the zAttributes in a zVariable.

    Normally accessed as an attribute of a :class:`Var` in an open
    CDF:

        >>> epoch_attribs = cdffile['Epoch'].attrs

    Appears as a dictionary: keys are attribute names, values are
    the value of the zEntry associated with the appropriate zVariable.
    Each vAttribute in a CDF may only have a *single* entry associated
    with each variable. The entry may be a string, a single numerical value,
    or a series of numerical values. Entries with multiple values are returned
    as an entire list; direct access to the individual elements is not
    possible.

    Example: finding the first dependency of (ISTP-compliant) variable
    ``Flux``:

        >>> print cdffile['Flux'].attrs['DEPEND_0']

    zAttributes are shared among zVariables, one zEntry allowed per zVariable.
    (pyCDF hides this detail.) Deleting the last zEntry for a zAttribute will
    delete the underlying zAttribute.

    zEntries are created and destroyed by the usual dict methods on the
    zAttrlist:

        >>> epoch_attribs['new_entry'] = [1, 2, 4] #assign a list to new zEntry
        >>> del epoch_attribs['new_entry'] #delete the zEntry

    The type of the zEntry is guessed from data provided. The type is chosen to
    match the data; subject to that constraint, it will try to match
    (in order):

        #. existing zEntry corresponding to this zVar
        #. other zEntries in this zAttribute
        #. the type of this zVar
        #. data-matching constraints described in :py:meth:`CDF.new`

    See Also
    ========
    :class:`AttrList`

    """
    AttrType = zAttr
    attr_name = 'zAttribute'
    global_scope = False

    def __init__(self, zvar):
        """Initialize the attribute collection

        @param zvar: zVariable these attributes are in
        @param zvar: :py:class:`pycdf.Var`
        """
        super(zAttrList, self).__init__(zvar.cdf_file, zvar._num)
        self._zvar = zvar

    def __getitem__(self, name):
        """Find an zEntry by name

        @param name: name of the zAttribute to return
        @type name: str
        @return: attribute named L{name}
        @rtype: L{zAttr}
        @raise KeyError: if there is no attribute named L{name} associated
                         with this zVariable
        @raise CDFError: other errors in CDF library
        """
        attrib = super(zAttrList, self).__getitem__(name)
        zvar_num = self._zvar._num()
        if attrib.has_entry(zvar_num):
            attrib._raw = self._zvar._raw
            return attrib[zvar_num]
        else:
            raise KeyError(name + ': no such attribute for variable ' +
                           self._zvar.name())

    def __delitem__(self, name):
        """Delete an zEntry by name

        @param name: name of the zEntry to delete
        @type name: str
        @raise KeyError: if there is no attribute named L{name} associated
                         with this zVariable
        @raise CDFError: other errors in CDF library
        @note: If this is the only remaining entry, the Attribute will be
               deleted.
        """
        attrib = super(zAttrList, self).__getitem__(name)
        zvar_num = self._zvar._num()
        if not attrib.has_entry(zvar_num):
            raise KeyError(str(name) + ': no such attribute for variable ' +
                           str(self._zvar._name))
        del attrib[zvar_num]
        if len(attrib) == 0:
            attrib._delete()

    def __setitem__(self, name, data):
        """Sets a zEntry by name

        The type of the zEntry is guessed from L{data}. The type is chosen to
        match the data; subject to that constraint, it will try to match
        (in order):
        1. existing zEntry corresponding to this zVar
        2. other zEntries in this zAttribute
        3. the type of this zVar
        4. data-matching constraints described in L{_Hyperslice.types}

        @param name: name of zAttribute; zEntry for this zVariable will be set
                     in zAttribute by this name
        @type name: str
        @raise CDFError: errors in CDF library
        @raise ValueError: if unable to find a valid CDF type matching L{data},
                           or if L{data} is the wrong dimensions.
        """
        try:
            attr = super(zAttrList, self).__getitem__(name)
        except KeyError:
            attr = zAttr(self._cdf_file, name, True)
        zvar_num = self._zvar._num()
        attr._raw = self._zvar._raw
        attr[zvar_num] = data

    def __len__(self):
        """Number of zAttributes in this variable

        @return: number of zAttributes in the CDF
                 which have entries for this variable.
        @rtype: int
        """
        length = 0
        count = ctypes.c_long(0)
        self._cdf_file._call(const.GET_, const.CDF_NUMATTRS_,
                             ctypes.byref(count))
        current = 0
        while current < count.value:
            candidate = zAttr(self._cdf_file, current)
            if not candidate.global_scope():
                if candidate.has_entry(self._zvar._num()):
                    length += 1
            current += 1
        return length

    def type(self, name, new_type=None):
        """Find or change the CDF type of a zEntry in this zVar

        @param name: name of the zAttr to check or change
        @type name: str
        @param new_type: type to change it to, see :py:mod:`pycdf.const`
        @type new_type: ctypes.c_long
        @return: CDF variable type, see :py:mod:`pycdf.const`
        @rtype: int
        @note: If changing types, old and new must be equivalent, see CDF
               User's Guide section 2.5.5 pg. 57
        """
        attrib = super(zAttrList, self).__getitem__(name)
        zvar_num = self._zvar._num()
        if not attrib.has_entry(zvar_num):
            raise KeyError(name + ': no such attribute for variable ' +
                           self._zvar.name())
        return attrib.type(zvar_num, new_type)

    def _clone_attr(self, master, name, new_name=None):
        """Clones a single attribute from one in this list or another

        Copies data and types from the master attribute to the new one

        @param master: attribute list to copy attribute from
        @type master: L{zAttrList}
        @param name: name of attribute to copy
        @type name: str
        @param new_name: name of the new attribute, default L{name}
        @type new_name: str
        """
        if new_name is None:
            new_name = name
        if new_name in self:
            del self[new_name]
        self.new(new_name, master[name],
                 master.type(name) if hasattr(master, 'type') else None)
