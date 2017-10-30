import netCDF4
import random
import json
import os

from os      import remove
from os.path import isfile
from os.path import expandvars as os_path_expandvars
from os.path import expanduser as os_path_expanduser
from string  import hexdigits

from numpy import array       as numpy_array
from numpy import bool_       as numpy_bool_
from numpy import dtype       as numpy_dtype
from numpy import ndindex     as numpy_ndindex
from numpy import integer     as numpy_integer
from numpy import intersect1d as numpy_intersect1d
from numpy import floating    as numpy_floating
from numpy import size        as numpy_size

from numpy.ma import empty  as numpy_ma_empty
from numpy.ma import isMA   as numpy_ma_isMA
from numpy.ma import masked as numpy_ma_masked

from ..                import __Conventions__
from ..boundedvariable import Bounds
from ..cfdatetime      import dt2rt
from ..coordinate      import Coordinate
#from ..coordinatebounds import CoordinateBounds
from ..field           import Field, FieldList
from ..functions       import equals, flat, relpath, abspath

from ..data.data       import Data

from .filearray import NetCDFFileArray
from .functions import _close_netcdf_file, _open_netcdf_file

class NetCDFError(Exception):
    '''A runtime netCDF error'''
    pass

def write(fields, filename, fmt='NETCDF4', overwrite=True,
          verbose=False, cfa_options=None, mode='w',
          least_significant_digit=None, endian='native', compress=0,
          fletcher32=False, no_shuffle=False, datatype=None,
          single=False, double=False, reference_datetime=None,
          variable_attributes=None, HDF_chunks=None, unlimited=None,
          _debug=False):
    '''Write fields to a CF-netCDF or CFA-netCDF file.
    
NetCDF dimension and variable names will be taken from variables'
`!ncvar` attributes and the field attribute `!ncdimensions` if
present, otherwise they are inferred from standard names or set to
defaults. NetCDF names may be automatically given a numerical suffix
to avoid duplication.

Output netCDF file global properties are those which occur in the set
of CF global properties and non-standard data variable properties and
which have equal values across all input fields.

Logically identical field components are only written to the file
once, apart from when they need to fulfil both dimension coordinate
and auxiliary coordinate roles for different data variables.

:Parameters:

    fields : (arbitrarily nested sequence of) cf.Field or cf.FieldList
        The field or fields to write to the file.

    filename : str
        The output CF-netCDF file. Various type of expansion are
        applied to the file names:
        
          ====================  ======================================
          Expansion             Description
          ====================  ======================================
          Tilde                 An initial component of ``~`` or
                                ``~user`` is replaced by that *user*'s
                                home directory.
           
          Environment variable  Substrings of the form ``$name`` or
                                ``${name}`` are replaced by the value
                                of environment variable *name*.
          ====================  ======================================
    
        Where more than one type of expansion is used in the same
        string, they are applied in the order given in the above
        table.

          Example: If the environment variable *MYSELF* has been set
          to the "david", then ``'~$MYSELF/out.nc'`` is equivalent to
          ``'~david/out.nc'``.
  
    fmt : str, optional
        The format of the output file. One of:

           =====================  ================================================
           fmt                    Description
           =====================  ================================================
           ``'NETCDF3_CLASSIC'``  Output to a CF-netCDF3 classic format file
           ``'NETCDF3_64BIT'``    Output to a CF-netCDF3 64-bit offset format file
           ``'NETCDF4_CLASSIC'``  Output to a CF-netCDF4 classic format file
           ``'NETCDF4'``          Output to a CF-netCDF4 format file
           ``'CFA3'``             Output to a CFA-netCDF3 classic format file 
           ``'CFA4'``             Output to a CFA-netCDF4 format file 
           =====================  ================================================

        By default the *fmt* is ``'NETCDF3_CLASSIC'``. Note that the
        netCDF3 formats may be slower than any of the other options.

    overwrite: bool, optional
        If False then raise an exception if the output file
        pre-exists. By default a pre-existing output file is over
        written.

    verbose : bool, optional
        If True then print one-line summaries of each field written.

    cfa_options : dict, optional
        A dictionary giving parameters for configuring the output
        CFA-netCDF file:

           ==========  ===============================================
           Key         Value
           ==========  ===============================================
           ``'base'``  * If ``None`` (the default) then file names
                         within CFA-netCDF files are stored with
                         absolute paths.

                       * If set to an empty string then file names
                         within CFA-netCDF files are given relative to
                         the directory or URL base containing the
                         output CFA-netCDF file.

                       * If set to a string then file names within
                         CFA-netCDF files are given relative to the
                         directory or URL base described by the
                         value. For example: ``'../archive'``.
           ==========  ===============================================        

        By default no parameters are specified.
    
    mode : str, optional
        Specify the mode of write access for the output file. One of:
 
           =======  ==================================================
           mode     Description
           =======  ==================================================
           ``'w'``  Create the file. If it already exists and
                    *overwrite* is True then the file is deleted prior
                    to being recreated.
           =======  ==================================================
       
        By default the file is opened with write access mode ``'w'``.
    
    datatype : dict, optional
        Specify data type conversions to be applied prior to writing
        data to disk. Arrays with data types which are not specified
        remain unchanged. By default, array data types are preserved
        with the exception of booleans (``numpy.dtype(bool)``, which
        are converted to 32 bit integers.

          **Example:**
            To convert 64 bit floats and integers to their 32 bit
            counterparts: ``dtype={numpy.dtype(float):
            numpy.dtype('float32'), numpy.dtype(int):
            numpy.dtype('int32')}``.

:Returns:

    None

:Raises:

    IOError :
        If *overwrite* is False and the output file pre-exists.

    ValueError :
        If a field does not have information required to write certain
        aspects of a CF-netCDF file.

:Examples:

>>> f
[<CF Field: air_pressure(30, 24)>,
 <CF Field: u_compnt_of_wind(19, 29, 24)>,
 <CF Field: v_compnt_of_wind(19, 29, 24)>,
 <CF Field: potential_temperature(19, 30, 24)>]
>>> write(f, 'file')

>>> type(f)
<class 'cf.field.FieldList'>
>>> type(g)
<class 'cf.field.Field'>
>>> cf.write([f, g], 'file.nc', verbose=True)
[<CF Field: air_pressure(30, 24)>,
 <CF Field: u_compnt_of_wind(19, 29, 24)>,
 <CF Field: v_compnt_of_wind(19, 29, 24)>,
 <CF Field: potential_temperature(19, 30, 24)>]

    '''    
    compress = int(compress)
    zlib = bool(compress) 

    if fmt not in ('NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'CFA3',
                   'NETCDF4', 'NETCDF4_CLASSIC', 'CFA4'):
        raise ValueError("Unknown output file format: {}".format(fmt))

    if compress and fmt in ('NETCDF3_CLASSIC', 'NETCDF3_64BIT', 'CFA3'):
        raise ValueError("Can't compress {} format file".format(fmt))
    
    if least_significant_digit and fmt in ('CFA3', 'CFA4'):
        raise ValueError("Can't truncate data variables in {} format file".format(fmt))

    # ----------------------------------------------------------------
    # Set up non-global attributes
    # ----------------------------------------------------------------
    if variable_attributes:
        if isinstance(variable_attributes, basestring):
            variable_attributes = set((variable_attributes,))
        else:
            variable_attributes = set(variable_attributes)
    else:
        variable_attributes = set()

    # ----------------------------------------------------------------
    # Set up data type conversions. By default, booleans are converted
    # to 32-bit integers and python objects are converted to 64-bit
    # floats.
    # ----------------------------------------------------------------
    dtype_conversions = {numpy_dtype(bool)  : numpy_dtype('int32'),
                         numpy_dtype(object): numpy_dtype(float)}
    if datatype:
        if single:
            raise ValueError("Can't set datatype and single")
        if double:
            raise ValueError("Can't set datatype and double")
        dtype_conversions.update(datatype)
    else:
        if single and double:
            raise ValueError("Can't set single and double")
        if single:
            dtype_conversions[numpy_dtype(float)] = numpy_dtype('float32')
            dtype_conversions[numpy_dtype(int)]   = numpy_dtype('int32')
        if double:
            dtype_conversions[numpy_dtype('float32')] = numpy_dtype(float)
            dtype_conversions[numpy_dtype('int32')]   = numpy_dtype(int)
    datatype = dtype_conversions

    if not unlimited:
        unlimited = ()

    # ----------------------------------------------------------------
    # Initialize dictionary of useful global variables
    # ----------------------------------------------------------------
    g = {'netcdf'           : None,    # - netCDF4.Dataset instance
                                       #-----------------------------
         'nc'               : {},      # - Map netCDF variable names
                                       #   to netCDF4.Variable
                                       #   instances
         'ncdim_to_size'    : {},      # - Map netCDF dimension names
                                       #   to netCDF dimension sizes
         'ncpdim_to_size'   : {},      # - Dictionary of PARTITION
                                       #   dimension sizes keyed by
                                       #   netCDF dimension names.
                                       #-----------------------------
         'seen'             : {},      # - Dictionary of netCDF
                                       #   variable names and netCDF
                                       #   dimensions keyed by items
                                       #   of the field (such as a
                                       #   coordinate or a coordinate
                                       #   reference).
                                       #-----------------------------
         'ncvar_names'      : set(()), # - Set of all netCDF
                                       #   dimension and netCDF
                                       #   variable names.
         'global_properties': set(()), # - Set of global or
                                       #   non-standard CF properties
                                       #   which have identical
                                       #   values across all input
                                       #   fields.
                                       #-----------------------------
         'variable_attributes': variable_attributes,
         'bounds' : {},
         # -----------------------------------------------------------
         # CFA parameters
         # -----------------------------------------------------------
         'cfa'        : False,   # - flag to use the CFA
                                 #   convention, or not.
         'cfa_options': {},      # - 
         'CFA_ncdims' : set(()), # - set of all private CFA
                                 #   netCDF dimension names.
         # -----------------------------------------------------------
         # Compression/endian
         # -----------------------------------------------------------
         'compression'            : {'zlib'       : zlib,
                                     'complevel'  : compress,
                                     'fletcher32' : fletcher32,
                                     'shuffle'    : not no_shuffle},
         'endian'                 : endian,
         'least_significant_digit': least_significant_digit,
         # -----------------------------------------------------------
         # CF properties which need not be set on bounds if they're
         # set on the parent coordinate
         # -----------------------------------------------------------
         'omit_bounds_properties': ('units', 'standard_name', 'axis',
                                    'positive', 'calendar', 'month_lengths',
                                    'leap_year', 'leap_month'),
         # ------------------------------------------------------------
         # Specify data type conversions to be applied prior to writing
         # ------------------------------------------------------------
         'datatype': datatype,
         # ------------------------------------------------------------
         # Specify unit conversions to be applied prior to writing
         # ------------------------------------------------------------
         'reference_datetime': reference_datetime,
         # ------------------------------------------------------------
         # 
         # ------------------------------------------------------------
         'unlimited': unlimited,
         # -----------------------------------------------------------
         # Miscellaneous
         # -----------------------------------------------------------
         'verbose': verbose,
         '_debug' : _debug,
    }

    if fmt == 'CFA3':
        g['cfa'] = True
        fmt = 'NETCDF3_CLASSIC'
        if cfa_options:
            g['cfa_options'] = cfa_options
    elif fmt == 'CFA4':
        g['cfa'] = True
        fmt = 'NETCDF4'
        if cfa_options:
            g['cfa_options'] = cfa_options  
    #--- End: if

    g['fmt'] = fmt

    # ---------------------------------------------------------------
    # Flatten the sequence of intput fields
    # ---------------------------------------------------------------
    fields = FieldList(flat(fields))

    # ---------------------------------------------------------------
    # Still here? Open the output netCDF file.
    # ---------------------------------------------------------------
