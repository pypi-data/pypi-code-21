from numpy import empty      as numpy_empty
from numpy import empty      as numpy_empty
from numpy import frombuffer as numpy_frombuffer
from numpy import full       as numpy_full
from numpy import load       as numpy_load
from numpy import ndarray    as numpy_ndarray
from numpy import save       as numpy_save

from numpy.ma import array     as numpy_ma_array
from numpy.ma import is_masked as numpy_ma_is_masked

from tempfile import mkstemp
from os       import close

from multiprocessing import Array as multiprocessing_Array

from ..functions import parse_indices, get_subspace
from ..functions import inspect as cf_inspect
from ..constants import CONSTANTS


# ====================================================================
#
# FileArray object
#
# ====================================================================

class FileArray(object):
    '''

A sub-array stored in a file.
     
'''
    flags = {'C_CONTIGUOUS': True,
             'OWNDATA'     : True}
             
    def __init__(self, **kwargs):
        '''
        
**Initialization**

:Parameters:

    file : str
        The netCDF file name in normalized, absolute form.

    dtype : numpy.dtype
        The numpy data type of the data array.

    ndim : int
        Number of dimensions in the data array.

    shape : tuple
        The data array's dimension sizes.

    size : int
        Number of elements in the data array.

'''
        self.__dict__ = kwargs
    #--- End: def

    def __array__(self, *dtype):
        '''

Returns a numpy array copy the data array.

:Returns:

    out : numpy.ndarray
        The numpy array copy the data array.

:Examples:

>>> numpy.all(a[...] == numpy.array(a))
True
 
'''
        if not dtype:
            return self[...]
        else:
            return self[...].astype(dtype[0]) #, copy=False) OUght to work!
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __getitem__(self, indices):
        raise NotImplementedError(
            "Class {0} must override the __getitem__ method".format(
                self.__class__.__name))

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''      
        return "<CF %s: %s>" % (self.__class__.__name__, str(self))
    #--- End: def
     
    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return "%s in %s" % (self.shape, self.file)
    #--- End: def

    @property
    def array(self):
        '''
        '''
        return self[...]
    #--- End: def

    @property
    def base(self):
        '''
        '''
        return
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``f.copy() is equivalent to ``copy.deepcopy(f)``.

:Returns:

    out :
        A deep copy.

:Examples:

>>> g = f.copy()

'''
        C = self.__class__
        new = C.__new__(C)
        new.__dict__ = self.__dict__.copy()
        return new
    #--- End: def
    
    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def
        
    def close(self):
        pass
    #--- End: def

    def open(self):
        pass
    #--- End: def

#--- End: class

# ====================================================================
#
# TempFileArray object
#
# ====================================================================

class TempFileArray(FileArray):
    ''' 

A indexable N-dimensional array supporting masked values.

The array is stored on disk in a temporary file until it is
accessed. The directory containing the temporary file may be found and
set with the `cf.TEMPDIR` function.

'''

    def __init__(self, array):
        '''

**Initialization**

:Parameters:

    array : numpy array
        The array to be stored on disk in a temporary file.        

:Examples:

>>> f = TempFileArray(numpy.array([1, 2, 3, 4, 5]))
>>> f = TempFileArray(numpy.ma.array([1, 2, 3, 4, 5]))

'''
        # ------------------------------------------------------------
        # Use mkstemp because we want to be responsible for deleting
        # the temporary file when done with it.
        # ------------------------------------------------------------
        fd, _partition_file = mkstemp(prefix='cf_array_', suffix='.npy', 
                                      dir=CONSTANTS['TEMPDIR'])
        close(fd)

        # The name of the temporary file storing the array
        self._partition_file = _partition_file

        # Numpy data type of the array
        self.dtype = array.dtype
        
        # Tuple of the array's dimension sizes
        self.shape = array.shape
        
        # Number of elements in the array
        self.size = array.size
        
        # Number of dimensions in the array
        self.ndim = array.ndim
        
        numpy_save(_partition_file, self.saveable(array))
#
#        if isinstance(array, SharedMemoryArray):
#            mask = getattr(array, mask, None)
#            if mask is not None:
#                # Mimic numpy.ma.MaskedArray.toflex
#                record = numpy_ndarray(array.shape, 
#                                       dtype=[('_data', array.dtype),
#                                              ('_mask', mask.dtype)])
#                record['_data'] = array
#                record['_mask'] = mask
#                array = record
#            #--- End: if
#            numpy_save(_partition_file, array)
#
#        elif numpy_ma_is_masked(array):
#            # Array is a masked array. Save it as record array with
#            # 'data' and 'mask' elements because this seems much
#            # faster than using numpy.ma.dump.
#            self._masked_as_record = True
#            numpy_save(_partition_file, array.toflex())
#        else:
#            self._masked_as_record = False
#            if hasattr(array, 'mask'):
#                # Array is a masked array with no masked elements
#                numpy_save(_partition_file, array.view(numpy_ndarray))
#            else:
#                # Array is not a masked array.
#                numpy_save(_partition_file, array)
    #--- End: def

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

'''
        array = numpy_load(self._partition_file)

        indices = parse_indices(array.shape, indices)
                   
        array = get_subspace(array, indices)

        if self._masked_as_record:
            # Convert a record array to a masked array
            array = numpy_ma_array(array['_data'], mask=array['_mask'],
                                   copy=False)
            array.shrink_mask()
        #--- End: if

        # Return the numpy array
        return array
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return '%s in %s' % (self.shape, self._partition_file)
    #--- End: def

    def close(self):
        '''

Close all referenced open files.

:Returns:

    None

:Examples:

>>> f.close()

'''     
        # No open files are referenced
        pass
    #--- End: def

    def saveable(self, array):
        '''
        '''
        if numpy_ma_isMaskedArray(array):
            self._masked_as_record = True
            return array.toflex()

        mask = getattr(array, mask, None)
        if mask is not None:
            # Mimic numpy.ma.MaskedArray.toflex
            self._masked_as_record = True
            record = numpy_ndarray(array.shape, 
                                   dtype=[('_data', array.dtype),
                                          ('_mask', mask.dtype)])
            record['_data'] = array
            record['_mask'] = mask
            array = record
        else:
            self._masked_as_record = False
        #--- End: if

        return array
   #--- End: def

