from struct import unpack as struct_unpack

from numpy import arange       as numpy_arangex
from numpy import array        as numpy_array
#from numpy import column_stack as numpy_column_stack
from numpy import dtype        as numpy_dtype
from numpy import fromfile     as numpy_fromfile
from numpy import memmap       as numpy_memmap
#from numpy import result_type  as numpy_result_type
from numpy import where        as numpy_where

from numpy.ma import array        as numpy_ma_array
#from numpy.ma import column_stack as numpy_ma_column_stack
from numpy.ma import isMA         as numpy_ma_isMA 
from numpy.ma import masked_where as numpy_ma_masked_where
from numpy.ma import where        as numpy_ma_where

from unwgdos import unwgdos

from ..constants import _file_to_fh
from ..functions import (open_files_threshold_exceeded,
                         close_one_file,
                         parse_indices,
                         get_subspace)

from ..data.filearray import FileArray

_filename_to_file = _file_to_fh.setdefault('PP', {})

# ====================================================================
#
# PPFileArray object
#
# ====================================================================

class PPFileArray(FileArray):
    ''' 
    
A sub-array stored in a PP file.
    
**Initialization**

:Parameters:

    file : str
        The PP file name in normalized, absolute form.

    dtype : numpy.dtype
        The numpy data type of the data array.

    ndim : int
        The number of dimensions in the data array.

    shape : tuple
        The data array's dimension sizes.

    size : int
        The number of elements in the data array.

    file_offset : int
        The start position in the file of the data array.

**Examples**

>>> ppfile
<open file 'file.pp', mode 'rb' at 0xc45e00>
>>> a = PPFileArray(file=ppfile.name, file_offset=ppfile.tell(),
...                 dtype=numpy.dtype('float32'), shape=(73, 96),
...                 size=7008, ndim=2)

'''
    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

''' 
        pp = self.open()
        pp.seek(self.file_offset, 0)

        # ------------------------------------------------------------
        # Read the first block control word
        # ------------------------------------------------------------
        bcw1 = struct_unpack('>i', pp.read(4))[0]

        if bcw1 == 256:
            # File is big endian
            endian = '>'
        elif bcw1 == 65536: 
            # File is little endian
            endian = '<'
        else:
            raise ValueError(
                "Can't read PP field from %s: 1st block control word (at offset %d) = %s" % 
                (self.file, self.file_offset, bcw1))

#        print 'file_offset, bcw1=', self.file_offset, bcw1

        # ------------------------------------------------------------
        # Read the integer and real headers and the 2nd and 3rd block
        # control words
        # ------------------------------------------------------------
        header = struct_unpack(endian+'45i21f', pp.read(264))
#        print 'header=',header

        if header[38] == 2:     # header[38] is LBUSER1
            d = numpy_dtype('int32')
        else:
            d = numpy_dtype('float32')

        d = d.newbyteorder(endian)

        lbpack = header[20]
        lblrec = header[14]

        # Set the fill_value from BMDI
        fill_value = header[62]
        if fill_value == -1.0e30:
            # -1.0e30 is the flag for the no missing data
            fill_value = None
        elif d.kind == 'i':
            # The fill_value must be of the same type as the data
            # values
            fill_value= int(fill_value)       

        if not lbpack:
            # --------------------------------------------------------
            # Data array is not packed
            # --------------------------------------------------------
            if indices is Ellipsis:
                delete_memmap = False
                
                array = numpy_fromfile(pp, dtype=d, count=lblrec)
                array.resize(self.shape)
            else:
                delete_memmap = True

                mm_array = numpy_memmap(pp, mode='r',
                                        offset=self.file_offset + 268,
                                        dtype=d, 
                                        shape=self.shape)
                
                indices = parse_indices(mm_array, indices)               
                array   = get_subspace(mm_array, indices)                
                array   = array.copy() ## ???

        else:
            # --------------------------------------------------------
            # Data array is packed
            # --------------------------------------------------------
            delete_memmap = False

            array = pp.read((lblrec-header[19])*4)

            if lbpack == 1:
                # ----------------------------------------------------
                # WGDOS packing
                # ----------------------------------------------------
                array = unwgdos(array, 4, self.size, fill_value)
                array.resize(self.shape)

            else:
                raise ValueError(
                    "PP field in %s has unknown packing flag: lbpack=%d" % 
                    (self.file, lbpack))
            
            if indices is not Ellipsis:
                indices = parse_indices(array, indices)               
                array   = get_subspace(array, indices)
        #--- End: if

        # ------------------------------------------------------------
        # Convert to a masked array
        # ------------------------------------------------------------
        if fill_value is not None:
            # Mask any missing values
            mask = (array == fill_value)
            masked = mask.any()
            if masked:
                array = numpy_ma_masked_where(mask, array, copy=False)    
        else:
            # There is no missing data
            array = numpy_array(array, copy=True) ##???
            masked = False

        if delete_memmap:
            # Close the memory mapped file
            del mm_array

        # ------------------------------------------------------------
        # Unpack the array using the scale_factor and add_offset, if
        # either is available
        # ------------------------------------------------------------
        # Treat BMKS as a scale_factor if it is not 0 or 1
        scale_factor = header[63]
        if scale_factor != 1.0 and scale_factor != 0.0:
            if d.kind == 'i':
                array *= int(scale_factor)
            else:
                array *= scale_factor

        # Treat BDATUM as an add_offset if it is not 0
        add_offset = header[49]
        if add_offset != 0.0:
            if d.kind == 'i':
                array += int(add_offset)
            else:
                array += add_offset

        if self.dtype.kind == 'b':
            array = array.astype(bool)

        # ------------------------------------------------------------
        # Return the numpy array
        # ------------------------------------------------------------
        return array
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''      
        return "%s%s in %s" % (self.file_offset, self.shape, self.file)
    #--- End: def

    @property
    def  file_pointer(self):
        '''