#    if mode != 'w':
#        raise ValueError("Can only set mode='w' at the moment")

    filename = os_path_expanduser(os_path_expandvars(filename))

    if mode == 'w' and isfile(filename):
        if not overwrite:
            raise IOError(
                "Can't write to an existing file unless overwrite=True: {}".format(
                    abspath(filename)))
                
        if not os.access(filename, os.W_OK):
            raise IOError(
                "Can't overwrite an existing file without permission: {}".format(
                    abspath(filename)))
            
        _close_netcdf_file(filename)
        remove(filename)
    #--- End: if          

    g['netcdf'] = _open_netcdf_file(filename, mode, fmt)
#netCDF4.Dataset(filename, mode, format=fmt)

    # ---------------------------------------------------------------
    # Set the fill mode for a Dataset open for writing to off. This
    # will prevent the data from being pre-filled with fill values,
    # which may result in some performance improvements.
    # ---------------------------------------------------------------
    g['netcdf'].set_fill_off()

    # ---------------------------------------------------------------
    # Write global properties to the file first. This is important as
    # doing it later could slow things down enormously. This function
    # also creates the g['global_properties'] set, which is used in
    # the _write_a_field function.
    # ---------------------------------------------------------------
    _create_global_properties(fields, g=g)

    # ---------------------------------------------------------------
    # ---------------------------------------------------------------
    for f in fields:

        # Set HDF chunking
        org_chunks = f.HDF_chunks(HDF_chunks)
        default_chunks = f.HDF_chunks()
        chunks = org_chunks.copy()
        shape = f.shape
        for i, size in org_chunks.iteritems():
            if size is None:
                size = default_chunks[i]
            dim_size = shape[i]
            if size is None or size > dim_size:
                size = dim_size
            chunks[i] = size
        #--- End: for
        f.HDF_chunks(chunks)

        # Write the field
        _write_a_field(f, g=g)

        # Reset HDF chunking
        f.HDF_chunks(org_chunks)

#        if verbose == 1:
#            for e in f:            
#                print repr(e)
    #-- End: for

    # ---------------------------------------------------------------
    # Write all of the buffered data to disk
    # ---------------------------------------------------------------
    g['netcdf'].close()
#--- End: def

#def _check_name(base, counter, g=None, dimsize=None, cfa=False):
def _check_name(base, g=None, dimsize=None, cfa=False):
    '''

:Parameters:

    base : str

#    counter : int

    g : dict

    dimsize : int, optional

    cfa : bool, optional

:Returns:

    ncvar : str
        NetCDF dimension name or netCDF variable name.

#    counter : int

'''
    ncvar_names = g['ncvar_names']

    if dimsize is not None:
        if not cfa:
            if base in ncvar_names and dimsize == g['ncdim_to_size'][base]:
                # Return the name of an existing netCDF dimension with
                # this size
                return base #, counter
            
        elif base in g['CFA_ncdims']:
            # Return the name of an existing private CFA-netCDF
            # dimension with this size
            return base #, counter
    #--- End: if

    if base in ncvar_names:


        counter = g.setdefault('count_'+base, 1)
    
    #        ncvar = '%(base)s_%(counter)d' % locals()
        ncvar = '{0}_{1}'.format(base, counter)
        while ncvar in ncvar_names:
            counter += 1
#            ncvar = '%(base)s_%(counter)d' % locals()
            ncvar = '{0}_{1}'.format(base, counter)
    else:
        ncvar = base

    ncvar_names.add(ncvar)

    return ncvar #, counter
#--- End: def

def _write_attributes(netcdf_var, netcdf_attrs):
    '''

:Parameters:

    netcdf_var : netCDF4.Variable

    netcdf_attrs : dict

:Returns:

    None

:Examples:


'''
    if hasattr(netcdf_var, 'setncatts'):
        # Use the faster setncatts
        netcdf_var.setncatts(netcdf_attrs)
    else:
        # Otherwise use the slower setncattr
        for attr, value in netcdf_attrs.iteritems():
            netcdf_var.setncattr(attr, value)
#--- End: def

def _character_array(array):
    '''

Convert a numpy string array to a numpy character array wih an extra
trailing dimension.

:Parameters:

    array : numpy array

:Returns:

    out : numpy array

:Examples:

>>> print a, a.shape, a.dtype.itemsize
['fu' 'bar'] (2,) 3
>>> b = _character_array(a)
>>> print b, b.shape, b.dtype.itemsize
[['f' 'u' ' ']
 ['b' 'a' 'r']] (2, 3) 1

>>> print a, a.shape, a.dtype.itemsize
[-- 'bar'] (2,) 3
>>> b = _character_array(a)
>>> print b, b.shape, b.dtype.itemsize
[[-- -- --]
 ['b' 'a' 'r']] (2, 3) 1

'''
    strlen = array.dtype.itemsize
    shape  = array.shape

    new = numpy_ma_empty(shape + (strlen,), dtype='S1')
    
    for index in numpy_ndindex(shape):
        value = array[index]
        if value is numpy_ma_masked:
            new[index] = numpy_ma_masked
        else:
            new[index] = tuple(value.ljust(strlen, ' ')) 
    #--- End: for

    return new
#--- End: def