#--- End: class

class FilledArray(FileArray):
    '''
**Initialization**

:Parameters:

    dtype : numpy.dtype
        The numpy data type of the data array.

    ndim : int
        Number of dimensions in the data array.

    shape : tuple
        The data array's dimension sizes.

    size : int
        Number of elements in the data array.

    fill_value : scalar, optional

'''

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

        '''
        array_shape = []
        for index in parse_indices(self.shape, indices):
            if isinstance(index, slice):                
                step = index.step
                if step == 1:
                    array_shape.append(index.stop - index.start)
                elif step == -1:
                    stop = index.stop
                    if stop is None:
                        array_shape.append(index.start + 1)
                    else:
                        array_shape.append(index.start - index.stop)
                else:                    
                    stop = index.stop
                    if stop is None:
                        stop = -1
                       
                    a, b = divmod(stop - index.start, step)
                    if b:
                        a += 1
                    array_shape.append(a)
            else:
                array_shape.append(len(index))
        #-- End: for

        if self.fill_value is not None:
            return numpy_full(array_shape, fill_value=self.fill_value, dtype=self.dtype)
        else:
            return numpy_empty(array_shape, dtype=self.dtype)
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return "<CF {0}: shape={1}, dtype={2}, fill_value={3}>".format(
            self.__class__.__name__, self.shape, self.dtype, self.fill_value)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return repr(self)
    #--- End: def

    def reshape(self, newshape):
        '''
'''
        new = self.copy()        
        new.shape = newshape
        new.ndim  = len(newshape)
        return new
    #--- End: def

    def resize(self, newshape):
        '''
'''
        self.shape = newshape
        self.ndim  = len(newshape)
    #--- End: def
#--- End: class

class ArrayInterface(object):
    '''
'''
    def __init__(self, array):
        '''

:Parameters:

    array : numpy.ndarary

'''        
        self.__array_interface__ = array.__array_interface__
        if numpy_ma_isMA(array):
            self.mask = type(self)(array.mask)
        else:        
            self.mask = None

        self.dtype = array.dtype
        self.shape = array.shape
        self.size  = array.size
        self.ndim  = array.ndim

        self.flags = {'C_CONTIGUOUS': array.flags['C_CONTIGUOUS']}
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __getitem__(self, indices):
        '''
'''      
        array = self.array
        indices = parse_indices(array.shape, indices)
        return get_subspace(array, indices)
    #--- End: def

    def __repr__(self):
        '''
        '''        
        out = '<CF {0}: {1}'.format(self.__class__.__name__,         
                                    self.__array_interface__)
        mask = self.mask
        if mask:
            out += ' MASK: {0}>'.format(mask.__array_interface__)
        else:
            out += '>'

        return out
    #--- End: def

    def __str__(self):
        '''
        '''        
        return repr(self)
    #--- End: def

    @property
    def array(self):
        '''
'''
        mask = self.mask
        if not mask:
            array = numpy_array(self, copy=False)
        else:
            array = numpy_ma_array(self, copy=False)
            array.mask = numpy_array(mask, copy=False)

        return array
    #--- End: def

    @property
    def base(self):
        '''
'''
        return self
#        return self.array.base
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``f.copy() is equivalent to ``copy.deepcopy(f)``.

:Returns:

    out :
        A deep copy.

:Examples:

>>> g = f.copy()

'''
        return type(self)(self.array.copy())
    #--- End: def

    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def
        
    def view(self):
        return self.array.view()
    #--- End: def

#--- End: class


class SharedMemoryArray(ArrayInterface):
    '''
    '''
    def __init__(self, array):
        '''
:Parameters:

    array : numpy.ndarary
'''
        # ------------------------------------------------------------
        # Copy the array to a numpy array which accesses shared memory
        # ------------------------------------------------------------
        shape = array.shape
        
        if numpy_ma_isMA(array):
            mask = array.mask
            array = array.data
        else:
            mask = None
        
        dtype = array.dtype
        mp_Array = multiprocessing_Array(_typecode[dtype.char], array.size)
        a = numpy_frombuffer(mp_Array.get_obj(), dtype=dtype)
        a.resize(shape)
        a[...] = array
        
        if mask is not None:
            mask = array.mask
            dtype = mask.dtype
            mp_Array = multiprocessing_Array(_typecode[dtype.char], mask.size)
            m = numpy_frombuffer(mp_Array.get_obj(), dtype=dtype)
            m.resize(shape)
            m[...] = mask
        
            a = numpy_ma_array(a, copy=False)
            a.mask = m
        #--- End: if

        #-------------------------------------------------------------
        # Store the array interface of the numpy array
        #-------------------------------------------------------------
        super(SharedMemoryArray, self).__init__(a)
    #--- End: def

#--- End: class
