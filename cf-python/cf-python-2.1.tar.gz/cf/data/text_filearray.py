from numpy import save    as numpy_save
from numpy import ndarray as numpy_ndarray
from numpy import load    as numpy_load

from numpy.ma import array     as numpy_ma_array
from numpy.ma import is_masked as numpy_ma_is_masked

from os import close

from . import FileArray
from ..functions import parse_indices, get_subspace
from ..functions import inspect as cf_inspect
from ..constants import CONSTANTS


# ====================================================================
#
# FileArray object
#
# ====================================================================

class TextFileArray(FileArray):
    '''

A sub-array stored in a file.
    
.. note:: Subclasses must define the following methods:
          `!__getitem__`, `!__str__`, `!close` and `!open`.
    
'''
    def __init__(self, **kwargs):
        '''
        
**Initialization**

:Parameters:

    file : str
        The file name in normalized, absolute form. If the filename
        extension is `!gz` or :py:obj:`bz2`, the file is first
        decompressed.

    dtype : numpy.dtype
        The numpy data type of the data array.

    ndim : int
        Number of dimensions in the data array (0, 1 or 2).

    shape : tuple
        The data array's dimension sizes.

    size : int
        Number of elements in the data array.

'''
        self.__dict__ = kwargs
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
        return "%s in %s" % (self.shape, self.file)
    #--- End: def
    
    def close(self):
        pass
    #--- End: def

    def open(self):
        pass
    #--- End: def

#--- End: class