def _datatype(variable, g=None):
    '''

Return the netCDF4.createVariable datatype corresponding to the
datatype of the array of the input variable

For example, if variable.dtype is 'float32', then 'f4' will be
returned.

Numpy string data types will return 'S1' regardless of the numpy
string length. This means that the required conversion of
multi-character datatype numpy arrays into single-character datatype
numpy arrays (with an extra trailing dimension) is expected to be done
elsewhere (currently in the _create_netcdf_variable function).

If the input variable has no `!dtype` attribute (or it is None) then
'S1' is returned.

:Parameters:

    variable : 
        Any object with a `!dtype` attribute whose value is a
        `numpy.dtype` object or None.

    g : dict

:Returns:

    out : str
        The netCDF4.createVariable datatype corresponding to the
        datatype of the array of the input variable.

'''
    if (not hasattr(variable, 'dtype') or
        variable.dtype.char == 'S'     or
        variable.dtype is None):
        return 'S1'            

    dtype = variable.dtype

    convert_dtype = g['datatype']

    new_dtype = convert_dtype.get(dtype, None)
    if new_dtype is not None:
        dtype = new_dtype
        
    return '{0}{1}'.format(dtype.kind, dtype.itemsize)
#--- End: def

def _string_length_dimension(size, g=None):
    '''

Create, if necessary, a netCDF dimension for string variables.

:Parameters:

    size : int

    g : dict


:Returns:

    out : str
        The netCDF dimension name.

'''
    # ----------------------------------------------------------------
    # Create a new dimension for the maximum string length
    # ----------------------------------------------------------------
    ncdim = _check_name('strlen{0}'.format(size), dimsize=size, g=g)
    
    if ncdim not in g['ncdim_to_size']:
        # This string length dimension needs creating
        g['ncdim_to_size'][ncdim] = size
        g['netcdf'].createDimension(ncdim, size)
    #--- End: if

    return ncdim
#--- End: def

def _random_hex_string(size=10):
    '''

Return a random hexadecimal string with the given number of
characters.

:Parameters:

    size : int, optional
        The number of characters in the generated string.

:Returns:

    out : str
        The hexadecimal string.

:Examples:

>>> _random_hex_string()
'C3eECbBBcf'
>>> _random_hex_string(6)
'7a4acc'

'''                        
    return ''.join(random.choice(hexdigits) for i in xrange(size))
#--- End: def
    
def _cfa_dimension(size, g=None):
    '''

Write a private CFA dimension to the netCDF file, unless one for the
given size already exists. In either case returns the netCDF dimension
name.

.. note:: This function updates ``g['CFA_ncdims']``,
          ``g['ncvar_names']``, ``g['netcdf']``.

:Parameters:

  
    size : int
        The size of the private CFA dimension.

    g : dict

:Returns:

     out : str
         The netCDF dimension name.

:Examples:

>>> _cfa_dimension(10, g=g)
'cfa10'

'''        
    ncdim = _check_name('cfa{0}'.format(size), g=g, 
                        dimsize=size, cfa=True)

    if ncdim not in g['CFA_ncdims']:
        g['CFA_ncdims'].add(ncdim)
        g['netcdf'].createDimension(ncdim, size)

    return ncdim
#--- End: def

def _write_cfa_variable(ncvar, ncdimensions, netcdf_attrs, data, g=None):
    '''

Write a CFA variable to the netCDF file.

Any CFA private variables required will be autmatically created and
written to the file.

:Parameters:

    ncvar : str
        The netCDF name for the variable.

    ncdimensions : sequence of str

    netcdf_attrs : dict

    data : cf.Data
        
    g : dict

:Returns:

    None

:Examples:

'''
    datatype = _datatype(data, g=g)

    fill_value = data.fill_value # False, None speed?

    g['nc'][ncvar] = g['netcdf'].createVariable(ncvar, datatype, (),
                                                fill_value=fill_value,
                                                least_significant_digit=None,
                                                endian=g['endian'],
                                                **g['compression'])

    netcdf_attrs['cf_role']        = 'cfa_variable'
    netcdf_attrs['cfa_dimensions'] = ' '.join(ncdimensions)

    # Create a dictionary representation of the data object
    data = data.copy()
    axis_map = {}
    for axis0, axis1 in zip(data._axes, ncdimensions):
        axis_map[axis0] = axis1
#    print axis_map, data._axes
    data._change_axis_names(axis_map)
    data._move_flip_to_partitions()

    cfa_array = data.dumpd()

    # Modify the dictionary so that it is suitable for JSON
    # serialization
    del cfa_array['_axes']
    del cfa_array['shape']
    del cfa_array['units']
    del cfa_array['dtype']
    cfa_array.pop('_cyclic', None)
    cfa_array.pop('_fill', None)
    cfa_array.pop('fill_value', None)

    pmshape = cfa_array.pop('_pmshape', None)
    if pmshape:
        cfa_array['pmshape'] = pmshape
        
    pmaxes = cfa_array.pop('_pmaxes', None)
    if pmaxes:
        cfa_array['pmdimensions'] = pmaxes
        
    config = data.partition_configuration(readonly=True)
 
    base = g['cfa_options'].get('base', None)
    if base is not None:
        cfa_array['base'] = base

    convert_dtype = g['datatype']

    for attrs in cfa_array['Partitions']:
        fmt = attrs.get('format', None)

        if fmt is None:
            # --------------------------------------------------------
            # This partition has an internal sub-array. This could be
            # a numpy array or a temporary FileArray object.
            # -------------------------------------------------------- 
            index = attrs.get('index', ())
            if len(index) == 1:
                index = index[0]
            else:
                index = tuple(index)

            partition = data.partitions.matrix.item(index)

            partition.open(config)
            array = partition.array

            # Convert data type
            new_dtype = convert_dtype.get(array.dtype, None)
            if new_dtype is not None:
                array = array.astype(new_dtype)  
                
            shape = array.shape        
            ncdim_strlen = []
            if array.dtype.kind == 'S':
                # This is an array of strings
                strlen = array.dtype.itemsize    
                if strlen > 1:
                    # Convert to an array of characters
                    array = _character_array(array)
                    # Get the netCDF dimension for the string length
                    ncdim_strlen = [_string_length_dimension(strlen, g=None)]
            #--- End: if

            # Create a name for the netCDF variable to contain the array
            p_ncvar = 'cfa_'+_random_hex_string()
            while p_ncvar in g['ncvar_names']:
                p_ncvar = 'cfa_'+_random_hex_string()
            #--- End: while
            g['ncvar_names'].add(p_ncvar)
          
            # Get the private CFA netCDF dimensions for the array.
            cfa_dimensions = [_cfa_dimension(n, g=g) for n in array.shape]
            
            # Create the private CFA variable and write the array to it
            v = g['netcdf'].createVariable(p_ncvar, _datatype(array, g=g),
                                           cfa_dimensions + ncdim_strlen,
                                           fill_value=fill_value,
                                           least_significant_digit=None,
                                           endian=g['endian'],
                                           **g['compression'])
            
            _write_attributes(v, {'cf_role': 'cfa_private'})

            v[...] = array

            # Update the attrs dictionary.
            #
            # Note that we don't need to set 'part', 'dtype', 'units',
            # 'calendar', 'dimensions' and 'reverse' since the
            # partition's in-memory data array always matches up with
            # the master data array.
            attrs['subarray'] = {'shape' : shape,
                                 'ncvar' : p_ncvar}

        else:
            # --------------------------------------------------------
            # This partition has an external sub-array
            # --------------------------------------------------------
            # PUNITS, PCALENDAR: Change from Units object to netCDF
            #                    string(s)
            units = attrs.pop('Units', None)
            if units is not None:
                attrs['punits'] = units.units
                if hasattr(units, 'calendar'):
                    attrs['pcalendar'] = units.calendar

            # PDIMENSIONS: 
            p_axes = attrs.pop('axes', None)
            if p_axes is not None:
                attrs['pdimensions'] = p_axes

            # REVERSE                
            p_flip = attrs.pop('flip', None)
            if p_flip:
                attrs['reverse'] = p_flip

            # DTYPE: Change from numpy.dtype object to netCDF string
            dtype = attrs['subarray'].pop('dtype', None)
            if dtype is not None:
                if dtype.kind != 'S':
                    attrs['subarray']['dtype'] = _convert_to_netCDF_datatype(dtype)

            # FORMAT: 
            sfmt = attrs.pop('format', None)
            if sfmt is not None:
                attrs['subarray']['format'] = sfmt
        #--- End: if
 
        # LOCATION: Change from python to CFA indexing (i.e. range
        #           includes the final index)
        attrs['location'] = [(x[0], x[1]-1) for x in attrs['location']]
        
        # PART: Change from python to to CFA indexing (i.e. slice
        #       range includes the final index)
        part = attrs.get('part', None)
        if part:
            p = []
            for x, size in zip(part, attrs['subarray']['shape']):
                if isinstance(x, slice):
                    x = x.indices(size)
                    if x[2] > 0:
                        p.append([x[0], x[1]-1, x[2]])
                    elif x[1] == -1:
                        p.append([x[0], 0, x[2]])
                    else:
                        p.append([x[0], x[1]+1, x[2]])
                else:
                    p.append(tuple(x))
            #--- End: for
            attrs['part'] = str(p)
        #--- End: if
                
        if 'base' in cfa_array and 'file' in attrs['subarray']:
            # Make the file name relative to base
            attrs['subarray']['file'] = relpath(attrs['subarray']['file'],
                                                cfa_array['base'])            
    #--- End: for

    # Add the description (as a JSON string) of the partition array to
    # the netcdf attributes.
    netcdf_attrs['cfa_array'] = json.dumps(cfa_array,
                                           default=_convert_to_builtin_type)

    # Write the netCDF attributes to the file
    _write_attributes(g['nc'][ncvar], netcdf_attrs)