'''
        return (self.file, self.file_offset)
    #--- End: def

    def close(self):
        '''

Close the file containing the data array.

If the file is not open then no action is taken.

:Returns:

    None

**Examples**

>>> f.close()

'''
        pp = _filename_to_file.pop(self.file, None)
        if pp is not None:
            pp.close()
    #--- End: def
   
    def open(self):
        '''

Return the 

:Returns:

    out : file

**Examples**

>>> f.open()

'''    
        filename = self.file

        pp = _filename_to_file.get(filename, None)
        
        if pp is not None:
            # File is already open
            return pp
      
        if open_files_threshold_exceeded():
            # Close an arbitrary data file to make way for this one
            close_one_file()

        # Open the file            
        pp = open(filename, 'rb')

        # Update dictionary
        _filename_to_file[filename] = pp

        return pp
    #--- End: def

#--- End: class


# ====================================================================
#
# PPFileArrayBounds object
#
# ====================================================================

class PPFileArrayBounds(FileArray):
    '''  
    
'''

    def __init__(self, **kwargs):
        '''

**Initialization**

:Parameters:

    _lower : PPFileArray

    _upper : PPFileArray

'''
        super(PPFileArrayBounds, self).__init__(**kwargs)

        lower = self._lower

        self.dtype = numpy_result_type(lower.dtype, self._upper.dtype)
        self.shape = lower.shape + (2,)       
        self.size  = lower.size * 2
        self.ndim  = lower.ndim + 1
    #--- End: def
   
    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

'''
        # ------------------------------------------------------------
        # Read the upper and lower bounds from the PP file and stick
        # them together
        # ------------------------------------------------------------
        lower = self._lower[...]
        upper = self._upper[...]

        if numpy_ma_isMA(lower) or numpy_ma_isMA(upper):
            array = numpy_ma_column_stack((lower, upper))
        else:
            array = numpy_column_stack((lower, upper))

        indices = parse_indices(array, indices)

        return get_subspace(array, indices)
    #--- End: def
  
    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return '%s%s' % (self.__class__.__name__, self.shape)
    #--- End: def
   
    def close(self):
        '''

Close the file containing the data array.

If the file is not open then no action is taken.

:Returns:

    None

**Examples**

>>> f.close()

'''
        # An instance references no open files
        pass
    #--- End: def
   
    def copy(self):
        '''

Return a deep copy.

``f.copy()`` is equivalent to ``copy.deepcopy(f)``.

:Returns:

    out :
        A deep copy.
    
**Examples**

>>> g = f.copy()

'''  
        return type(self)(_lower=self._lower.copy(), _upper=self._upper.copy())
    #--- End: def
    
#--- End: class

## ====================================================================
##
## PPc object
##
## ====================================================================
#
#class PPc(FileArray):
#    ''' 
#    
#**Initialization**
#
#:Parameters:
#
#    file : str
#        The PP file name in normalized, absolute form.
#
#    dtype : numpy.dtype
#        The numpy data type of the data array.
#
#    ndim : int
#        The number of dimensions in the data array.
#
#    shape : tuple
#        The data array's dimension sizes.
#
#    size : int
#        The number of elements in the data array.
#
#    file_offset : int
#        The start position in the file of the data array.
#
#**Examples**
#
#>>> ppfile
#<open file 'file.pp', mode 'rb' at 0xc45e00>
#>>> a = PPFileArray(file=ppfile.name, file_offset=ppfile.tell(),
#...                 dtype=numpy.dtype('float32'), shape=(73, 96),
#...                 size=7008, ndim=2)
#
#'''
#    def __init__(self, bz, bd, size, dtype):
#        '''
#'''
#        self.bz    = bz
#        self.dd    = bd
#        self.size  = size
#        self.dtype = dtype
#        self.shape = (size,)
#        self.ndim  = 1
#    #--- End: def
#
#    def __getitem__(self, indices):
#        '''
#
#x.__getitem__(indices) <==> x[indices]
#
#Returns a numpy array.
#
#''' 
#        bz = self.bz
#        bd = self.bd
#        array = numpy_arange(bz+bd, bz+bd*(self.size+1), bd,
#                             dtype=self.dtype) 
#
#        if indices is not Ellipsis:
#            indices = parse_indices(array, indices)
#            array = get_subspace(array, indices)
#
#        return array
#    #--- End: def
#
#    def __hash__(self):
#        '''
#
#The built-in function `hash`
#'''
#        return hash((self.bz, self.bd, self.size))
#    #--- End: def
#
#    def __str__(self):
#        '''
#
#x.__str__() <==> str(x)
#
#'''
#        return 'bz=%s bd=%d size=%d' % \
#            (self.bz, self.bd, self.size)
#    #--- End: def
#    
##--- End: class

