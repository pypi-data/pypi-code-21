#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Toolbox of various functions and generic utilities.

Authors: Steve Morley, Jon Niehof, Brian Larsen, Josef Koller, Dan Welling
Institution: Los Alamos National Laboratory
Contact: smorley@lanl.gov, jniehof@lanl.gov, balarsen@lanl.gov, jkoller@lanl.gov, dwelling@lanl.gov
Los Alamos National Laboratory

Copyright 2010 Los Alamos National Security, LLC.
"""

#If you add functions here, be sure to:
#1) add to the __all__ list
#2) add to functions in Doc/source/toolbox.rst so it goes in the docs
from __future__ import division
from __future__ import absolute_import

import datetime
import glob
import itertools
import os
import os.path
import re
import subprocess
import sys
import time
import numbers
import warnings
import zipfile

try:
    import cPickle as pickle
except:
    import pickle

import numpy as np

from pycdf import time as spt

#Try to pull in the C version. Assumption is that if you import this module,
#you want to do some association analysis, so the overhead in the import
#is OK.
from pycdf import lib
if lib.have_libspacepy:
    import ctypes

#Py3k compatibility renamings
try:
    xrange
except NameError:
    xrange = range

__all__ = ['tOverlap', 'tOverlapHalf', 'tCommon', 'loadpickle', 'savepickle', 'assemble',
           'human_sort', 'feq', 'dictree', 'update', 'progressbar',
           'windowMean', 'medAbsDev', 'binHisto',
           'logspace', 'geomspace', 'linspace', 'arraybin', 'mlt2rad',
           'rad2mlt', 'pmm', 'getNamedPath', 'query_yes_no',
           'interpol', 'normalize', 'intsolve', 'dist_to_list',
           'bin_center_to_edges', 'bin_edges_to_center', 'thread_job', 'thread_map',
           'eventTimer', 'isview', 'interweave', 'indsFromXrange', 'hypot',
           'do_with_timeout', 'TimeoutError', 'timeout_check_call', 'unique_columns']

__contact__ = 'Brian Larsen: balarsen@lanl.gov'

def unique_columns(inval, axis=0):
    """
    Given a multidimensional input return the unique rows or columns along the given axis.
    Based largely on http://stackoverflow.com/questions/16970982/find-unique-rows-in-numpy-array
    axis=0 is unique rows, axis=1 is unique columns

    Parameters
    ==========
    inval :  array-like
        array to find unique columns or rows of

    Optional Parameters
    ===================
    axis : int
        The axis to find unique over, default: 0

    Returns
    =======
    out : array
        N-dimensional array of the unique values along the axis

    Examples
    ========
    """
    # this is a nice trick taking advantage of structed arrays where each row or column
    #   is the value, so returl unique works
    # np.ascontiguousarray() is to be really sure it will work
    if axis == 0:
        val = np.ascontiguousarray(np.transpose(inval))
    else:
        val = np.ascontiguousarray(inval)
    b = val.view(np.dtype((np.void, val.dtype.itemsize * val.shape[1])))
    unique_a = np.unique(b).view(val.dtype).reshape(-1, val.shape[1])
    return unique_a


def hypot(*args):
    """
    compute the N-dimensional hypot of an iterable or many arguments

    Parameters
    ==========
    args : many numbers or array-like
        array like or many inputs to compute from

    Returns
    =======
    out : float
        N-dimensional hypot of a number

    Notes
    =====
    This function has a complicated speed function.
     - if a numpy array of floats is input this is passed off to C
     - if iterables are passed in they are made into numpy arrays and comptaton is done local
     - if many scalar agruments are passed in calculation is done in a loop
    For max speed:
     - <20 elements expand them into scalars
         >>> tb.hypot(*vals)
         >>> tb.hypot(vals[0], vals[1]...) #alternate
     - >20 elements premake them into a numpy array of doubles

    Examples
    ========
    >>> from spacepy import toolbox as tb
    >>> print tb.hypot([3,4])
    5.0
    >>> print tb.hypot(3,4)
    5.0
    >>> # Benchmark ####
    >>> from spacepy import toolbox as tb
    >>> import numpy as np
    >>> import timeit
    >>> num_list = []
    >>> num_np = []
    >>> num_np_double = []
    >>> num_scalar = []
    >>> tot = 500
    >>> for num in tb.logspace(1, tot, 10):
    >>>     print num
    >>>     num_list.append(timeit.timeit(stmt='tb.hypot(a)', setup='from spacepy import toolbox as tb; import numpy as np; a = [3]*{0}'.format(int(num)), number=10000))
    >>>     num_np.append(timeit.timeit(stmt='tb.hypot(a)', setup='from spacepy import toolbox as tb; import numpy as np; a = np.asarray([3]*{0})'.format(int(num)), number=10000))
    >>>     num_scalar.append(timeit.timeit(stmt='tb.hypot(*a)', setup='from spacepy import toolbox as tb; import numpy as np; a = [3]*{0}'.format(int(num)), number=10000))
    >>> from pylab import *
    >>> loglog(tb.logspace(1, tot, 10),  num_list, lw=2, label='list')
    >>> loglog(tb.logspace(1, tot, 10),  num_np, lw=2, label='numpy->ctypes')
    >>> loglog(tb.logspace(1, tot, 10),  num_scalar, lw=2, label='scalar')
    >>> legend(shadow=True, fancybox=1, loc='upper left')
    >>> title('Different hypot times for 10000 runs')
    >>> ylabel('Time [s]')
    >>> xlabel('Size')

    .. image:: ../../source/images/hypot_no_extension_speeds_3cases.png
    """
    if lib.have_libspacepy:
        if len(args) == 1 and hasattr(args, 'ndim'): # it is an array
                ans = lib.hypot_tb(args[0], np.product(args[0].shape))
                return ans
    ans = 0.0
    for arg in args:
        if hasattr(arg, '__iter__'):
            tmp = np.asanyarray(arg)
            ans += np.sum(tmp**2)
        else:
            ans += arg**2
    return np.sqrt(ans)

def tOverlap(ts1, ts2, *args, **kwargs):
    """
    Finds the overlapping elements in two lists of datetime objects

    Parameters
    ==========
    ts1 : datetime
        first set of datetime object
    ts2 : datetime
        datatime object
    args :
        additional arguments passed to tOverlapHalf

    Returns
    =======
    out : list
        indices of ts1 within interval of ts2, & vice versa

    Examples
    ========
    Given two series of datetime objects, event_dates and omni['Time']:

    >>> import spacepy.toolbox as tb
    >>> from spacepy import omni
    >>> import datetime
    >>> event_dates = st.tickrange(datetime.datetime(2000, 1, 1), datetime.datetime(2000, 10, 1), deltadays=3)
    >>> onni_dates = st.tickrange(datetime.datetime(2000, 1, 1), datetime.datetime(2000, 10, 1), deltadays=0.5)
    >>> omni = omni.get_omni(onni_dates)
    >>> [einds,oinds] = tb.tOverlap(event_dates, omni['ticks'])
    >>> omni_time = omni['ticks'][oinds[0]:oinds[-1]+1]
    >>> print omni_time
    [datetime.datetime(2000, 1, 1, 0, 0), datetime.datetime(2000, 1, 1, 12, 0),
    ... , datetime.datetime(2000, 9, 30, 0, 0)]

    See Also
    ========
    tOverlapHalf
    tCommon
    """
    idx_1in2 = tOverlapHalf(ts2, ts1, *args, **kwargs)
    idx_2in1 = tOverlapHalf(ts1, ts2, *args, **kwargs)
    if len(idx_2in1) == 0:
        idx_2in1 = None
    if len(idx_1in2) == 0:
        idx_1in2 = None
    return idx_1in2, idx_2in1

def tOverlapHalf(ts1, ts2, presort=False):
    """
    Find overlapping elements in two lists of datetime objects

    This is one-half of tOverlap, i.e. it finds only occurrences where
    ts2 exists within the bounds of ts1, or the second element
    returned by tOverlap.

    Parameters
    ==========
    ts1 : list
        first set of datetime object
    ts2 : list
        datatime object
    presort : bool
        Set to use a faster algorithm which assumes ts1 and
                   ts2 are both sorted in ascending order. This speeds up
                   the overlap comparison by about 50x, so it is worth sorting
                   the list if one sort can be done for many calls to tOverlap

    Returns
    =======
    out : list
        indices of ts2 within interval of ts1

        **note:** Returns empty list if no overlap found

    See Also
    ========
    tOverlap
    tCommon
    """
    if presort:
        import bisect
        t_lower, t_upper = ts1[0], ts1[-1]
        return xrange(bisect.bisect_left(ts2, t_lower),
                     bisect.bisect_right(ts2, t_upper))
    else:
        t_lower, t_upper = min(ts1), max(ts1)
        return [i for i in range(len(ts2))
                if ts2[i] >= t_lower and ts2[i] <= t_upper]

def tCommon(ts1, ts2, mask_only=True):
    """
    Finds the elements in a list of datetime objects present in another

    Parameters
    ==========
    ts1 : list or array-like
        first set of datetime objects
    ts2 : list or array-like
        second set of datetime objects

    Returns
    =======
    out : tuple
        Two element tuple of truth tables (of 1 present in 2, & vice versa)

    See Also
    ========
    tOverlapHalf
    tOverlap

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> import numpy as np
    >>> import datetime as dt
    >>> ts1 = np.array([dt.datetime(2001,3,10)+dt.timedelta(hours=a) for a in range(20)])
    >>> ts2 = np.array([dt.datetime(2001,3,10,2)+dt.timedelta(hours=a*0.5) for a in range(20)])
    >>> common_inds = tb.tCommon(ts1, ts2)
    >>> common_inds[0] #mask of values in ts1 common with ts2
    array([False, False,  True,  True,  True,  True,  True,  True,  True,
            True,  True,  True, False, False, False, False, False, False,
           False, False], dtype=bool)
    >>> ts2[common_inds[1]] #values of ts2 also in ts1

    The latter can be found more simply by setting the mask_only keyword to False

    >>> common_vals = tb.tCommon(ts1, ts2, mask_only=False)
    >>> common_vals[1]
    array([2001-03-10 02:00:00, 2001-03-10 03:00:00, 2001-03-10 04:00:00,
           2001-03-10 05:00:00, 2001-03-10 06:00:00, 2001-03-10 07:00:00,
           2001-03-10 08:00:00, 2001-03-10 09:00:00, 2001-03-10 10:00:00,
           2001-03-10 11:00:00], dtype=object)
    """
    from matplotlib.dates import date2num, num2date

    tn1, tn2 = date2num(ts1), date2num(ts2)

    v_test = np.__version__.split('.')
    if v_test[0] == 1 and v_test[1] <= 3:
        el1in2 = np.setmember1d(tn1, tn2) #makes mask of present/absent
        el2in1 = np.setmember1d(tn2, tn1)
    else:
        el1in2 = np.in1d(tn1, tn2, assume_unique=True) #makes mask of present/absent
        el2in1 = np.in1d(tn2, tn1, assume_unique=True)

    if mask_only:
        return el1in2, el2in1
    else:
        truemask1 = np.abs(np.array(el1in2)-1)
        truemask2 = np.abs(np.array(el2in1)-1)
        time1 = np.ma.masked_array(tn1, mask=truemask1)
        time2 = np.ma.masked_array(tn2, mask=truemask2)
        dum1 = num2date(time1.compressed())
        dum2 = num2date(time2.compressed())
        #        dum1 = [val.replace(tzinfo=None) for val in dum1] # this hits ValueError: microsecond must be in 0..999999
        #        dum2 = [val.replace(tzinfo=None) for val in dum2]
        dum11 = []
        dum22 = []
        for v1, v2 in zip(dum1, dum2):
            try:
                dum11.append(v1.replace(tzinfo=None))
            except ValueError: # ValueError: microsecond must be in 0..999999
                dum11.append((datetime.datetime(v1.year, v1.month, v1.day, v1.hour, v1.minute, v1.second, 0) +
                             datetime.timedelta(seconds=1)).replace(tzinfo=None))
            try:
                dum22.append(v2.replace(tzinfo=None))
            except ValueError: # ValueError: microsecond must be in 0..999999
                dum22.append((datetime.datetime(v2.year, v2.month, v2.day, v2.hour, v2.minute, v2.second, 0) +
                             datetime.timedelta(seconds=1)).replace(tzinfo=None))
        dum1 = dum11
        dum2 = dum22
        if type(ts1)==np.ndarray or type(ts2)==np.ndarray:
            dum1 = np.array(dum1)
            dum2 = np.array(dum2)
        return dum1, dum2

def loadpickle(fln):
    """
    load a pickle and return content as dictionary

    Parameters
    ==========
    fln : string
        filename

    Returns
    =======
    out : dict
        dictionary with content from file

    See Also
    ========
    savepickle

    Examples
    ========
    **note**: If fln is not found, but the same filename with '.gz'
           is found, will attempt to open the .gz as a gzipped file.

    >>> d = loadpickle('test.pbin')
    """
    if not os.path.exists(fln) and os.path.exists(fln + '.gz'):
        gzip = True
        fln += '.gz'
    else:
        try:
            with open(fln, 'rb') as fh:
                try: #Py3k
                    return pickle.load(fh, encoding='latin1')
                except TypeError:
                    return pickle.load(fh)
        except pickle.UnpicklingError: #maybe it's a gzip?
            gzip = True
        else:
            gzip = False
    if gzip:
        try:
            import zlib
            with open(fln, 'rb') as fh:
                stream = zlib.decompress(fh.read(), 16 + zlib.MAX_WBITS)
                try: #Py3k
                    return pickle.loads(stream, encoding='latin1')
                except TypeError:
                    return pickle.loads(stream)
        except MemoryError:
            import gzip
            with open(fln) as fh:
                gzh = gzip.GzipFile(fileobj=fh)
                try: #Py3k
                    contents = pickle.load(gzh, encoding='latin1')
                except TypeError:
                    contents = pickle.load(gzh)
                gzh.close()
            return contents


# -----------------------------------------------
def savepickle(fln, dict, compress=None):
    """
    save dictionary variable dict to a pickle with filename fln

    Parameters
    ----------
    fln : string
        filename
    dict : dict
        container with stuff
    compress : bool
        write as a gzip-compressed file
                     (.gz will be added to L{fln}).
                     If not specified, defaults to uncompressed, unless the
                     compressed file exists and the uncompressed does not.

    See Also
    ========
    loadpickle

    Examples
    ========
    >>> d = {'grade':[1,2,3], 'name':['Mary', 'John', 'Chris']}
    >>> savepickle('test.pbin', d)
    """
    if compress == None:
        if not os.path.exists(fln) and os.path.exists(fln + '.gz'):
            compress = True
        else:
            compress = False
    if compress:
        import gzip
        with open(fln + '.gz', 'wb') as fh:
            gzh = gzip.GzipFile(fln, 'wb', compresslevel=3, fileobj=fh)
            pickle.dump(dict, gzh, 2)
            gzh.close()
    else:
        with open(fln, 'wb') as fh:
            pickle.dump(dict, fh, 2) # 2 ... fast binary
    return


# -----------------------------------------------
def assemble(fln_pattern, outfln, sortkey='ticks', verbose=True):
    """
    assembles all pickled files matching fln_pattern into single file and
    save as outfln. Pattern may contain simple shell-style wildcards \*? a la fnmatch
    file will be assembled along time axis given by Ticktock (key: 'ticks') in dictionary
    If sortkey = None, then nothing will be sorted

    Parameters
    ----------
    fln_pattern : string
        pattern to match filenames
    outfln : string
        filename to save combined files to

    Returns
    =======
    out : dict
        dictionary with combined values

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> a, b, c = {'ticks':[1,2,3]}, {'ticks':[4,5,6]}, {'ticks':[7,8,9]}
    >>> tb.savepickle('input_files_2001.pkl', a)
    >>> tb.savepickle('input_files_2002.pkl', b)
    >>> tb.savepickle('input_files_2004.pkl', c)
    >>> a = tb.assemble('input_files_*.pkl', 'combined_input.pkl')
    ('adding ', 'input_files_2001.pkl')
    ('adding ', 'input_files_2002.pkl')
    ('adding ', 'input_files_2004.pkl')
    ('\\n writing: ', 'combined_input.pkl')
    >>> print(a)
    {'ticks': array([1, 2, 3, 4, 5, 6, 7, 8, 9])}
    """
    # done this way so it works before install
    from spacepy import coordinates as c

    filelist = glob.glob(fln_pattern)
    filelist = human_sort(filelist)
    # read all files
    d = {}
    for fln in filelist:
        if verbose: print("adding ", fln)
        d[fln] = loadpickle(fln)

    # combine them
    dcomb = d[filelist[0]]  # copy the first file over
    for fln in filelist[1:]:
       # check if sortkey is actually available
        assert (sortkey in d[fln] or sortkey==None), 'provided sortkey ='+sortkey+' is not available'

        if sortkey:
            TAIcount = len(d[fln][sortkey])
        else:
            TAIcount = len(d[fln][ list(d[fln].keys())[0] ])
        for key in d[fln]:
            #print fln, key
            dim = np.array(np.shape(d[fln][key]))
            ax = np.where(dim==TAIcount)[0]
            if len(ax) == 1: # then match with TAI length is given (jump over otherwise like for 'parameters')
                if isinstance(dcomb[key], spt.Ticktock):
                    dcomb[key] = dcomb[key].append(d[fln][key])
                elif isinstance(dcomb[key], c.Coords):
                    dcomb[key] = dcomb[key].append(d[fln][key])
                else:
                    dcomb[key] = np.append(dcomb[key], d[fln][key], axis=ax[0])

    if sortkey:    #  then sort
        if isinstance(dcomb[sortkey], spt.Ticktock):
            idx = np.argsort(dcomb[sortkey].RDT)
        else:
            idx = np.argsort(dcomb[sortkey])
        TAIcount = len(dcomb[sortkey])
        for key in dcomb: # iterates over keys by default
            dim = np.array(np.shape(dcomb[key]))
            ax = np.where(dim==TAIcount)[0]
            if len(ax) == 1: # then match with length of TAI
                dcomb[key] = dcomb[key][idx] # resort
    else:
        # do nothing
        pass

    if verbose: print('\n writing: ', outfln)
    savepickle(outfln, dcomb)
    return dcomb

def human_sort( l ):
    """ Sort the given list in the way that humans expect.
    http://www.codinghorror.com/blog/2007/12/sorting-for-humans-natural-sort-order.html

    Parameters
    ----------
    l : list
        list of objects to human sort

    Returns
    -------
    out : list
        sorted list

    Examples
    --------
    >>> import spacepy.toolbox as tb
    >>> dat = ['r1.txt', 'r10.txt', 'r2.txt']
    >>> dat.sort()
    >>> print dat
    ['r1.txt', 'r10.txt', 'r2.txt']
    >>> tb.human_sort(dat)
    ['r1.txt', 'r2.txt', 'r10.txt']
    """
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    alphanum_key = None
    try:
        l.sort( key=alphanum_key )
    except TypeError:
        l.sort()
    return l

def feq(x, y, precision=0.0000005):
    """
    compare two floating point values if they are equal
    after: http://www.lahey.com/float.htm

    See Also
    --------
    numpy.allclose

    Parameters
    ----------
    x : float
        a number
    y : float or array of floats
        other numbers to compare
    precision : float (optional)
        Relative precision for equal (default 0.0000005)
        Specified as a fraction of the sum of ``x`` and ``y``.

    Returns
    -------
    out : bool
        True (equal) or False (not equal)

    Examples
    --------
    >>> import spacepy.toolbox as tb
    >>> x = 1 + 1e-4
    >>> y = 1 + 2e-4
    >>> tb.feq(x, y)
    False
    >>> tb.feq(x, y, 1e-3)
    True
    """
    x = np.asanyarray(x)
    y = np.asanyarray(y)
    boolean = abs(x-y) <= (abs(x+y)*precision)
    return boolean

def dictree(in_dict, verbose=False, spaces=None, levels=True, attrs=False, **kwargs):
    """
    pretty print a dictionary tree

    Parameters
    ----------
    in_dict : dict
        a complex dictionary (with substructures)
    verbose : boolean (optional)
        print more info
    spaces : string (optional)
        string will added for every line
    levels : integer (optional)
        number of levels to recurse through (True means all)
    attrs : boolean (optional)
        display information for attributes

    Examples
    --------
    >>> import spacepy.toolbox as tb
    >>> d = {'grade':{'level1':[4,5,6], 'level2':[2,3,4]}, 'name':['Mary', 'John', 'Chris']}
    >>> tb.dictree(d)
    +
    |____grade
         |____level1
         |____level2
    |____name

    More complicated example using a datamodel:

    >>> from spacepy import datamodel
    >>> counts = datamodel.dmarray([2,4,6], attrs={'units': 'cts/s'})
    >>> data = {'counts': counts, 'PI': 'Dr Zog'}
    >>> tb.dictree(data)
    +
    |____PI
    |____counts
    >>> tb.dictree(data, attrs=True, verbose=True)
    +
    |____PI (str [6])
    |____counts (spacepy.datamodel.dmarray (3,))
        :|____units (str [5])

    Attributes of, e.g., a CDF or a datamodel type object (obj.attrs)
    are denoted by a colon.
    """
    try:
        assert hasattr(in_dict, 'keys')
    except AssertionError:
        try:
            assert hasattr(in_dict, 'attrs')
        except:
            raise TypeError('dictree: Input must be dictionary-like')

    if not spaces:
        spaces = ''
        print('+')

    if 'toplev' in kwargs:
        toplev = kwargs['toplev']
    else:
        toplev = True
    try:
        if toplev and attrs:
            dictree(in_dict.attrs, spaces = ':', verbose = verbose, levels = levels, attrs=attrs, toplev=True)
            toplev = False
    except:
        pass

    # TODO, if levels is True why check again?
    if levels:
        try:
            assert levels is True
        except AssertionError:
            levels -= 1
            if levels == 0:
                levels = None

    try:
        for key in sorted(in_dict.keys()):
            bar = '|____' + str(key)
            if verbose:
                typestr = str(type(in_dict[key])).split("'")[1]
                #check entry for dict-like OR .attrs dict
                try:
                    dimstr = in_dict[key].shape
                    dimstr = ' ' + str(dimstr)
                except AttributeError:
                    try:
                        dimstr = len(in_dict[key])
                        dimstr = ' [' + str(dimstr) + ']'
                    except:
                        dimstr = ''
                print(spaces + bar + ' ('+ typestr + dimstr + ')')
            else:
                print(spaces + bar)
            if hasattr(in_dict[key], 'attrs') and attrs:
                dictree(in_dict[key].attrs, spaces = spaces + '    :', verbose = verbose, levels = levels, attrs=attrs, toplev=False)
            if hasattr(in_dict[key], 'keys') and levels:
                dictree(in_dict[key], spaces = spaces + '     ', verbose = verbose, levels = levels, attrs=attrs, toplev=False)
    except:
        pass
    return None

def update(all=True, QDomni=False, omni=False, omni2=False, leapsecs=False, PSDdata=False):
    """
    Download and update local database for omni, leapsecs etc

    Parameters
    ==========
    all : boolean (optional)
        if True, update OMNI2, Qin-Denton and leapsecs
    omni : boolean (optional)
        if True. update only omni (Qin-Denton)
    omni2 : boolean (optional)
        if True, update only original OMNI2
    QDomni : boolean (optional)
        if True, update OMNI2 and Qin-Denton
    leapsecs : boolean (optional)
        if True, update only leapseconds

    Returns
    =======
    out : string
        data directory where things are saved

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.update(omni=True)
    """
    from spacepy.datamodel import SpaceData, dmarray, fromCDF, toHDF5
    from spacepy import DOT_FLN, config

    if sys.version_info[0]<3:
        import urllib as u
    else:
        import urllib.request as u

    if 'user_agent' in config and config['user_agent']:
        class AppURLopener(u.FancyURLopener):
            version = config['user_agent']
        u._urlopener = AppURLopener()

    datadir = os.path.join(DOT_FLN, 'data')
    if not os.path.exists(datadir):
        os.mkdir(datadir)
        os.chmod(datadir, 0o777)

    #leapsec_url ='ftp://maia.usno.navy.mil/ser7/tai-utc.dat'
    leapsec_fname = os.path.join(datadir, 'tai-utc.dat')

    # define location for getting omni
    #omni_url = 'ftp://virbo.org/QinDenton/hour/merged/latest/WGhour-latest.d.zip'
    omni_fname_zip = os.path.join(datadir, 'WGhour-latest.d.zip')
    omni2_fname_zip = os.path.join(datadir, 'omni2-latest.cdf.zip')
    omni_fname_pkl = os.path.join(datadir, 'omnidata.pkl')
    omni_fname_json = os.path.join(datadir, 'omnidata.txt')
    omni_fname_h5 = os.path.join(datadir, 'omnidata.h5')
    omni2_fname_h5 = os.path.join(datadir, 'omni2data.h5')

    PSDdata_fname = os.path.join('psd_dat.sqlite')

    if (omni or omni2 or QDomni or leapsecs or PSDdata):
        all = False #if an option is explicitly selected, turn 'all' off

    if all == True:
        omni = True
        omni2 = True
        leapsecs = True

    if QDomni == True:
        omni = True
        omni2 = True

    if omni == True:
        # retrieve omni, unzip and save as table
        print("Retrieving Qin_Denton file ...")
        u.urlretrieve(config['qindenton_url'], omni_fname_zip, reporthook=progressbar)
        fh_zip = zipfile.ZipFile(omni_fname_zip)
        data = fh_zip.read(fh_zip.namelist()[0])
        fh_zip.close()
        if not str is bytes:
            data = data.decode('ascii')
        A = np.array(data.split('\n'))
        print("Now processing (this may take a minute) ...")

        # create a keylist
        keys = A[0].split()
        keys.remove('8')
        keys.remove('6')
        keys[keys.index('status')] = '8_status'
        keys[keys.index('stat')] = '6_status'
        keys[keys.index('dst')] = 'Dst'
        keys[keys.index('kp')] = 'Kp'
        #keys[keys.index('Hr')] = 'Hr'
        keys[keys.index('V_SW')] = 'velo'
        keys[keys.index('Den_P')] = 'dens'
        keys[keys.index('Day')] = 'DOY'
        keys[keys.index('Year')] = 'Year'

        # remove keyword lines and empty lines as well
        idx = np.where(A != '')[0]
        # put it into a 2D table
        tab = [val.split() for val in A[idx[1:]]]
        stat8 = [val[11] for val in tab]
        stat6 = [val[27] for val in tab]

        tab = np.array(tab, dtype='float32')
        # take out where Dst not available ( = 99999) or year == 0
        idx = np.where((tab[:,12] !=99.0) & (tab[:,0] != 0))[0]
        tab = tab[idx,:]
        stat8 = np.array(stat8)[idx]
        stat6 = np.array(stat6)[idx]

        omnidata = SpaceData()
        # sort through and make an omni dictionary
        # extract keys from line above
        for ikey, i  in zip(keys,range(len(keys))):
            if ikey in ('Year', 'DOY', 'Hr', 'Dst'):
                omnidata[ikey] = dmarray(tab[:, i], dtype='int16')
            else:
                omnidata[ikey] = dmarray(tab[:,i])

        # add TAI to omnidata
        nTAI = len(omnidata['DOY'])

        # add interpolation quality flags
        omnidata['Qbits'] = SpaceData()
        arr = dmarray(stat8.view(stat8.dtype.kind + '1'),
                      dtype=np.byte).reshape((8, nTAI))
        for ik, key in enumerate(['ByIMF', 'BzIMF', 'velo', 'dens', 'Pdyn', 'G1', 'G2', 'G3']):
            omnidata['Qbits'][key] = arr[ik,:]
        if stat6.dtype.str[1:] == 'U6':
            stat6 = np.require(stat6, dtype='|S6')
        arr = dmarray(stat6.view(stat6.dtype.kind + '1'),
                      dtype=np.byte).reshape((6, nTAI))
        for ik, key in enumerate(['W1', 'W2', 'W3', 'W4', 'W5', 'W6']):
            omnidata['Qbits'][key] = arr[ik,:]

        #remove string status keys
        foo = omnidata.pop('6_status')
        foo = omnidata.pop('8_status')

        # add time information to omni pickle (long loop)
        omnidata['UTC'] = dmarray([datetime.datetime(int(omnidata['Year'][i]), 1, 1) +
                 datetime.timedelta(days=int(omnidata['DOY'][i]) - 1,
                                    hours=int(omnidata['Hr'][i]))
                 for i in range(nTAI)])

        omnidata['ticks'] = spt.Ticktock(omnidata['UTC'], 'UTC')
        omnidata['RDT'] = omnidata['ticks'].RDT
        del omnidata['ticks'] #Can be quickly regenerated on import
        del omnidata['Year']
        del omnidata['Hr']

        print("Now saving... ")
        ##for now, make one file -- think about whether monthly/annual files makes sense
        toHDF5(omni_fname_h5, omnidata)

        # delete left-overs
        os.remove(omni_fname_zip)


    if omni2 == True:
        # adding missing values from original omni2
        print("Retrieving OMNI2 file ...")
        u.urlretrieve(config['omni2_url'], omni2_fname_zip, reporthook=progressbar)
        fh_zip = zipfile.ZipFile(omni2_fname_zip)
        fh_zip.extractall();
        fh_zip.close()
        omnicdf = fromCDF(fh_zip.namelist()[0])
        #add RDT
        omnicdf['RDT'] = spt.Ticktock(omnicdf['Epoch'],'UTC').RDT
        #remove keys that get in the way
        del omnicdf['Hour']
        del omnicdf['Year']
        del omnicdf['Decimal_Day']

        # save as HDF5
        toHDF5(omni2_fname_h5, omnicdf)

        # delete left-overs
        os.remove(omni2_fname_zip)

    if leapsecs == True:
        print("Retrieving leapseconds file ... ")
        u.urlretrieve(config['leapsec_url'], leapsec_fname)

    if PSDdata == True:
        print("Retrieving PSD sql database")
        u.urlretrieve(config['psddata_url'], PSDdata_fname, reporthook=progressbar)
    return datadir

def indsFromXrange(inxrange):
    '''return the start and end indices implied by an xrange, useful when xrange is zero-length

    Parameters
    ==========
    inxrange : xrange
        input xrange object to parse

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> foo = xrange(23, 39)
    >>> foo[0]
    23
    >>> tb.indsFromXrange(foo)
    [23, 39]
    >>> foo1 = xrange(23, 23)
    >>> tb.indsFromXrange(foo) #indexing won't work in this case
    [23, 23]
    '''
    if not isinstance(inxrange, xrange): return None
    valstr = inxrange.__str__()
    if ',' not in valstr:
        res = re.search('(\d+)', valstr)
        retval = [int(0), int(res.group(1))]
    else:
        res = re.search('(\d+), (\d+)', valstr)
        retval = [int(res.group(1)), int(res.group(2))]
    return retval

def progressbar(count, blocksize, totalsize, text='Download Progress'):
    """
    print a progress bar with urllib.urlretrieve reporthook functionality

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> import urllib
    >>> urllib.urlretrieve(config['psddata_url'], PSDdata_fname, reporthook=tb.progressbar)
    """
    percent = int(count*blocksize*100/totalsize)
    sys.stdout.write("\r" + text + " " + "...%d%%" % percent)
    if percent == 100: print('\n')
    sys.stdout.flush()

def windowMean(data, time=[], winsize=0, overlap=0, st_time=None, op=np.mean):
    """
    Windowing mean function, window overlap is user defined

    Parameters
    ==========
    data : array_like
        1D series of points
    time : list (optional)
        series of timestamps, optional (format as numeric or datetime)
        For non-overlapping windows set overlap to zero.
    winsize : integer or datetime.timedelta (optional)
        window size
    overlap : integer or datetime.timedelta (optional)
        amount of window overlap
    st_time : datetime.datetime (optional)
        for time-based averaging, a start-time other than the first
        point can be specified
    op : callable (optional)
        the operator to be called, default numpy.mean

    Returns
    =======
    out : tuple
        the windowed mean of the data, and an associated reference time vector

    Examples
    ========
    For non-overlapping windows set overlap to zero.
    e.g. (time-based averaging)
    Given a data set of 100 points at hourly resolution (with the time tick in
    the middle of the sample), the daily average of this, with half-overlapping
    windows is calculated:

    >>> import spacepy.toolbox as tb
    >>> from datetime import datetime, timedelta
    >>> wsize = datetime.timedelta(days=1)
    >>> olap = datetime.timedelta(hours=12)
    >>> data = [10, 20]*50
    >>> time = [datetime.datetime(2001,1,1) + datetime.timedelta(hours=n, minutes = 30) for n in range(100)]
    >>> outdata, outtime = tb.windowMean(data, time, winsize=wsize, overlap=olap, st_time=datetime.datetime(2001,1,1))
    >>> outdata, outtime
    ([15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0],
     [datetime.datetime(2001, 1, 1, 12, 0),
      datetime.datetime(2001, 1, 2, 0, 0),
      datetime.datetime(2001, 1, 2, 12, 0),
      datetime.datetime(2001, 1, 3, 0, 0),
      datetime.datetime(2001, 1, 3, 12, 0),
      datetime.datetime(2001, 1, 4, 0, 0),
      datetime.datetime(2001, 1, 4, 12, 0)])

    When using time-based averaging, ensure that the time tick corresponds to
    the middle of the time-bin to which the data apply. That is, if the data
    are hourly, say for 00:00-01:00, then the time applied should be 00:30.
    If this is not done, unexpected behaviour can result.

    e.g. (pointwise averaging),

    >>> outdata, outtime = tb.windowMean(data, winsize=24, overlap=12)
    >>> outdata, outtime
    ([15.0, 15.0, 15.0, 15.0, 15.0, 15.0, 15.0], [12.0, 24.0, 36.0, 48.0, 60.0, 72.0, 84.0])

    where winsize and overlap are numeric,
    in this example the window size is 24 points (as the data are hourly) and
    the overlap is 12 points (a half day). The output vectors start at
    winsize/2 and end at N-(winsize/2), the output time vector
    is basically a reference to the nth point in the original series.

    **note** This is a quick and dirty function - it is NOT optimized, at all.
    """
    #check inputs and initialize
    #Set resolution to 1 if no times supplied
    if len(time) == 0:
        startpt, res = 0, 1
        time = list(range(len(data)))
        pts = True
    else:
        if len(data) != len(time):
            raise ValueError('windowmean error: data and time must have same length')
        #First check if datetime objects
        try:
            assert type(winsize) == datetime.timedelta
            assert type(overlap) == datetime.timedelta
        except AssertionError:
            raise TypeError('windowmean error: winsize/overlap must be timedeltas')
        pts = False #force time-based averaging
        if (type(time[0]) != datetime.datetime):
            startpt = time[0]

    #now actually do windowing mean
    outdata, outtime = [], []
    data = np.array(data)
    if pts:
        #loop for fixed number of points in window
        try:
            inttypes = (int, long)
        except NameError:
            inttypes = (int,)
        if not isinstance(winsize, inttypes):
            winsize = int(round(winsize))
            warnings.warn('windowmean: non-integer windowsize, rounding to %d' \
            % winsize)
        if winsize < 1:
            winsize = 1
            warnings.warn('windowmean: window length < 1, defaulting to 1')
        if overlap >= winsize:
            overlap = winsize - 1
            warnings.warn('''windowmean: overlap longer than window, truncated to
            %d''' % overlap)
        lastpt = winsize-1 #set last point to end of window size
        while lastpt < len(data):
            datwin = np.ma.masked_where(np.isnan(data[startpt:startpt+winsize]), \
                data[startpt:startpt+winsize])
            getmean = op(datwin.compressed()) #mean of window, excl. NaNs
            gettime = (time[startpt+winsize] - time[startpt])/2. \
                + time[startpt]#new timestamp
            startpt = startpt+winsize-overlap
            lastpt = startpt+winsize
            outdata.append(getmean) #construct output arrays
            outtime.append(gettime)
    else:
        #loop with time-based window
        lastpt = time[0] + winsize
        delta = datetime.timedelta(microseconds=1) #TODO: replace this with an explicit check for times on the boundary?
        if st_time:
            startpt = st_time
        else:
            startpt = time[0]
        if overlap >= winsize:
            raise ValueError('Overlap requested greater than size of window')
        while startpt < time[-1]:
            getinds = tOverlapHalf([startpt,startpt+winsize-delta], time, presort=True)
            if getinds: #if not None
                getdata = np.ma.masked_where(np.isnan(data[getinds[0]:getinds[-1]+1]), data[getinds[0]:getinds[-1]+1])
                getmean = op(getdata.compressed()) #find mean excluding NaNs
            else:
                getmean = np.nan
            gettime = startpt + winsize//2 #new timestamp -floordiv req'd with future division
            startpt = startpt + winsize - overlap #advance window start
            lastpt = startpt + winsize
            outdata.append(getmean) #construct output arrays
            outtime.append(gettime)

    return outdata, outtime

def medAbsDev(series, scale=False):
    """
    Calculate median absolute deviation of a given input series

    Median absolute deviation (MAD) is a robust and resistant measure of
    the spread of a sample (same purpose as standard deviation). The
    MAD is preferred to the inter-quartile range as the inter-quartile
    range only shows 50% of the data whereas the MAD uses all data but
    remains robust and resistant. See e.g. Wilks, Statistical methods
    for the Atmospheric Sciences, 1995, Ch. 3. For additional details on
    the scaling, see Rousseeuw and Croux, J. Amer. Stat. Assoc., 88 (424),
    pp. 1273-1283, 1993.

    Parameters
    ==========
    series : array_like
        the input data series

    Other Parameters
    ================
    scale : bool
        if True (default: False), scale to standard deviation of a normal distribution

    Returns
    =======
    out : float
        the median absolute deviation

    Examples
    ========
    Find the median absolute deviation of a data set. Here we use the log-
    normal distribution fitted to the population of sawtooth intervals, see
    Morley and Henderson, Comment, Geophysical Research Letters, 2009.

    >>> import numpy
    >>> import spacepy.toolbox as tb
    >>> numpy.random.seed(8675301)
    >>> data = numpy.random.lognormal(mean=5.1458, sigma=0.302313, size=30)
    >>> print data
    array([ 181.28078923,  131.18152745, ... , 141.15455416, 160.88972791])
    >>> tb.medAbsDev(data)
    28.346646721370192

    **note** This implementation is robust to presence of NaNs
    """
    #ensure input is numpy array (and make 1-D)
    series = (np.array(series, dtype=float)).ravel()
    #mask for NaNs
    series = np.ma.masked_where(np.isnan(series),series)
    #get median absolute deviation of unmasked elements
    perc50 = np.median(series.compressed())
    mad = np.median(abs(series.compressed()-perc50))
    if scale:
        mad *= 1.4826 #scale so that MAD is same as SD for normal distr.
    return mad

def binHisto(data, verbose=False):
    """
    Calculates bin width and number of bins for histogram using Freedman-Diaconis rule, if rule fails, defaults to square-root method

    The Freedman-Diaconis method is detailed in:
        Freedman, D., and P. Diaconis (1981), On the histogram as a density estimator: L2 theory, Z. Wahrscheinlichkeitstheor. Verw. Geb., 57, 453–476

    and is also described by:
        Wilks, D. S. (2006), Statistical Methods in the Atmospheric Sciences, 2nd ed.

    Parameters
    ==========
    data : array_like
        list/array of data values
    verbose : boolean (optional)
        print out some more information

    Returns
    =======
    out : tuple
        calculated width of bins using F-D rule, number of bins (nearest integer) to use for histogram

    Examples
    ========
    >>> import numpy, spacepy
    >>> import matplotlib.pyplot as plt
    >>> numpy.random.seed(8675301)
    >>> data = numpy.random.randn(1000)
    >>> binw, nbins = spacepy.toolbox.binHisto(data)
    >>> print(nbins)
    19.0
    >>> p = plt.hist(data, bins=nbins, histtype='step', normed=True)

    See Also
    ========
    matplotlib.pyplot.hist
    """
    from matplotlib.mlab import prctile
    pul = prctile(data, p=(25,75)) #get confidence interval
    ql, qu = pul[0], pul[1]
    iqr = qu-ql
    binw = 2.*iqr/(len(data)**(1./3.))
    if binw != 0:
        nbins = round((max(data)-min(data))/binw)
    # if nbins is 0, NaN or inf don't use the F-D rule just use sqrt(num) rule
    if binw == 0 or nbins == 0 or not np.isfinite(nbins):
        nbins = round(np.sqrt(len(data)))
        binw = len(data)/nbins
        if verbose:
            print("Used sqrt rule")
    else:
        if verbose:
            print("Used F-D rule")
    return (binw, nbins)

def logspace(min, max, num, **kwargs):
    """
    Returns log-spaced bins. Same as numpy.logspace except the min and max are the min and max
    not log10(min) and log10(max)

    Parameters
    ==========
    min : float
        minimum value
    max : float
        maximum value
    num : integer
        number of log spaced bins

    Other Parameters
    ================
    kwargs : dict
        additional keywords passed into matplotlib.dates.num2date

    Returns
    =======
    out : array
        log-spaced bins from min to max in a numpy array

    Notes
    =====
    This function works on both numbers and datetime objects

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.logspace(1, 100, 5)
    array([   1.        ,    3.16227766,   10.        ,   31.6227766 ,  100.        ])

    See Also
    ========
    geomspace
    linspace
    """
    if isinstance(min, datetime.datetime):
        from matplotlib.dates import date2num, num2date
        ans = num2date(np.logspace(np.log10(date2num(min)), np.log10(date2num(max)), num, **kwargs))
        ans = spt.no_tzinfo(ans)
        return np.array(ans)
    else:
        return np.logspace(np.log10(min), np.log10(max), num, **kwargs)

def linspace(min, max, num, **kwargs):
    """
    Returns linear-spaced bins. Same as numpy.linspace except works with datetime
    and is faster

    Parameters
    ==========
    min : float, datetime
        minimum value
    max : float, datetime
        maximum value
    num : integer
        number of linear spaced bins

    Other Parameters
    ================
    kwargs : dict
        additional keywords passed into matplotlib.dates.num2date

    Returns
    =======
    out : array
        linear-spaced bins from min to max in a numpy array

    Notes
    =====
    This function works on both numbers and datetime objects

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.linspace(1, 10, 4)
    array([  1.,   4.,   7.,  10.])

    See Also
    ========
    geomspace
    logspace
    """
    if hasattr(min, 'shape') and min.shape is ():
        min = min.item()
    if hasattr(max, 'shape') and max.shape is ():
        max = max.item()
    if isinstance(min, datetime.datetime):
        from matplotlib.dates import date2num, num2date
        ans = num2date(np.linspace(date2num(min), date2num(max), num, **kwargs))
        ans = spt.no_tzinfo(ans)
        return np.array(ans)
    else:
        return np.linspace(min, max, num, **kwargs)

def geomspace(start, ratio=None, stop=False, num=50):
    """
    Returns geometrically spaced numbers.

    Parameters
    ==========
    start : float
        The starting value of the sequence.
    ratio : float (optional)
        The ratio between subsequent points
    stop : float (optional)
        End value, if this is selected `num` is overridden
    num : int (optional)
        Number of samples to generate. Default is 50.

    Returns
    =======
    seq : array
        geometrically spaced sequence

    See Also
    ========
    linspace
    logspace

    Examples
    ========
    To get a geometric progression between 0.01 and 3 in 10 steps

    >>> import spacepy.toolbox as tb
    >>> tb.geomspace(0.01, stop=3, num=10)
    [0.01,
     0.018846716378431192,
     0.035519871824902655,
     0.066943295008216955,
     0.12616612944575134,
     0.23778172582285118,
     0.44814047465571644,
     0.84459764235318191,
     1.5917892219322083,
     2.9999999999999996]

    To get a geometric progression with a specified ratio, say 10

    >>> import spacepy.toolbox as tb
    >>> tb.geomspace(0.01, ratio=10, num=5)
    [0.01, 0.10000000000000001, 1.0, 10.0, 100.0]
    """
    if not ratio and stop != False:
        ratio = (stop/start)**(1/(num-1))
    seq = []
    seq.append(start)
    if stop == False:
        for j in range(1, num):
            seq.append(seq[j-1]*ratio)
        return seq
    else:
        val, j = start, 1
        while val <= stop or np.allclose(val, stop, ):
            val = seq[j-1]*ratio
            seq.append(val)
            j+=1
        return seq[:-1]

def arraybin(array, bins):
    """
    Split a sequence into subsequences based on value.

    Given a sequence of values and a sequence of values representing the
    division between bins, return the indices grouped by bin.

    Parameters
    ==========
    array : array_like
        the input sequence to slice, must be sorted in ascending order
    bins : array_like
        dividing lines between bins. Number of bins is len(bins)+1,
            value that exactly equal a dividing value are assigned
            to the higher bin

    Returns
    =======
    out : list
        indices for each bin (list of lists)

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.arraybin(range(10), [4.2])
    [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
    """
    bin_it = lambda value: (i for i in range(len(array)) if array[i] >= value)
    splits = [next(bin_it(value), len(array)) for value in bins]
    return [list(range(start_idx, stop_idx)) for (start_idx, stop_idx)
            in zip([0] + splits, splits + [len(array)])]

def mlt2rad(mlt, midnight = False):
    """
    Convert mlt values to radians for polar plotting
    transform mlt angles to radians from -pi to pi
    referenced from noon by default

    Parameters
    ==========
    mlt : numpy array
        array of mlt values
    midnight : boolean (optional)
        reference to midnight instead of noon

    Returns
    =======
    out : numpy array
        array of radians

    Examples
    ========
    >>> from numpy import array
    >>> mlt2rad(array([3,6,9,14,22]))
    array([-2.35619449, -1.57079633, -0.78539816,  0.52359878,  2.61799388])

    See Also
    ========
    rad2mlt
    """
    if midnight:
        try:
            mlt_arr =  [val + 12 for val in mlt]
        except TypeError:
            mlt_arr = mlt + 12
    else:
        mlt_arr = mlt
    try:
        rad_arr = [(val-12)*np.pi/12. for val in mlt_arr]
    except TypeError:
        rad_arr = (mlt_arr-12)*np.pi/12.
    return rad_arr

def rad2mlt(rad, midnight=False):
    """
    Convert radians values to mlt
    transform radians from -pi to pi to mlt
    referenced from noon by default

    Parameters
    ==========
    rad : numpy array
        array of radian values
    midnight : boolean (optional)
        reference to midnight instead of noon

    Returns
    =======
    out : numpy array
        array of mlt values

    Examples
    ========
    >>> rad2mlt(array([0,pi, pi/2.]))
    array([ 12.,  24.,  18.])

    See Also
    ========
    mlt2rad
    """
    if midnight:
        rad_arr = rad + np.pi
    else:
        rad_arr = rad
    mlt_arr=rad_arr*(12/np.pi) + 12
    return mlt_arr

def pmm(a, *b):
    """
    print min and max of input arrays

    Parameters
    ==========
    a : numpy array
        input array
    b : list arguments
        some additional number of arrays

    Returns
    =======
    out : list
        list of min, max for each array

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> from numpy import arange
    >>> tb.pmm(arange(10), arange(10)+3)
    [[0, 9], [3, 12]]
    """
    ind = np.isfinite(a)
    try:
        ans = [[ np.min(a[ind]), np.max(a[ind]) ]]
    except TypeError:
        a_tmp = np.asarray(a)
        ans = [[ np.min(a_tmp[ind]), np.max(a_tmp[ind]) ]]
    for val in b:
        ind = np.isfinite(val)
        try:
            ans.append( [np.min(val[ind]), np.max(val[ind])] )
        except TypeError:
            val_tmp = np.asarray(val)
            ans.append( [np.min(val_tmp[ind]), np.max(val_tmp[ind])] )
    return ans

def getNamedPath(name):
    """
    Return the full path of a parent directory with name as the leaf

    Parameters
    ==========
    name : string
        the name of the parent directory to locate

    Examples
    ========
    Run from a directory
    /mnt/projects/dream/bin/Ephem
    with 'dream' as the name, this function
    would return '/mnt/projects/dream'
    """
    def findNamed(path):
        pp = os.path.split(path)
        if pp[-1] == '':
            return None
        if pp[-1] != name:
            path = findNamed(pp[0])
        return path
    return findNamed(os.getcwd())

def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user).

    The "answer" return value is one of "yes" or "no".

    Parameters
    ==========
    question : string
        the question to ask
    default : string (optional)

    Returns
    =======
    out : string
        answer ('yes' or 'no')

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.query_yes_no('Ready to go?')
    Ready to go? [Y/n] y
    'yes'
    """
    valid = {"yes":"yes",   "y":"yes",  "ye":"yes",
             "no":"no",     "n":"no"}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while 1:
        sys.stdout.write(question + prompt)
        if sys.version_info[0]==2:
            choice = raw_input().lower()
        elif sys.version_info[0]>2:
            choice = input().lower()
        if default is not None and choice == '':
            return default
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

def interpol(newx, x, y, wrap=None, **kwargs):
    """
    1-D linear interpolation with interpolation of hours/longitude

    Parameters
    ==========
    newx : array_like
        x values where we want the interpolated values
    x : array_like
        x values of the original data (must be monotonically increasing or wrapping)
    y : array_like
        y values of the original data
    wrap : string, optional
        for continuous x data that wraps in y at 'hours' (24), 'longitude' (360),
        or arbitrary value (int, float)
    kwargs : dict
        additional keywords, currently accepts baddata that sets baddata for
        masked arrays

    Returns
    =======
    out : numpy.masked_array
        interpolated data values for new abscissa values

    Examples
    ========
    For a simple interpolation

    >>> import spacepy.toolbox as tb
    >>> import numpy
    >>> x = numpy.arange(10)
    >>> y = numpy.arange(10)
    >>> tb.interpol(numpy.arange(5)+0.5, x, y)
    array([ 0.5,  1.5,  2.5,  3.5,  4.5])

    To use the wrap functionality, without the wrap keyword you get the wrong answer

    >>> y = range(24)*2
    >>> x = range(len(y))
    >>> tb.interpol([1.5, 10.5, 23.5], x, y, wrap='hour').compressed() # compress removed the masked array
    array([  1.5,  10.5,  23.5])
    >>> tb.interpol([1.5, 10.5, 23.5], x, y)
    array([  1.5,  10.5,  11.5])
    """
    if 'baddata' in kwargs:
        y = np.ma.masked_equal(y, kwargs['baddata'])
        x = np.ma.masked_array(x)
        x.mask = y.mask
        kwargs.__delitem__('baddata')
    else:
        tst = np.ma.core.MaskedArray
        if type(x)!=tst or type(y)!=tst or type(newx)!=tst:
            x = np.ma.masked_array(x)
            y = np.ma.masked_array(y)
            newx = np.ma.masked_array(newx)

    def wrap_interp(xout, xin, yin, sect):
        dpsect=360/sect
        yc = np.cos(np.deg2rad(y*dpsect))
        ys = np.sin(np.deg2rad(y*dpsect))
        new_yc = np.interp(newx, x.compressed(), yc.compressed(), **kwargs)
        new_ys = np.interp(newx, x.compressed(), ys.compressed(), **kwargs)
        try:
            new_bad = np.interp(newx, x, y.mask)
        except ValueError:
            new_bad = np.zeros((len(newx)))
        newy = np.rad2deg(np.arctan(new_ys/new_yc))/dpsect
        #1st quadrant is O.K
        #2nd quadrant
        idx = [n for n in range(len(new_yc)) if new_yc[n]<0 and new_ys[n]>0]
        newy[idx] = sect/2 + newy[idx]
        #print('Sector 2 inds: %s' % idx)
        #3rd quadrant
        idx = [n for n in range(len(new_yc)) if new_yc[n]<0 and new_ys[n]<0]
        newy[idx] = sect/2 + newy[idx]
        #print('Sector 3 inds: %s' % idx)
        #4th quadrant
        idx = [n for n in range(len(new_yc)) if new_yc[n]>0 and new_ys[n]<0]
        newy[idx] = sect + newy[idx]
        #print('Sector 4 inds: %s' % idx)
        new_bad = np.ma.make_mask(new_bad)
        newy = np.ma.masked_array(newy, mask=new_bad)
        return newy

    if wrap=='hour':
        newy = wrap_interp(newx, x.compressed(), y.compressed(), 24)
    elif wrap=='lon':
        newy = wrap_interp(newx, x.compressed(), y.compressed(), 360)
    elif isinstance(wrap, numbers.Real):
        newy = wrap_interp(newx, x.compressed(), y.compressed(), wrap)
    else:
        newy = np.interp(newx, x.compressed(), y.compressed(), **kwargs)
    return newy

# -----------------------------------------------

def quaternionNormalize(Qin, scalarPos='last'):
    '''
    Given an input quaternion (or array of quaternions), return the unit quaternion

    Parameters
    ==========
    vec : array_like
        input quaternion to normalize

    Returns
    =======
    out : array_like
        normalized quaternion

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.quaternionNormalize([0.707, 0, 0.707, 0.2])
    array([ 0.69337122,  0.        ,  0.69337122,  0.19614462])

    '''
    if scalarPos.lower()=='last':
        i, j, k = 0, 1, 2
        w = 3
    elif scalarPos.lower()=='first':
        i, j, k = 1, 2, 3
        w = 0
    else:
        raise NotImplementedError('quaternionNormalize: scalarPos must be set to "First" or "Last"')

    Quse = np.asanyarray(Qin).astype(float)
    try:
        Quse.shape[1]
    except IndexError:
        Quse = np.asanyarray([Quse])
    outarr = np.empty_like(Quse)
    for idx, row in enumerate(Quse):
        magn = hypot(row)
        if magn>1e-12:
            mag_inv = 1.0/magn
            tmp = row*mag_inv
        else:
            tmp = [0]*4
            tmp[i] = tmp[j] = tmp[k] = 0.0
            tmp[w] = 1.0
        outarr[idx, i] = tmp[i]
        outarr[idx, j] = tmp[j]
        outarr[idx, k] = tmp[k]
        outarr[idx, w] = tmp[w]
    return outarr.squeeze()


def quaternionRotateVector(Qin, Vin, scalarPos='last', normalize=True):
    '''
    Given quaternions and vectors, return the vectors rotated by the quaternions

    Parameters
    ==========
    Qin : array_like
        input quaternion to rotate by
    Vin : array-like
        input vector to rotate

    Returns
    =======
    out : array_like
        rotated vector

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> import numpy as np
    >>> vec = [1, 0, 0]
    >>> quat_wijk = [np.sin(np.pi/4), 0, np.sin(np.pi/4), 0.0]
    >>> quat_ijkw = [0.0, np.sin(np.pi/4), 0, np.sin(np.pi/4)]
    >>> tb.quaternionRotateVector(quat_ijkw, vec)
    array([ 0.,  0., -1.])
    >>> tb.quaternionRotateVector(quat_wijk, vec, scalarPos='first')
    array([ 0.,  0., -1.])

    See Also
    ========
    quaternionMultiply
    '''
    if scalarPos.lower()=='last':
        i, j, k = 0, 1, 2
        w = 3
    elif scalarPos.lower()=='first':
        i, j, k = 1, 2, 3
        w = 0
    else:
        raise NotImplementedError('quaternionRotateVector: scalarPos must be set to "First" or "Last"')

    Quse = np.asanyarray(Qin).astype(float)
    if normalize: Quse = quaternionNormalize(Quse, scalarPos=scalarPos)
    Vuse = np.asanyarray(Vin).astype(float)
    try:
        Quse.shape[1]
    except IndexError:
        Quse = np.asanyarray([Quse])
    try:
        Vuse.shape[1]
    except IndexError:
        Vuse = np.asanyarray([Vuse])
    try:
        assert Vuse.shape[0]==Quse.shape[0]
    except AssertionError:
        raise ValueError('quaternionRotateVector: Input vector array must have same length as input quaternion array')

    outarr = np.empty((Quse.shape[0], 3))
    for idx, row in enumerate(Quse):
        Vrow = Vuse[idx]
        ii, jj, kk, ww = row[i]**2, row[j]**2, row[k]**2, row[w]**2
        iw, jw, kw = row[i]*row[w], row[j]*row[w], row[k]*row[w]
        ij, ik, jk = row[i]*row[j], row[i]*row[k], row[j]*row[k]

        outarr[idx, 0] = ww*Vrow[0] + 2*jw*Vrow[2] - 2*kw*Vrow[1] + ii*Vrow[0] + 2*ij*Vrow[1] + 2*ik*Vrow[2] - kk*Vrow[0] - jj*Vrow[0]
        outarr[idx, 1] = 2*ij*Vrow[0] + jj*Vrow[1] + 2*jk*Vrow[2] + 2*kw*Vrow[0] - kk*Vrow[1] + ww*Vrow[1] - 2*iw*Vrow[2] - ii*Vrow[1]
        outarr[idx, 2] = 2*ik*Vrow[0] + 2*jk*Vrow[1] + kk*Vrow[2] - 2.0*jw*Vrow[0] - jj*Vrow[2] + 2.0*iw*Vrow[1] - ii*Vrow[2] + ww*Vrow[2]
    return outarr.squeeze()


def quaternionMultiply(Qin1, Qin2, scalarPos='last'):
    '''
    Given quaternions, return the product, i.e. Qin1*Qin2

    Parameters
    ==========
    Qin1 : array_like
        input quaternion, first position
    Qin2 : array-like
        input quaternion, second position

    Returns
    =======
    out : array_like
        quaternion product

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> import numpy as np
    >>> vecX = [1, 0, 0] #shared X-axis
    >>> vecZ = [0, 0, 1] #unshared, but similar, Z-axis
    >>> quat_eci_to_gsm = [-0.05395384,  0.07589845, -0.15172533,  0.98402634]
    >>> quat_eci_to_gse = [ 0.20016056,  0.03445775, -0.16611386,  0.96496352]
    >>> quat_gsm_to_eci = tb.quaternionConjugate(quat_eci_to_gsm)
    >>> quat_gse_to_gsm = tb.quaternionMultiply(quat_gsm_to_eci, quat_eci_to_gse)
    >>> tb.quaternionRotateVector(quat_gse_to_gsm, vecX)
    array([  1.00000000e+00,   1.06536725e-09,  -1.16892107e-08])
    >>> tb.quaternionRotateVector(quat_gse_to_gsm, vecZ)
    array([  1.06802834e-08,  -4.95669027e-01,   8.68511494e-01])
    '''
    if scalarPos.lower()=='last':
        i, j, k = 0, 1, 2
        w = 3
    elif scalarPos.lower()=='first':
        i, j, k = 1, 2, 3
        w = 0
    else:
        raise NotImplementedError('quaternionMultiply: scalarPos must be set to "First" or "Last"')

    Quse1 = np.asanyarray(Qin1).astype(float)
    Quse2 = np.asanyarray(Qin2).astype(float)
    try:
        Quse1.shape[1]
    except IndexError:
        Quse1 = np.asanyarray([Quse1])
    try:
        Quse2.shape[1]
    except IndexError:
        Quse2 = np.asanyarray([Quse2])
    try:
        assert Quse2.shape==Quse1.shape
    except AssertionError:
        raise ValueError('quaternionMultiply: Input quaternion arrays must have same length')

    outarr = np.empty_like(Quse1)
    for idx, row in enumerate(Quse1):
        row1 = row
        row2 = Quse2[idx]
        #vector components
        outarr[idx, i] = row1[w]*row2[i] + row1[i]*row2[w] + row1[j]*row2[k] - row1[k]*row2[j]
        outarr[idx, j] = row1[w]*row2[j] - row1[i]*row2[k] + row1[j]*row2[w] + row1[k]*row2[i]
        outarr[idx, k] = row1[w]*row2[k] + row1[i]*row2[j] - row1[j]*row2[i] + row1[k]*row2[w]
        #real part
        outarr[idx, w] = row1[w]*row2[w] - row1[i]*row2[i] - row1[j]*row2[j] - row1[k]*row2[k]
    return outarr.squeeze()


def quaternionConjugate(Qin, scalarPos='last'):
    '''
    Given an input quaternion (or array of quaternions), return the conjugate

    Parameters
    ==========
    vec : array_like
        input quaternion to conjugate

    Returns
    =======
    out : array_like
        conjugate quaternion

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.quaternionConjugate([0.707, 0, 0.707, 0.2], scalarPos='last')
    array([-0.707, -0.   , -0.707,  0.2  ])

    See Also
    ========
    quaternionMultiply
    '''
    if scalarPos.lower()=='last':
        i, j, k = 0, 1, 2
        w = 3
    elif scalarPos.lower()=='first':
        i, j, k = 1, 2, 3
        w = 0
    else:
        raise NotImplementedError('quaternionConjugate: scalarPos must be set to "First" or "Last"')

    Quse = np.asanyarray(Qin).astype(float)
    try:
        Quse.shape[1]
    except IndexError:
        Quse = np.asanyarray([Quse])
    outarr = np.empty_like(Quse)
    for idx, row in enumerate(Quse):
        outarr[idx, i] = -row[i]
        outarr[idx, j] = -row[j]
        outarr[idx, k] = -row[k]
        outarr[idx, w] = row[w]

    return outarr.squeeze()

# -----------------------------------------------

def normalize(vec):
    """
    Given an input vector normalize the vector

    Parameters
    ==========
    vec : array_like
        input vector to normalize

    Returns
    =======
    out : array_like
        normalized vector

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.normalize([1,2,3])
    [0.0, 0.5, 1.0]
    """
    # check to see if vec is numpy array, this is fastest
    if isinstance(vec, np.ndarray):
        out = (vec - vec.min())/np.ptp(vec)
    else:
        vecmin = np.min(vec)
        ptp = np.ptp(vec)
        out = [(val -  vecmin)/ptp for val in vec]
    return out

def intsolve(func, value, start=None, stop=None, maxit=1000):
    """
    Find the function input such that definite integral is desired value.

    Given a function, integrate from an (optional) start point until the
    integral reached a desired value, and return the end point of the
    integration.

    Parameters
    ==========
    func : callable
        function to integrate, must take single parameter
    value : float
        desired final value of the integral
    start : float (optional)
        value at which to start integration, default -Infinity
    stop : float (optional)
        value at which to stop integration, default +Infinity
    maxit : integer
        maximum number of iterations

    Returns
    =======
    out : float
        x such that the integral of L{func} from L{start} to x is L{value}

    **Note:** Assumes func is everywhere positive, otherwise solution may
           be multi-valued.
    """
    from scipy import inf
    from scipy.integrate import quad
    from warnings import warn
    if start is None:
        start = -inf
    if stop is None:
        stop = inf
    lower_bound = start
    upper_bound = stop
    it = 0
    while it < maxit:
        it += 1
        if upper_bound == inf:
            if lower_bound == -inf:
                test_bound = 0
            elif lower_bound < 1.0:
                test_bound = 1.0
            else:
                test_bound = lower_bound * 2
        else:
            if lower_bound == -inf:
                if upper_bound > -1.0:
                    test_bound = -1.0
                else:
                    test_bound = upper_bound * 2
            else:
                test_bound = (lower_bound + upper_bound) / 2.0
        (test_value, err) = quad(func, start, test_bound)
        if abs(value - test_value) <= err:
            break
        elif value < test_value:
            upper_bound = test_bound
        else:
            lower_bound = test_bound

    if abs(value - test_value) > err:
        warn('Difference between desired value and actual is ' +
             str(abs(value - test_value)) +
             ', greater than integral error ' +
             str(err), UserWarning, stacklevel=2)
    return test_bound

def dist_to_list(func, length, min=None, max=None):
    """
    Convert a probability distribution function to a list of values

    This is a deterministic way to produce a known-length list of values
    matching a certain probability distribution. It is likely to be a closer
    match to the distribution function than a random sampling from the
    distribution.

    Parameters
    ==========
    func : callable
        function to call for each possible value, returning
            probability density at that value (does not need to be
            normalized.)
    length : int
        number of elements to return
    min : float
        minimum value to possibly include
    max : float
        maximum value to possibly include

    Examples
    ========
    >>> import matplotlib
    >>> import numpy
    >>> import spacepy.toolbox as tb
    >>> gauss = lambda x: math.exp(-(x ** 2) / (2 * 5 ** 2)) / (5 * math.sqrt(2 * math.pi))
    >>> vals = tb.dist_to_list(gauss, 1000, -numpy.inf, numpy.inf)
    >>> print vals[0]
    -16.45263...
    >>> p1 = matplotlib.pyplot.hist(vals, bins=[i - 10 for i in range(21)], facecolor='green')
    >>> matplotlib.pyplot.hold(True)
    >>> x = [i / 100.0 - 10.0 for i in range(2001)]
    >>> p2 = matplotlib.pyplot.plot(x, [gauss(i) * 1000 for i in x], 'red')
    >>> matplotlib.pyplot.draw()
    """
    from scipy import inf
    from scipy.integrate import quad
    if min is None:
        min = -inf
    if max is None:
        max = inf
    total = quad(func, min, max)[0]
    step = float(total) / length
    return [intsolve(func, (0.5 + i) * step, min, max) for i in range(length)]

def bin_center_to_edges(centers):
    """
    Convert a list of bin centers to their edges

    Given a list of center values for a set of bins, finds the start and
    end value for each bin. (start of bin n+1 is assumed to be end of bin n).
    Useful for e.g. matplotlib.pyplot.pcolor.

    Edge between bins n and n+1 is arithmetic mean of the center of n
    and n+1; edge below bin 0 and above last bin are established to make
    these bins symmetric about their center value.

    Parameters
    ==========
    centers : list
        list of center values for bins

    Returns
    =======
    out : list
        list of edges for bins

    **note:** returned list will be one element longer than centers

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.bin_center_to_edges([1,2,3])
    [0.5, 1.5, 2.5, 3.5]
    """
    edges = bin_edges_to_center(centers)
    edges = np.append(centers[0]-(edges[0]-centers[0]), edges)
    edges = np.append(edges, centers[-1]+(centers[-1]-edges[-1]))
    return edges

def bin_edges_to_center(edges):
    """
    Convert a list of bin edges to their centers

    Given a list of edge values for a set of bins, finds the center of each bin.
    (start of bin n+1 is assumed to be end of bin n).

    Center of bin n is arithmetic mean of the edges of the adjacent bins.

    Parameters
    ==========
    edges : list
        list of edge values for bins

    Returns
    =======
    out : numpy.ndarray
        array of centers for bins

    **note:** returned array will be one element shorter than edges

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.bin_center_to_edges([1,2,3])
    [0.5, 1.5, 2.5, 3.5]
    """
    df = np.diff(edges)
    if isinstance(df[0], datetime.timedelta) and sys.version_info[0:2]<=(3,2):
        return edges[:-1] + df//2
    else:
        return edges[:-1] + df/2

def thread_job(job_size, thread_count, target, *args, **kwargs):
    """
    Split a job into subjobs and run a thread for each

    Each thread spawned will call L{target} to handle a slice of the job.

    This is only useful if a job:
      1. Can be split into completely independent subjobs
      2. Relies heavily on code that does not use the Python GIL, e.g.
         numpy or ctypes code
      3. Does not return a value. Either pass in a list/array to hold the
         result, or see L{thread_map}

    Examples
    ========
    squaring 100 million numbers:

    >>> import numpy
    >>> import spacepy.toolbox as tb
    >>> numpy.random.seed(8675301)
    >>> a = numpy.random.randint(0, 100, [100000000])
    >>> b = numpy.empty([100000000], dtype='int64')
    >>> def targ(in_array, out_array, start, count): \
             out_array[start:start + count] = in_array[start:start + count] ** 2
    >>> tb.thread_job(len(a), 0, targ, a, b)
    >>> print(b[0:5])
    [2704 7225  196 1521   36]

    This example:
      - Defines a target function, which will be called for each thread.
        It is usually necessary to define a simple "wrapper" function
        like this to provide the correct call signature.
      - The target function receives inputs C{in_array} and C{out_array},
        which are not touched directly by C{thread_job} but are passed
        through in the call. In this case, C{a} gets passed as
        C{in_array} and C{b} as C{out_array}
      - The target function also receives the start and number of elements
        it needs to process. For each thread where the target is called,
        these numbers are different.

    Parameters
    ==========
    job_size : int
        Total size of the job. Often this is an array size.
    thread_count : int
        Number of threads to spawn. If =0 or None, will
            spawn as many threads as there are cores available on
            the system. (Each hyperthreading core counts as 2.)
            Generally this is the Right Thing to do.
            If NEGATIVE, will spawn abs(thread_count) threads,
            but will run them sequentially rather than in
            parallel; useful for debugging.
    target : callable
        Python callable (generally a function, may also be an
            imported ctypes function) to run in each thread. The
            *last* two positional arguments passed in will be a
            "start" and a "subjob size," respectively;
            frequently this will be the start index and the number
            of elements to process in an array.
    args : sequence
        Arguments to pass to L{target}. If L{target} is an instance
            method, self must be explicitly passed in. start and
            subjob_size will be appended.
    kwargs : dict
        keyword arguments to pass to L{target}.
    """
    try:
        import threading
    except:
        return (target(*(args +  (0, job_size)), **kwargs), )
    if thread_count == None or thread_count == 0:
        try:
            import multiprocessing
            thread_count = multiprocessing.cpu_count()
        except: #Do something not too stupid
            thread_count = 8
    if thread_count < 0:
        thread_count *= -1
        seq = True
    else:
        seq = False
    count = float(job_size) / thread_count
    starts = [int(count * i + 0.5) for i in range(thread_count)]
    subsize = [(starts[i + 1] if i < thread_count - 1 else job_size) -
               starts[i]
               for i in range(thread_count)]
    threads = []
    for i in range(thread_count):
        t = threading.Thread(
            None, target, None,
            args + (starts[i], subsize[i]), kwargs)
        t.start()
        if seq:
            t.join()
        else:
            threads.append(t)
    if not seq:
        for t in threads:
            t.join()

def thread_map(target, iterable, thread_count=None, *args, **kwargs):
    """
    Apply a function to every element of a list, in separate threads

    Interface is similar to multiprocessing.map, except it runs in threads

    This is made largely obsolete in python3 by from concurrent import futures

    Examples
    ========
    find totals of several arrays

    >>> import numpy
    >>> from spacepy import toolbox
    >>> inputs = range(100)
    >>> totals = toolbox.thread_map(numpy.sum, inputs)
    >>> print(totals[0], totals[50], totals[99])
    (0, 50, 99)

    >>> # in python3
    >>> from concurrent import futures
    >>> with futures.ThreadPoolExecutor(max_workers=4) as executor:
    ...:     for ans in executor.map(numpy.sum, [0,50,99]):
    ...:         print ans
    #0
    #50
    #99

    Parameters
    ==========
    target : callable
        Python callable to run on each element of iterable.
            For each call, an element of iterable is appended to
            args and both args and kwargs are passed through.
            Note that this means the iterable element is always the
            *last* positional argument; this allows the specification
            of self as the first argument for method calls.
    iterable : iterable
        elements to pass to each call of L{target}
    args : sequence
        arguments to pass to target before each element of
            iterable
    thread_count : integer
        Number of threads to spawn; see L{thread_job}.
    kwargs : dict
        keyword arguments to pass to L{target}.

    Returns
    =======
    out : list
        return values of L{target} for each item from L{iterable}
    """
    try:
        jobsize = len(iterable)
    except TypeError:
        iterable = list(iterable)
        jobsize = len(iterable)
    def array_targ(function, it, retvals, arglist, kwarglist, start, size):
        for i in range(start, start + size):
            retvals[i] = function(*(arglist + (it[i],)), **kwarglist)
    retvals = [None] * jobsize
    thread_job(jobsize, thread_count, array_targ,
               target, iterable, retvals, args, kwargs)
    return retvals

def eventTimer(Event, Time1):
    """
    Times an event then prints out the time and the name of the event,
    nice for debugging and seeing that the code is progressing

    Parameters
    ==========
    Event : str
        Name of the event, string is printed out by function
    Time1 : time.time
        the time to difference in the function

    Returns
    =======
    Time2 : time.time
        the new time for the next call to EventTimer

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> import time
    >>> t1 = time.time()
    >>> t1 = tb.eventTimer('Test event finished', t1)
    ('4.40', 'Test event finished')
    """
    Time2 = time.time()
    print(("%4.2f" % (Time2 - Time1), Event))
    return Time2


def isview(array1, array2=None):
    """
    Returns if an object is a view of another object.  More precisely if one array argument is specified
    True is returned is the arrays owns its data.  If two arrays arguments are specified a tuple is returned
    of if the first array owns its data and the the second if they point at the same memory location

    Parameters
    ==========
    array1 : numpy.ndarray
        array to query if it owns its data

    Other Parameters
    ================
    array2 : object (optional)
        array to query if array1 is a view of this object at the specified memory location

    Returns
    =======
    out : bool or tuple
        If one array is specified bool is returned, True is the array owns its data.  If two arrays
        are specified a tuple where the second element is a bool of if the array point at the same
        memory location

    Examples
    ========
    import numpy
    import spacepy.toolbox as tb
    a = numpy.arange(100)
    b = a[0:10]
    tb.isview(a)
    # False
    tb.isview(b)
    # True
    tb.isview(b, a)
    # (True, True)
    tb.isview(b, b)
    # (True, True)  # the conditions are met and numpy cannot tell this
    """
    # deal with the one input case first
    if array2 is None:
        try:
            if array1.base is None:
                return False
            return True
        except AttributeError:
            return False # if it is not an array then it is not a view
    # there are two arrays input
    try:
        if array1.base is None:
            return (False, False)
        return (True, array1.base is array2)
    except AttributeError:
            return (False, False) # if it is not an array then it is not a view

def interweave(a, b):
    """
    given two array-like variables interweave them together.
    Discussed here: http://stackoverflow.com/questions/5347065/interweaving-two-numpy-arrays

    Parameters
    ==========
    a : array-like
        first array

    b : array-like
        second array

    Returns
    =======
    out : numpy.ndarray
        interweaved array
    """
    a = np.asanyarray(a)
    b = np.asanyarray(b)
    ans = np.empty((a.size + b.size), dtype=a.dtype)
    ans[0::2] = a
    ans[1::2] = b
    return ans


class TimeoutError(Exception):
    """Raised when a time-limited process times out"""
    pass


def do_with_timeout(timeout, target, *args, **kwargs):
    """
    Execute a function (or method) with a timeout.

    Call the function (or method) ``target``, with arguments ``args`` and
    keyword arguments ``kwargs``. Normally return the return value
    from ``target``, but if ``target`` takes more than ``timeout`` seconds
    to execute, raises ``TimeoutError``.

    .. note::
        This is, at best, a blunt instrument. Exceptions from ``target`` may
        not propagate properly (tracebacks will be hard to follow.) The
        function which failed to time out may continue to execute until the
        interpreter exits; trapping the TimeoutError and continuing normally
        is not recommended.

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> import time
    >>> def time_me_out():
    ...     time.sleep(5)
    >>> tb.do_with_timeout(0.5, time_me_out) #raises TimeoutError

    Parameters
    ==========
    timeout : float
        Timeout, in seconds.
    target : callable
        Python callable (generally a function, may also be an
            imported ctypes function) to run.
    args : sequence
        Arguments to pass to ``target``.
    kwargs : dict
        keyword arguments to pass to ``target``.

    Raises
    ======
    TimeoutError : If ``target`` does not return in ``timeout`` seconds.

    Returns
    =======
    out :
        return value of ``target``
    """
    import threading
    class ReturningThread(threading.Thread):
        def __init__(self, group=None, target=None, name=None,
                     args=(), kwargs={}):
            #we're handling target, args, kwargs
            super(ReturningThread, self).__init__(group, name=name)
            self._target = target
            self._args = args
            self._kwargs = kwargs
            self._retval = None
            self._exception = None

        def run(self):
            try:
                self._retval = self._target(*self._args, **self._kwargs)
            except:
                self._exception = sys.exc_info()

        def join(self, *args, **kwargs):
            super(ReturningThread, self).join(*args, **kwargs)
            if not self._exception is None:
                try:
                    raise self._exception[1].with_traceback(self._exception[2])
                except AttributeError:
                    raise (self._exception[1], None, self._exception[2])
            return self._retval

    t = ReturningThread(None, target, None, args, kwargs)
    t.start()
    retval = t.join(timeout)
    if t.isAlive():
        raise TimeoutError()
    return retval


def timeout_check_call(timeout, *args, **kwargs):
    """
    Call a subprocess with a timeout.

    Like :func:`subprocess.check_call`, but will terminate the process and
    raise :exc:`TimeoutError` if it runs for too long.

    This will only terminate the single process started; any child processes
    will remain running (this has implications for, say, spawing shells.)

    Examples
    ========
    >>> import spacepy.toolbox as tb
    >>> tb.timeout_check_call(1, 'sleep 30', shell=True) #raises TimeoutError

    Parameters
    ==========
    timeout : float
        Timeout, in seconds. Fractions are acceptable but the resolution is of
        order 100ms.
    args : sequence
        Arguments passed through to :class:`subprocess.Popen`
    kwargs : dict
        keyword arguments to pass to :class:`subprocess.Popen`

    Raises
    ======
    TimeoutError : If subprocess does not return in ``timeout`` seconds.
    CalledProcessError : if command has non-zero exit status

    Returns
    =======
    out : int
        0 on successful completion
    """
    resolution = 0.1
    pro = subprocess.Popen(*args, **kwargs)
    starttime = time.time()
    while pro.poll() is None:
        time.sleep(resolution)
        if time.time() - starttime > timeout:
            to = time.time() - starttime
            pro.terminate()
            time.sleep(resolution)
            if pro.poll() is None:
                pro.kill()
            raise TimeoutError('Timed out after {0:.1f} seconds'.format(to))
    if pro.returncode:
        raise subprocess.CalledProcessError(
            pro.returncode, kwargs['args'] if 'args' in kwargs else args[0])
    return 0


if __name__ == "__main__":
    import doctest
    doctest.testmod()