#--- End: def

def _convert_to_netCDF_datatype(dtype):
    '''

Convert a numpy.dtype object to a netCDF data type string.

:Parameters:

    dtype : numpy.dtype

:Returns:

    out : str

:Examples:

>>> _convert_to_netCDF_datatype(numpy.dtype('float32'))
'float'
>>> _convert_to_netCDF_datatype(numpy.dtype('float64'))
'double'
>>> _convert_to_netCDF_datatype(numpy.dtype('int8'))
'byte'

'''    
    if dtype.char is 'f':
        return 'float'
    if dtype.char is 'd':
        return 'double'
    if dtype.kind is 'i':  # long int??
        return 'int'
    if dtype.char is 'S':
        return 'char'
    if dtype.char is 'b':
        return 'byte'
    if dtype.char is 'h':
        return 'short'

    raise TypeError("Ho hum de hum")
#--- End: def

def _convert_to_builtin_type(x):
    '''

Convert a non-JSON-encodable object to a JSON-encodable built-in type.

Possible conversions are:

==============  =============  ======================================
Input object    Output object  numpy data types covered
==============  =============  ======================================
numpy.bool_     bool           bool
numpy.integer   int            int, int8, int16, int32, int64, uint8,
                               uint16, uint32, uint64
numpy.floating  float          float, float16, float32, float64
==============  =============  ======================================

:Parameters:

    x : 
        
:Returns: 

    out :

:Raises:

    TypeError :
        If *x* can't be converted to a JSON serializableis type.

:Examples:

>>> type(_convert_to_netCDF_datatype(numpy.bool_(True)))
bool
>>> type(_convert_to_netCDF_datatype(numpy.array([1.0])[0]))
double
>>> type(_convert_to_netCDF_datatype(numpy.array([2])[0]))
int

''' 
    if isinstance(x, numpy_bool_):
        return bool(x)

    if isinstance(x, numpy_integer):
        return int(x)
     
    if isinstance(x, numpy_floating):
        return float(x)

    raise TypeError(
        "{0!r} object is not JSON serializable: {1!r}".format(type(x), x))
#--- End: def


def _grid_ncdimensions(f, key, axis_to_ncdim, g=None):
    '''

Return a tuple of the netCDF dimension names for the axes of a
coordinate or cell measures objects.

:Parameters:

    f : cf.Field

    key : str

    axis_to_ncdim : dict
        Mapping of field axis identifiers to netCDF dimension names.

    g : dict

:Returns:

    out : tuple
        A tuple of the netCDF dimension names.

'''
#    if f.item(key).ndim == 0:
#        return ()
#    else:
    return tuple([axis_to_ncdim[axis] for axis in f.item_axes(key)])
#--- End: def
    
def _variable_ncvar(variable, default, g=None):
    '''
    
:Returns:

    variable : cf.Variable or cf.CoordinateReference
       
    default : str

    g : dict

'''
    ncvar = getattr(variable, 'ncvar', variable.identity(default=default))    
    return _check_name(ncvar, g=g)        
#--- End: def

def _data_ncvar(data, ncvar, g=None):
    '''
    
:Returns:

    data : cf.Data
       
    default : str

#    counter : int

    g : dict

'''
    return _check_name(ncvar, None, g=g)        
#--- End: def

def _write_dimension(ncdim, f, axis, axis_to_ncdim, unlimited=False, g=None):
    '''Write a dimension to the netCDF file.

.. note:: This function updates ``axis_to_ncdim``, ``g['ncdim_to_size']``.

:Parameters:

    ncdim: `str`
        The netCDF dimension name.

    f: `cf.Field`
   
    axis: `str`
        The field's axis identifier.

    axis_to_ncdim: `dict`
        Mapping of field axis identifiers to netCDF dimension names.

    unlimited: `bool`, optional
        If true then create an unlimited dimension. By default
        dimensions are not unlimited.

    g: `dict`

:Returns:

    `None`

    '''          
    size = f.axis_size(axis)

    g['ncdim_to_size'][ncdim] = size
    axis_to_ncdim[axis] = ncdim

    if unlimited:
        # Create an unlimited dimension
        try:
            g['netcdf'].createDimension(ncdim, None)
        except RuntimeError as error:

            message = "Can't create unlimited dimension in {} file ({}).".format(
                g['netcdf'].file_format, error)

            error = str(error)
            if error == 'NetCDF: NC_UNLIMITED size already in use':
                raise NetCDFError(
message+" Only one unlimited dimension allowed. Consider using a netCDF4 format.")
                
            raise NetCDFError(message)
    else:
        try:
            g['netcdf'].createDimension(ncdim, size)
        except RuntimeError as error:
            raise NetCDFError(
"Can't create dimension of size {} in {} file ({})".format(
    size, g['netcdf'].file_format, error))
#--- End: def

def _change_reference_datetime(coord, g=None):
    '''

:Parameters:

    coord : cf.Coordinate

    g : dict

:Returns:

    out : cf.Coordinate

'''       
    if not coord.Units.isreftime:
        return coord

    reference_datetime = g['reference_datetime']
    if not reference_datetime:
        return coord

    coord2 = coord.copy()
    try:
        coord2.reference_datetime = reference_datetime
    except ValueError:
        raise ValueError(
"Can't override coordinate reference date-time {0!r} with {1!r}".format(
    coord.reference_datetime, reference_datetime))
    else:
        return coord2
#--- End: def

def _write_dimension_coordinate(f, axis, coord, key_to_ncvar, axis_to_ncdim,
                                g=None):
    '''

Write a dimension coordinate and bounds to the netCDF file.

This also writes a new netCDF dimension to the file and, if required,
a new netCDF bounds dimension.

.. note:: This function updates ``axis_to_ndim``, ``g['seen']``.

:Parameters:

    f : cf.Field
   
    axis : str

    coord : cf.DimensionCoordinate

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF dimension names.

    axis_to_ncdim : dict
        Mapping of field axis identifiers to netCDF dimension names.

    g : dict

:Returns:

    out : str
        The netCDF name of the dimension coordinate.

'''       
    seen = g['seen']

    coord = _change_reference_datetime(coord, g)

    create = False
    if not _seen(coord, g=g):
        create = True
    elif seen[id(coord)]['ncdims'] != ():
        if seen[id(coord)]['ncvar'] != seen[id(coord)]['ncdims'][0]:
            # Already seen this coordinate but it was an auxiliary
            # coordinate, so it needs to be created as a dimension
            # coordinate.
            create = True
    #--- End: if

    if create:
        ncdim = _variable_ncvar(coord, default='coordinate', g=g)

        # Create a new dimension, if it is not a scalar coordinate
        if coord.ndim > 0:
            unlimited = _unlimited(f, axis, g=g)
            _write_dimension(ncdim, f, axis, axis_to_ncdim,
                             unlimited=unlimited, g=g)

        ncdimensions = _grid_ncdimensions(f, axis, axis_to_ncdim, g=g)
        
        # If this dimension coordinate has bounds then create the
        # bounds netCDF variable and add the bounds or climatology
        # attribute to the dictionary of extra attributes
        extra = _write_coordinate_bounds(coord, ncdimensions, ncdim, g=g)

        # Create a new dimension coordinate variable
        _create_netcdf_variable(ncdim, ncdimensions, coord, 
                                extra=extra, g=g)
    else:
        ncdim = seen[id(coord)]['ncvar']

    key_to_ncvar[axis] = ncdim

#    try:    ### ????? why not always do this dch??
    axis_to_ncdim[axis] = ncdim
#    except KeyError:
#        pass

    return ncdim
#--- End: def

