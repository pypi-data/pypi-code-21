import operator

import numpy
import netCDF4
import cfdm

from ..functions import parse_indices, open_files_threshold_exceeded

_file_to_fh       = {}
_file_to_fh_write = {}

_debug = False


# ====================================================================
#
# NetCDFArray object
#
# ====================================================================

class NetCDFArray(cfdm.data.array.NetCDFArray):
    '''A sub-array stored in a netCDF file.
    
**Initialization**

:Parameters:

    file: `str`
        The netCDF file name in normalized, absolute form.

    dtype: `numpy.dtype`
        The numpy data type of the data array.

    ndim: `int`
        Number of dimensions in the data array.

    shape: `tuple`
        The data array's dimension sizes.

    size: `int`
        Number of elements in the data array.

    ncvar: `str`, optional
        The netCDF variable name containing the data array. Must be
        set if *varid* is not set.

    varid: `int`, optional
        The netCDF ID of the variable containing the data array. Must
        be set if *ncvar* is not set. Ignored if *ncvar* is set.

#    ragged: `int`, optional
#        Reduction in logical rank due to ragged array representation.
#
#    gathered: `int`, optional
#        Reduction in logical rank due to compression by gathering.

:Examples:

>>> import netCDF4
>>> import os
>>> nc = netCDF4.Dataset('file.nc', 'r')
>>> v = nc.variable['tas']
>>> a = NetCDFFileArray(file=os.path.abspath('file.nc'), ncvar='tas',
                        dtype=v.dtype, ndim=v.ndim, shape=v.shape,
                        size=v.size)

    '''    
           
    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

'''
        nc = self.open()
        
        indices = tuple(parse_indices(self.shape, indices))
        
        ncvar = getattr(self, 'ncvar', None)

        if ncvar is not None:
            # Get the variable by name
            array = nc.variables[ncvar][indices]
        else:
            # Get the variable by netCDF ID
            varid = self.varid
            for value in nc.variables.itervalues():
                if value._varid == varid:
                    array = value[indices]
                    break
        #--- End: if

        if not self.ndim:
            # Hmm netCDF4 has a thing for making scalar size 1 , 1d
            array = array.squeeze()

        # ------------------------------------------------------------
        # If approriate, collapse (by concatenation) the outermost
        # (fastest varying) dimension of string valued array into
        # memory. E.g. [['a','b','c']] becomes ['abc']
        # ------------------------------------------------------------
        if array.dtype.kind == 'S' and array.ndim > (self.ndim -
                                                     getattr(self, 'gathered', 0) -
                                                     getattr(self, 'ragged', 0)):
            strlen = array.shape[-1]
            
            new_shape = array.shape[0:-1]
            new_size  = long(reduce(operator.mul, new_shape, 1))
            
            array = numpy.ma.resize(array, (new_size, strlen))
            
            array = array.filled(fill_value='')

            array = numpy.array([''.join(x).rstrip() for x in array],
                                dtype='S%d' % strlen)
            
            array = array.reshape(new_shape)

            array = numpy.ma.where(array=='', numpy.ma.masked, array)
        #--- End: if
        
        return array
    #--- End: def

    @classmethod
    def file_open(cls, filename, mode, fmt=None):
        '''Return an open `netCDF4.Dataset` for a netCDF file.

:Returns:

    out: `netCDF4.Dataset`

:Examples:

>>> f.file_open(filename, 'r')
<netCDF4.Dataset at 0x115a4d0>

        '''
        if mode == 'r':
            files = _file_to_fh
        else:
            files = _file_to_fh_write

        if filename in files:
            # File is already open
            return files[filename]
        elif open_files_threshold_exceeded():
            # Close a random data file to make way for this one
            for f in _file_to_fh:                    
                cls.file_close(f)
                break

        if mode in ('a', 'r+'):
            if not isfile(filename):
                nc = netCDF4.Dataset(filename, 'w', format=fmt) 
                nc.close()
            elif filename in files:
                cls.close_file(filename)
        #--- End: if
        
        try:        
            nc = netCDF4.Dataset(filename, mode, format=fmt)
        except RuntimeError as runtime_error:
            raise RuntimeError("{}: {}".format(runtime_error, filename))
        
        files[filename] = nc

        return nc
    #--- End: def

#--- End: class

#class GatheredArray(Array):
#    '''
#    '''        
#    def __getitem__(self, indices):
#        '''
#        '''
#
#        array = numpy.ma.masked_all(self.shape, dtype=dtype)
#        
#        compressed_axes = range(self.sample_axis, array.ndim - (self.gathered_array.ndim - self.sample_axis - 1))
#        
#        zzz = [reduce(operator.mul, [array.shape[i] for i in compressed_axes[i:]], 1)
#               for i in range(1, len(compressed_axes))]
#        
#        xxx = [[0] * self.indices.size for i in compressed_axes]
#
#
#        for n, b in enumerate(self.indices.varray):
#            if not zzz or b < zzz[-1]:
#                xxx[-1][n] = b
#                continue
#            
#            for i, z in enumerate(zzz):
#                if b >= z:
#                    (a, b) = divmod(b, z)
#                    xxx[i][n] = a
#                    xxx[-1][n] = b
#        #--- End: for
#
#        uncompressed_indices = [slice(None)] * array.ndim        
#        for i, x in enumerate(xxx):
#            uncompressed_indices[sample_axis+i] = x
#
#        array[tuple(uncompressed_indices)] = self.gathered_array[...]
#
#        if indices is Ellpisis:
#            return array
#
#        indices = parse_indices(array.shape, indices)
#        array = self.get_subspace(array, indices)
#        
#        return array