def _write_scalar_data(v, ncvar, g=None):
    '''Write a dimension coordinate and bounds to the netCDF file.

This also writes a new netCDF dimension to the file and, if required,
a new netCDF bounds dimension.

.. note:: This function updates ``g['seen']``.

:Parameters:

    data : cf.Data
   
    ncvar : str

    g : dict

:Returns:

    out : str
        The netCDF name of the scalar data variable

    '''       
    seen = g['seen']

    create = not _seen(data, ncdims=(), g=g)

    if create:
        ncvar = _data_ncvar(data, ncvar, g=g)
        
        # Create a new dimension coordinate variable
        _create_netcdf_variable(ncvar, (), data, g=g)

    else:
        ncvar = seen[id(data)]['ncvar']

    return ncvar
#--- End: def

def _seen(variable, ncdims=None, g=None):
    '''

Return True if a variable is logically equal any variable in the
g['seen'] dictionary.

If this is the case then the variable has already been written to the
output netCDF file and so we don't need to do it again.

If 'ncdims' is set then a extra condition for equality is applied,
namely that of 'ncdims' being equal to the netCDF dimensions (names
and order) to that of a variable in the g['seen'] dictionary.

When True is returned, the input variable is added to the g['seen']
dictionary.

.. note:: This function updates ``g['seen']``.

:Parameters:

    variable : 

    ncdims : tuple, optional

    g : dict

:Returns:

    out : bool
        True if the variable has already been written to the file,
        False otherwise.

'''
    seen = g['seen']

    for key, value in seen.iteritems():
        if ncdims is not None and ncdims != value['ncdims']:
            # The netCDF dimensions (names and order) of the input
            # variable are different to those of this variable in
            # the 'seen' dictionary
            continue

        # Still here?
        if variable.equals(value['variable']):
            seen[id(variable)] = {'variable': variable,
                                  'ncvar'   : value['ncvar'],
                                  'ncdims'  : value['ncdims']}
            return True
    #--- End: for

    return False
#--- End: def

def _write_coordinate_bounds(coord, coord_ncdimensions, coord_ncvar, g=None):
    '''

Create a coordinate's bounds netCDF variable, creating a new bounds
netCDF dimension if required. Return the bounds variable's netCDF
variable name.

.. note:: This function updates ``g['netcdf']``.

:Parameters:

    coord : cf.Coordinate

    coord_ncdimensions : tuple
        The ordered netCDF dimension names of the coordinate's
        dimensions (which do not include the bounds dimension).

    coord_ncvar : str
        The netCDF variable name of the coordinate.

     g : dict

:Returns:

    out : dict

:Examples:

>>> extra = _write_coordinate_bounds(c, ('dim2',), g=g)

'''

    if not (coord._hasbounds and coord.bounds._hasData):
        return {}

    extra = {}

    # Still here? Then this coordinate has a bounds attribute
    # which contains data.
    bounds = coord.bounds

    size = bounds.shape[-1]

    ncdim = _check_name('bounds{0}'.format(size), dimsize=size, g=g)

    # Check if this bounds variable has not been previously
    # created.
    ncdimensions = coord_ncdimensions +(ncdim,)        
    if _seen(bounds, ncdimensions, g=g):
        # This bounds variable has been previously created, so no
        # need to do so again.
        ncvar = g['seen'][id(bounds)]['ncvar']

    else:

        # This bounds variable has not been previously created, so
        # create it now.
        ncdim_to_size = g['ncdim_to_size']
        if ncdim not in ncdim_to_size:
            ncdim_to_size[ncdim] = size
            g['netcdf'].createDimension(ncdim, size) #ncdim_to_size[ncdim])
        #--- End: if
        
        ncvar = getattr(bounds, 'ncvar', coord_ncvar+'_bounds')
        
        ncvar = _check_name(ncvar, g=g)
        
        # Note that, in a field, bounds always have equal units to
        # their parent coordinate

        # Select properties to omit
        omit = []
        for prop in g['omit_bounds_properties']:
            if coord.hasprop(prop):
                omit.append(prop)

        # Create the bounds netCDF variable
        _create_netcdf_variable(ncvar, ncdimensions, bounds, omit=omit, g=g)
    #--- End: if

    if getattr(coord, 'climatology', None):
        extra['climatology'] = ncvar
    else:
        extra['bounds'] = ncvar

    g['bounds'][coord_ncvar] = ncvar
            
    return extra
#--- End: def
        
def _write_scalar_coordinate(f, axis, coord, coordinates,
                             key_to_ncvar, axis_to_ncscalar, g=None):
    '''Write a scalar coordinate and bounds to the netCDF file.

It is assumed that the input coordinate is has size 1, but this is not
checked.

If an equal scalar coordinate has already been written to the file
then the input coordinate is not written.

.. note:: This function updates ``key_to_ncvar``,
          ``axis_to_ncscalar``.

:Parameters:

    f : cf.Field
   
    axis : str
        The field's axis identifier for the scalar coordinate.

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF dimension names.

    axis_to_ncscalar : dict
        Mapping of field axis identifiers to netCDF scalar coordinate
        variable names.

    coordinates : list

    g : dict

:Returns:

    coordinates : list
        The updated list of netCDF auxiliary coordinate names.

    '''
    coord = _change_reference_datetime(coord, g)

    coord = coord.squeeze()

    if not _seen(coord, (), g=g):
        ncvar = _variable_ncvar(coord, default='scalar', g=g)

        # If this scalar coordinate has bounds then create the
        # bounds netCDF variable and add the bounds or climatology
        # attribute to the dictionary of extra attributes
        extra = _write_coordinate_bounds(coord, (), ncvar, g=g)

        # Create a new auxiliary coordinate variable
        _create_netcdf_variable(ncvar, (), coord, extra=extra, g=g)

    else:
        # This scalar coordinate has already been written to the
        # file
        ncvar = g['seen'][id(coord)]['ncvar']

    axis_to_ncscalar[axis] = ncvar

    key_to_ncvar[axis] = ncvar

    coordinates.append(ncvar)

    return coordinates
#--- End: def

def _write_auxiliary_coordinate(f, key, coord, coordinates,
                                key_to_ncvar, axis_to_ncdim, g=None):
    '''

Write an auxiliary coordinate and its bounds to the netCDF file.

If an equal auxiliary coordinate has already been written to the file
then the input coordinate is not written.

:Parameters:

    f : cf.Field
   
    key : str

    coord : cf.Coordinate

    coordinates : list

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF dimension names.

    axis_to_ncdim : dict
        Mapping of field axis identifiers to netCDF dimension names.

    g : dict

:Returns:

    coordinates : list
        The list of netCDF auxiliary coordinate names updated in
        place.

:Examples:

>>> coordinates = _write_auxiliary_coordinate(f, 'aux2', coordinates, g=g)

'''
    coord = _change_reference_datetime(coord, g)

    ncdimensions = _grid_ncdimensions(f, key, axis_to_ncdim, g=g)

    if _seen(coord, ncdimensions, g=g):
        ncvar = g['seen'][id(coord)]['ncvar']
    
    else:
        ncvar = _variable_ncvar(coord, default='auxiliary', g=g)
        
        # If this auxiliary coordinate has bounds then create the
        # bounds netCDF variable and add the bounds or climatology
        # attribute to the dictionary of extra attributes
        extra = _write_coordinate_bounds(coord, ncdimensions, ncvar, g=g)

        # Create a new auxiliary coordinate variable
        _create_netcdf_variable(ncvar, ncdimensions, coord, extra=extra, g=g)
    #--- End: if

    key_to_ncvar[key] = ncvar

    coordinates.append(ncvar)

    return coordinates
#--- End: def
  
def _write_domain_ancillary(f, key, anc, key_to_ncvar, axis_to_ncdim,
                            g=None):
    '''

Write a domain ancillary and its bounds to the netCDF file.

If an equal domain ancillary has already been written to the file then
it is not re-written.

:Parameters:

    f : cf.Field
   
    key : str

    anc : cf.DomainAncillary

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF variables.

    axis_to_ncdim : dict
        Mapping of field axis identifiers to netCDF dimensions.

    g : dict

:Returns:

    out : str
        The ncvar.

:Examples:

>>> _write_domain_ancillary(f, 'cct2', anc, g=g)

'''
#    print f.items(key)
#   print 'axis_to_ncdim=',axis_to_ncdim
#   print 'f.item_axes('+key+')=', f.item_axes(key)
    ncdimensions = tuple([axis_to_ncdim[axis] for axis in f.item_axes(key)])

    create = not _seen(anc, ncdimensions, g=g)

    if not create:
        ncvar = g['seen'][id(anc)]['ncvar']
    
    else:
        ncvar = _variable_ncvar(anc, default='domain_ancillary', g=g)

        # If this domain ancillary has bounds then create the bounds
        # netCDF variable and add the bounds or climatology attribute
        # to the dictionary of extra attributes
        extra = _write_coordinate_bounds(anc, ncdimensions, ncvar, g=g)

        _create_netcdf_variable(ncvar, ncdimensions, anc, extra=extra, g=g)
    #--- End: if

    key_to_ncvar[key] = ncvar

    return ncvar
#--- End: def
  
def _write_field_ancillary(f, key, anc, key_to_ncvar, axis_to_ncdim,
                           g=None):
    '''Write a field ancillary to the netCDF file.

If an equal field ancillary has already been written to the file then
it is not re-written.

:Parameters:

    f : cf.Field
   
    key : str

    anc : cf.FieldAncillary

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF variables

    axis_to_ncdim : dict
        Mapping of field axis identifiers to netCDF dimensions.

    g : dict

:Returns:

    out : str
        The ncvar.

:Examples:

>>> ncvar = _write_field_ancillary(f, 'fav2', anc, key_to_ncvar, axis_to_ncdim, g=g)

    '''
    ncdimensions = tuple([axis_to_ncdim[axis] for axis in f.item_axes(key)])

    create = not _seen(anc, ncdimensions, g=g)

    if not create:
        ncvar = g['seen'][id(anc)]['ncvar']    
    else:
        ncvar = _variable_ncvar(anc, 'ancillary_data', g=g)
        _create_netcdf_variable(ncvar, ncdimensions, anc, g=g)

    key_to_ncvar[key] = ncvar

    return ncvar
#--- End: def
  
def _write_cell_measure(f, key, msr, key_to_ncvar, axis_to_ncdim,
                        g=None):
    '''

Write an auxiliary coordinate and bounds to the netCDF file.

If an equal cell measure has already been written to the file then the
input coordinate is not written.

:Parameters:

    f : cf.Field
        The field containing the cell measure.

    key : str
        The identifier of the cell measure (e.g. 'msr0').

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF dimension names.

    axis_to_ncdim : dict
        Mapping of field axis identifiers to netCDF dimension names.

    g : dict

:Returns:

    out : str
        The 'measure: ncvar'.

:Examples:

'''
    ncdimensions = _grid_ncdimensions(f, key, axis_to_ncdim, g=g)

    create = not _seen(msr, ncdimensions, g=g)

    if not create:
        ncvar = g['seen'][id(msr)]['ncvar']
    else:
        if not hasattr(msr, 'measure'):
            raise ValueError(
"Can't create a cell measure variable without a 'measure' attribute")

        ncvar = _variable_ncvar(msr, 'cell_measure', g=g)

        _create_netcdf_variable(ncvar, ncdimensions, msr, g=g)
    #--- End: if
            
    key_to_ncvar[key] = ncvar

    # Update the cell_measures list
    return '{0}: {1}'.format(msr.measure, ncvar)
#--- End: def
  

def _write_grid_mapping(f, ref, multiple_grid_mappings, key_to_ncvar,
                        g=None):
    '''

Write a grid mapping georeference to the netCDF file.

.. note:: This function updates ``grid_mapping``, ``g['seen']``.

:Parameters:

    f : cf.Field

    ref : cf.CoordinateReference
        The grid mapping coordinate reference to write to the file.

    multiple_grid_mappings : bool

    key_to_ncvar : dict
        Mapping of field item identifiers to netCDF variable names.

    g : dict

:Returns:

    out : str

:Examples:

'''
    if _seen(ref, g=g):
        # Use existing grid_mapping
        ncvar = g['seen'][id(ref)]['ncvar']

    else:
        # Create a new grid mapping
        ncvar = _variable_ncvar(ref, 'grid_mapping', g=g)

        g['nc'][ncvar] = g['netcdf'].createVariable(ncvar, 'S1', (),
                                                    endian=g['endian'],
                                                    **g['compression'])

        cref = ref.canonical(f)

        # Add properties from key/value pairs
        if hasattr(g['nc'][ncvar], 'setncatts'):
            # Use the faster setncatts
            for term, value in cref.parameters.iteritems():
                if value is None:
                    del cref[term]
                elif numpy_size(value) == 1:
                    cref[term] = numpy_array(value, copy=False).item()
                else:
                    cref[term] = numpy_array(value, copy=False).tolist()
            #--- End: for
            g['nc'][ncvar].setncatts(cref.parameters)
        else:
            # Otherwise use the slower setncattr
            pass #  I don't want to support this any more.
        
        # Update the 'seen' dictionary
        g['seen'][id(ref)] = {'variable': ref, 
                              'ncvar'   : ncvar,
                              'ncdims'  : (), # Grid mappings have no netCDF dimensions
                          }
    #--- End: if

    # Update the grid_mapping list in place
    if multiple_grid_mappings:
        return ncvar+':'+' '.join(sorted([key_to_ncvar[key] for key in ref.coordinates]))
    else:
        return ncvar
#--- End: def

def _create_netcdf_variable(ncvar, dimensions, cfvar, omit=(),
                            extra={}, data_variable=False, g=None):
    '''Create a netCDF variable from *cfvar* with name *ncvar* and dimensions
*ncdimensions*. The new netCDF variable's properties are given by
cfvar.properties(), less any given by the *omit* argument. If a new
string-length netCDF dimension is required then it will also be
created. The ``seen`` dictionary is updated for *cfvar*.

.. note:: This function updates ``g['ncdim_to_size']``,
          ``g['netcdf']``, ``g['nc']``, ``g['seen']``.

:Parameters:

    ncvar: `str`
        The netCDF name of the variable.

    dimensions: `tuple`
        The netCDF dimension names of the variable

    cfvar: `cf.Variable`
        The coordinate, cell measure or field object to write to the
        file.

    omit: sequence of `str`, optional

    extra: `dict`, optional

    g: `dict`

:Returns:

    `None`

    '''
    _debug = g['_debug']
    
    if g['verbose']:
        print repr(cfvar)+' netCDF: '+ncvar

    if _debug:
        print '        '+repr(cfvar)+' netCDF: '+ncvar
        
    # ----------------------------------------------------------------
    # Set the netCDF4.createVariable datatype
    # ----------------------------------------------------------------
    datatype = _datatype(cfvar, g=g)

    # ----------------------------------------------------------------
    # Set the netCDF4.createVariable dimensions
    # ----------------------------------------------------------------
    ncdimensions = dimensions
    
    if not cfvar._hasData:
        data = None
    else:
        data = cfvar.Data            
        config = data.partition_configuration(readonly=True)

        if datatype == 'S1':
            # --------------------------------------------------------
            # Convert a string data type numpy array into a character
            # data type ('S1') numpy array with an extra trailing
            # dimension.
            # --------------------------------------------------------
            strlen = data.dtype.itemsize
            if strlen > 1:
                ncdim = _string_length_dimension(strlen, g=g)
                    
                ncdimensions = dimensions + (ncdim,)

                data = data.copy()

                new_axis = data._new_axis_identifier()

                for partition in data.partitions.flat:
                    partition.open(config)
                    array = partition.array
                    
                    # Convert the partition's string array into a
                    # character array. Note that it is very important
                    # to not change the mutable attributes of the
                    # partition object in-place.
                    if partition.part:
                        partition.part = partition.part + [slice(None)]

                    partition.axes     = partition.axes + [new_axis]
                    partition.shape    = partition.shape + [strlen]
                    partition.location = partition.location + [(0, strlen)]

                    partition.subarray    = _character_array(array)

                    partition.close()
                #--- End: for

                data._axes = data._axes + [new_axis]
                data._shape += (strlen,)
                data._ndim += 1
                data.dtype = datatype

                config['axes'] = data._axes
#                pda_args['keep_in_memory'] = True
    #--- End: if

    # Find the fill value (note that this is set in the call to
    # netCDF4.createVariable, rather than with setncattr).
    fill_value = cfvar.fill_value()

    # Add simple properties (and units and calendar) to the netCDF
    # variable
    netcdf_attrs = cfvar.properties()
    for attr in ('units', 'calendar'):
        value = getattr(cfvar, attr, None)
        if value is not None:
            netcdf_attrs[attr] = value
    #--- End: for

    netcdf_attrs.update(extra)
    netcdf_attrs.pop('_FillValue', None)

    for attr in omit:
        netcdf_attrs.pop(attr, None) 

    is1d_coord = (isinstance(cfvar, Coordinate) and cfvar.ndim <= 1 or
                  isinstance(cfvar, Bounds)     and cfvar.ndim <= 2)

    if not g['cfa'] or data.in_memory or is1d_coord:
        #---------------------------------------------------------
        # Write a normal netCDF variable 
        #---------------------------------------------------------

        # ------------------------------------------------------------
        # Create a new netCDF variable and set the _FillValue
        # ------------------------------------------------------------ 
        if data_variable:
            lsd = g['least_significant_digit']
        else:
            lsd = None

        # Set HDF chunk sizes
        chunksizes = [size for i, size in sorted(cfvar.HDF_chunks().items())]
        if chunksizes == [None] * cfvar.ndim:
            chunksizes = None

        try:
            g['nc'][ncvar] = g['netcdf'].createVariable(
                ncvar,
                datatype, 
                ncdimensions,
                fill_value=fill_value,
                least_significant_digit=lsd,
                endian=g['endian'],
                chunksizes=chunksizes,
                **g['compression'])
#        except (TypeError, RuntimeError):
        except RuntimeError as error:
            error = str(error)
            if error == 'NetCDF: Not a valid data type or _FillValue type mismatch':
                raise ValueError(
"Can't write {} data from {!r} to a {} file. Consider using a netCDF4 format or use the 'single' or 'datatype' parameters or change the datatype before writing.".format(
    cfvar.dtype.name, cfvar, g['netcdf'].file_format))
            
            message = "Can't create variable in {} file from {} ({})".format(g['netcdf'].file_format, cfvar, error)

            if error == 'NetCDF: NC_UNLIMITED in the wrong index':            
                raise NetCDFError(
message+". Unlimited dimension must be the first (leftmost) dimension of the variable. Consider using a netCDF4 format.")
                
            raise NetCDFError(message)
        #--- End: try

        _write_attributes(g['nc'][ncvar], netcdf_attrs)

        #-------------------------------------------------------------
        # Add data to the netCDF variable
        #
        # Note that we don't need to worry about scale_factor and
        # add_offset, since if a partition's data array is *not* a
        # numpy array, then it will have its own scale_factor and
        # add_offset parameters which will be applied when the array
        # is realised, and the python netCDF4 package will deal with
        # the case when scale_factor or add_offset are set as
        # properties on the variable.
        # -------------------------------------------------------------
        if data is not None:  

            # Find the missing data values, if any.
            if not fill_value:
                missing_data = None
            else:
                _FillValue    = getattr(cfvar, '_FillValue', None) 
                missing_value = getattr(cfvar, 'missing_value', None)
                missing_data = [value for value in (_FillValue, missing_value)
                                if value is not None]
            #--- End: if

#            pda_args['revert_to_file'] = True
            
#            if data._isdt:
#                # Convert date-time objects to numeric reference times
#                pda_args['func']   = dt2rt
#                # Turn off data type checking and partition updating
#                pda_args['dtype']  = None
#                pda_args['update'] = False
#            #--- End: if
            
            convert_dtype = g['datatype']

#dch            if data.fits_in_one_chunk_in_memory(data.dtype.itemsize):
#dch                data.varray

            if _debug:
                print "        g['nc']['"+ncvar+"'].shape =", g['nc'][ncvar].shape

            for partition in data.partitions.flat:
                partition.open(config)
                array = partition.array

                # Convert data type
                new_dtype = convert_dtype.get(array.dtype, None)
                if new_dtype is not None:
                    array = array.astype(new_dtype)  

                # Check that the array doesn't contain any elements
                # which are equal to any of the missing data values
                if missing_data:
                    if partition.masked:
                        temp_array = array.compressed()
                    else:
                        temp_array = array

                    if numpy_intersect1d(missing_data, temp_array):
                        raise ValueError(
"ERROR: Can't write field when array has _FillValue or missing_value at unmasked point: {!r}".format(cfvar))
                #--- End: if

                if _debug:
                    print '            partition.indices =', partition.indices
                    print '            array.shape       =', array.shape
                    print '            array.max()       =', array.max()

                # Copy the array into the netCDF variable
                g['nc'][ncvar][partition.indices] = array        

                partition.close()
            #--- End: for                  
        #--- End: if

        # Update the 'seen' dictionary
        g['seen'][id(cfvar)] = {'variable': cfvar,
                                'ncvar'   : ncvar,
                                'ncdims'  : dimensions}

        return

    elif data is not None:
        #---------------------------------------------------------
        # Write a CFA variable 
        #---------------------------------------------------------
        _write_cfa_variable(ncvar, ncdimensions, netcdf_attrs, data, g=g)

        return
#--- End: def
 
def _write_a_field(f, add_to_seen=False, allow_data_expand_dims=True,
                   remove_crap_axes=False, g=None):
    '''

:Parameters:

    f : cf.Field

    add_to_seen : bool, optional

    allow_data_expand_dims : bool, optional

    g : dict

:Returns:

    None

'''
    if g['_debug']:
        print '    Field:', repr(f)

    seen = g['seen']
      
    if add_to_seen:
        id_f = id(f)
        org_f = f
        
    f = f.copy()

    data_axes = f.data_axes()

    # Mapping of field axis identifiers to netCDF dimension names
    axis_to_ncdim = {}

    # Mapping of field axis identifiers to netCDF scalar coordinate
    # variable names
    axis_to_ncscalar = {}

    # Mapping of field item identifiers to netCDF variable names
    key_to_ncvar = {}

    # Initialize the list of the field's auxiliary coordinates
    coordinates = []

    # For each of the field's axes ...
    for axis in sorted(f.axes()):
        dim_coord = f.dim(axis)

        if dim_coord is not None:
            # --------------------------------------------------------
            # A dimension coordinate exists for this axis
            # --------------------------------------------------------
            if axis in data_axes:
                # The data array spans this axis, so write the
                # dimension coordinate to the file as a netCDF 1-d
                # coordinate variable.
                ncdim = _write_dimension_coordinate(f, axis, dim_coord,
                                                    key_to_ncvar, axis_to_ncdim,
                                                    g=g)
            else:
                # The data array does not span this axis (and
                # therefore it must have size 1).
                if f.items(role=('a', 'm', 'c', 'f'), axes=axis):
                    # There ARE auxiliary coordinates, cell measures,
                    # domain ancillaries or field ancillaries which
                    # span this axis, so write the dimension
                    # coordinate to the file as a netCDF 1-d
                    # coordinate variable.
                    ncdim = _write_dimension_coordinate(f, axis, dim_coord,
                                                        key_to_ncvar,
                                                        axis_to_ncdim, g=g)

                    # Expand the field's data array to include this
                    # axis
                    f.expand_dims(0, axes=axis, i=True) 
                else:
                    # There are NO auxiliary coordinates, cell
                    # measures, domain ancillaries or field
                    # ancillaries which span this axis, so write the
                    # dimension coordinate to the file as a netCDF
                    # scalar coordinate variable.
                    coordinates = _write_scalar_coordinate(f, axis, dim_coord,
                                                           coordinates,
                                                           key_to_ncvar,
                                                           axis_to_ncscalar,
                                                           g=g)
                    
            #--- End: if
        else:
            # --------------------------------------------------------
            # There is no dimension coordinate for this axis
            # --------------------------------------------------------
            if axis not in data_axes and f.items(role=('a', 'm', 'c', 'f'), axes=axis):
                # The data array doesn't span the axis but an
                # auxiliary coordinate, cell measure, domain ancillary
                # or field ancillary does, so expand the data array to
                # include it.
                f.expand_dims(0, axes=axis, i=True)
                data_axes.append(axis)
            #--- End: if

            # If the data array (now) spans this axis then create a
            # netCDF dimension for it
            if axis in data_axes:
                ncdim = getattr(f, 'ncdimensions', {}).get(axis, 'dim')
                ncdim = _check_name(ncdim, g=g)

                unlimited = _unlimited(f, axis, g=g)
                _write_dimension(ncdim, f, axis, axis_to_ncdim,
                                 unlimited=unlimited, g=g)
             #--- End: if
        #--- End: if

    #--- End: for

    # ----------------------------------------------------------------
    # Create auxiliary coordinate variables, except those which might
    # be completely specified elsewhere by a transformation.
    # ----------------------------------------------------------------
    # Initialize the list of 'coordinates' attribute variable values
    # (each of the form 'name')
    for key, aux_coord in sorted(f.auxs().items()):
        coordinates = _write_auxiliary_coordinate(f, key, aux_coord,
                                                  coordinates, key_to_ncvar,
                                                  axis_to_ncdim, g=g)
    #--- End: for

    # ----------------------------------------------------------------
    # Create domain ancillaries
    # ----------------------------------------------------------------
    for key, anc in sorted(f.domain_ancs().iteritems()):
        _write_domain_ancillary(f, key, anc, key_to_ncvar,
                                axis_to_ncdim, g=g)

    # ----------------------------------------------------------------
    # Create cell measures variables
    # ----------------------------------------------------------------
    # Set the list of 'cell_measures' attribute values (each of
    # the form 'measure: name')
    cell_measures = [_write_cell_measure(f, key, msr, key_to_ncvar,
                                         axis_to_ncdim, g=g)
                     for key, msr in f.measures().iteritems()]

    # ----------------------------------------------------------------
    # Grid mappings
    # ----------------------------------------------------------------
    grid_mapping_refs = f.refs('type%grid_mapping').values()
    multiple_grid_mappings = len(grid_mapping_refs) > 1

    grid_mapping = [_write_grid_mapping(f, ref, multiple_grid_mappings,
                                        key_to_ncvar, g=g)
                    for ref in grid_mapping_refs]
    
    if multiple_grid_mappings:        
        grid_mapping2 = []
        for x in grid_mapping:
            name, a = x.split(':')
            a = a.split()
            for y in grid_mapping:
                if y == x:
                    continue
                b = y.split(':')[1].split()

                if len(a) > len(b) and set(b).issubset(a):
                    a = [q for q in a if q not in b]
            #--- End: for
            grid_mapping2.apend(name+':'+' '.join(a))
        #--- End: for
        grid_mapping = grid_mapping2
    #--- End: if

    # ----------------------------------------------------------------
    # formula_terms
    # ----------------------------------------------------------------
    for ref in f.refs('type%formula_terms').values():
        formula_terms = []
        bounds_formula_terms = []
    
        formula_terms_name = ref.name()
        if formula_terms_name is None:
            owning_coord = None
        else:
            owning_coord = f.coord(formula_terms_name, exact=True)

        z_axis = f.item_axes(formula_terms_name, role=('d', 'a'), exact=True)[0]
                
        if owning_coord is not None:
            # This formula_terms coordinate reference matches up with
            # an existing coordinate

            for term, value in ref.parameters.iteritems():
                if value is None:
                    continue

                if term == 'standard_name':
                    continue

                value = Data.asdata(value)
                ncvar = _write_scalar_data(value, ncvar=term, g=g)

                formula_terms.append('{0}: {1}'.format(term, ncvar))
            #--- End: for
        
            for term, value in ref.ancillaries.iteritems():
                if value is None:
                    continue

                domain_anc = f.domain_anc(value)
                if domain_anc is None:
                    continue

                if id(domain_anc) not in g['seen']:
                    continue

                # Get the netCDF variable name for the domain
                # ancillary and add it to the formula_terms attribute
                ncvar = g['seen'][id(domain_anc)]['ncvar']
                formula_terms.append('{0}: {1}'.format(term, ncvar))

                bounds = g['bounds'].get(ncvar, None)
                if bounds is not None:
                    if z_axis not in f.item_axes(value, role='c'):
                        bounds = None
    
                if bounds is None:        
                    bounds_formula_terms.append('{0}: {1}'.format(term, ncvar))
                else:
                    bounds_formula_terms.append('{0}: {1}'.format(term, bounds))
        #--- End: if

        # Add the formula_terms attribute to the output
        # variable
        if formula_terms:
            ncvar = seen[id(owning_coord)]['ncvar']
            g['nc'][ncvar].setncattr('formula_terms',
                                     ' '.join(formula_terms))
            if g['_debug']:
                print '  formula_terms =', formula_terms
    
            # Add the formula_terms attribute to the coordinate bounds
            # variable
            bounds = g['bounds'].get(ncvar)
            if bounds is not None:
                bounds_formula_terms = ' '.join(bounds_formula_terms)
                g['nc'][bounds].setncattr('formula_terms', bounds_formula_terms)
                if g['_debug']:
                    print '  Bounds formula_terms =', bounds_formula_terms
    #--- End: for

    # ----------------------------------------------------------------
    # Field ancillary variables
    # ----------------------------------------------------------------
    # Create the 'ancillary_variables' CF-netCDF attribute and create
    # the referenced CF-netCDF ancillary variables
    ancillary_variables = [_write_field_ancillary(f, key, anc, key_to_ncvar,
                                                  axis_to_ncdim, g=g)
                           for key, anc in f.field_ancs().iteritems()]

    # ----------------------------------------------------------------
    # Create the CF-netCDF data variable
    # ----------------------------------------------------------------
    ncvar = _variable_ncvar(f, 'data', g=g)

#    ncvar = getattr(f, 'ncvar', f.identity(default='data'))a
#    ncvar, g['dataN'] = _check_name(ncvar, g['dataN'], g=g)

#    axis_to_ncdim    = g['axis_to_ncdim']
#    axis_to_ncscalar = g['axis_to_ncscalar']

    ncdimensions = tuple([axis_to_ncdim[axis] for axis in f.data_axes()])

    extra = {}

    # Cell measures
    if cell_measures:
        extra['cell_measures'] = ' '.join(cell_measures)           

    # Auxiliary/scalar coordinates
    if coordinates:
        extra['coordinates'] = ' '.join(coordinates)

    # Grid mapping
    if grid_mapping: 
        extra['grid_mapping'] = ' '.join(grid_mapping)

    # Ancillary variables
    if ancillary_variables:
        extra['ancillary_variables'] = ' '.join(ancillary_variables)
        
    # Flag values
    if hasattr(f, 'flag_values'):
        extra['flag_values'] = f.flag_values

    # Flag masks
    if hasattr(f, 'flag_masks'):
        extra['flag_masks'] = f.flag_masks

    # Flag meanings
    if hasattr(f, 'flag_meanings'):
        extra['flag_meanings'] = ' '.join(f.flag_meanings)

    # name can be a dimension of the variable, a scalar coordinate
    # variable, a valid standard name, or the word 'area'
    cell_methods = f.CellMethods
    if cell_methods:
        axis_map = axis_to_ncdim.copy()
        axis_map.update(axis_to_ncscalar)
        extra['cell_methods'] = cell_methods.write(axis_map)

    # Create a new data variable
    _create_netcdf_variable(ncvar, ncdimensions, f,
                            omit=g['global_properties'],
                            extra=extra,
                            data_variable=True,
                            g=g)
    
    # Update the 'seen' dictionary, if required
    if add_to_seen:
        g['seen'][id_f] = {'variable': org_f,
                           'ncvar'   : ncvar,
                           'ncdims'  : ncdimensions}
#--- End: def

def _unlimited(f, axis, g=None):
    '''
'''
    unlimited = f.unlimited().get(axis)

    if unlimited is None:
        unlimited = False
        for u in g['unlimited']:
            if f.axis(u, key=True) == axis:
                unlimited = True
                break
    
    return unlimited
#--- End: def

def _create_global_properties(fields, g=None):
    '''

Find the netCDF global properties from all of the input fields and
write them to the netCDF4.Dataset.

.. note:: This function updates ``g['global_properties']``.

:Parameters:

    fields : cf.FieldList

    g : dict

:Returns:

    None

'''
    # Data variable properties, as defined in Appendix A, without
    # those which are not simple.
    data_properties = set(('add_offset',
                           'cell_methods',
                           '_FillValue',
                           'flag_masks',
                           'flag_meanings',
                           'flag_values',
                           'long_name',
                           'missing_value',
                           'scale_factor',
                           'standard_error_multiplier',
                           'standard_name',
                           'units',
                           'valid_max',
                           'valid_min',
                           'valid_range',
                           ))

    # Global properties, as defined in Appendix A
    global_properties = set(('comment',
                             'Conventions',
                             'featureType',
                             'history',
                             'institution',
                             'references',
                             'source',
                             'title',
                             ))

    # Put all non-standard CF properties (i.e. those not in the
    # data_properties set) into the global_properties set, but
    # omitting those which have been requested to be on variables.
    for f in fields:
        for attr in set(f._simple_properties()) - global_properties - g['variable_attributes']:
            if attr not in data_properties:
                global_properties.add(attr)
    #--- End: for

    # Remove properties from the new global_properties set which
    # have different values in different fields
    f0 = fields[0]
    for prop in tuple(global_properties):
        if not f0.hasprop(prop):
            global_properties.remove(prop)
            continue
            
        prop0 = f0.getprop(prop)

        if len(fields) > 1:
            for f in fields[1:]:
                if (not f.hasprop(prop) or 
                    not equals(f.getprop(prop), prop0, traceback=False)):
                    global_properties.remove(prop)
                    break
    #--- End: for

    # Write the global properties to the file
    Conventions = __Conventions__
    if g['cfa']:
        Conventions += ' CFA'

    g['netcdf'].setncattr('Conventions', Conventions)
    
    for attr in global_properties - set(('Conventions',)):
        g['netcdf'].setncattr(attr, f0.getprop(attr)) 

    g['global_properties'] = global_properties
#--- End: def
