import re
#
from operator  import mul
from json      import loads as json_loads
from ast       import literal_eval as ast_literal_eval
from struct    import unpack as struct_unpack
from itertools import izip

from netCDF4  import Dataset as netCDF4_Dataset

from numpy import dtype       as numpy_dtype
from numpy import result_type as numpy_result_type
from numpy import unique      as numpy_unique
from numpy import where       as numpy_where

from ..boundedvariable     import Bounds
from ..coordinate          import DimensionCoordinate, AuxiliaryCoordinate
from ..cellmeasure         import CellMeasure
from ..cellmethods         import CellMethods
from ..coordinatereference import CoordinateReference
from ..domainancillary     import DomainAncillary
from ..domainaxis          import DomainAxis
from ..field               import Field, FieldList
from ..fieldancillary      import FieldAncillary
from ..functions           import abspath, dirname, pathjoin
from ..variable            import Variable
from ..units               import Units

from ..data.data      import Data
from ..data.filearray import CompressedArray, FilledArray

from .functions import _open_netcdf_file
from .filearray import NetCDFFileArray

_compression_type = {'gathered'              : 'gathered',
                     'DSG_indexed'           : 'DSG_indexed',
                     'DSG_contiguous'        : 'DSG_contiguous',
                     'DSG_indexed_contiguous': 'DSG_indexed_contiguous'}

def read(filename, fmt=None, field=(), verbose=False, chunk=True,
         _debug=False):
    '''Read fields from an input netCDF file on disk or from an OPeNDAP
server location.

The file may be big or little endian.

NetCDF dimension names are stored in the `ncdim` attributes of the
field's DomainAxis objects and netCDF variable names are stored in the
`ncvar` attributes of the field and its components (coordinates,
coordinate bounds, cell measures and coordinate references, domain
ancillaries, field ancillaries).

:Parameters:

    filename: `str` or `file`
        A string giving the file name or OPenDAP URL, or an open file
        object, from which to read fields. Note that if a file object
        is given it will be closed and reopened.

    fmt: `str`, optional
        Only read the file if it is the given format. Valid formats
        are ``'NETCDF'`` for a CF-netCDF file and ``'CFA'`` for
        CFA-netCDF file. By default a file of any of these formats is
        read.

    field: sequence of `str`, optional
        Create independent fields from field components. The *field*
        parameter may be one, or a sequence, of:

          ======================  ====================================
          *field*                 Field components
          ======================  ====================================
          ``'field_ancillary'``   Field ancillary objects
          ``'domain_ancillary'``  Domain ancillary objects
          ``'dimension'``         Dimension coordinate objects
          ``'auxiliary'``         Auxiliary coordinate objects
          ``'measure'``           Cell measure objects
          ``'all'``               All of the above
          ======================  ====================================

            *Example:*
              To create fields from auxiliary coordinate objects:
              ``field=['auxiliary']``.

            *Example:*
              To create fields from domain ancillary and cell measure
              objects: ``field=['domain_ancillary', 'measure']``.

        .. versionadded:: 1.0.4

    verbose: `bool`, optional
        If True then print information to stdout.
    
:Returns:

    out: `cf.FieldList`
        The fields in the file.

:Examples:

>>> f = cf.netcdf.read('file.nc')
>>> type(f)
<class 'cf.field.FieldList'>
>>> f
[<CF Field: pmsl(30, 24)>,
 <CF Field: z-squared(17, 30, 24)>,
 <CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

>>> cf.netcdf.read('file.nc')[0:2]
[<CF Field: pmsl(30, 24)>,
 <CF Field: z-squared(17, 30, 24)>]

>>> cf.netcdf.read('file.nc', units='K')
[<CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

>>> cf.netcdf.read('file.nc')[0]
<CF Field: pmsl(30, 24)>

    '''
    if isinstance(filename, file):
        name = filename.name
        filename.close()
        filename = name
    #--- End: if

    g = {'compression'   : {},
         'new_dimensions': {},
         'promoted'      : [],
         'cfa'           : False,
         'chunk'         : chunk,
         '_debug'        : _debug,
         'formula_terms' : {},
    }
    
    compression = {}
    
    # ----------------------------------------------------------------
    # Parse field
    # ----------------------------------------------------------------
    try:
        iter(field)
    except TypeError:
        raise ValueError(
            "Can't read: Bad parameter value: field={!r}".format(field))
           
    if 'all' in field:
        field = set(('domain_ancillary', 'field_ancillary', 'dimension_coordinate',
                     'auxiliary_coordinate', 'cell_measure'))


    filename = abspath(filename)

    g['field']    = field
    g['filename'] = filename
    
    # Read the netCDF file 
    nc = _open_netcdf_file(filename, 'r')
    g['nc'] = nc

    if _debug:
        print 'Input netCDF dataset =',nc

    # Set of all of the netCDF variable names in the file.
    #
    # For example:
    # >>> variables
    # set(['lon','lat','tas'])
    variables = set(map(str, nc.variables))
    if _debug:
        print 'variables =', variables

    # ----------------------------------------------------------------
    # Put the file's global attributes into the global
    # 'global_attributes' dictionary
    # ----------------------------------------------------------------
    global_attributes = {}
    for attr in map(str, nc.ncattrs()):
        try:
            value = nc.getncattr(attr)
            if isinstance(value, basestring):
                try:
                    global_attributes[attr] = str(value)
                except UnicodeEncodeError:
                    global_attributes[attr] = value.encode(errors='ignore')          
            else:
                global_attributes[attr] = value     
        except UnicodeDecodeError:
            pass
    #--- End: for
    g['global_attributes'] = global_attributes
    if _debug:
        print 'global_attributes =', g['global_attributes']
        
    # Find out if this is a CFA file
    cfa = 'CFA' in global_attributes.get('Conventions', ())
    g['cfa'] = cfa

    if (fmt and 
        (not cfa and fmt == 'CFA') or (cfa and fmt == 'NETCDF')):
        # Return an empty field list
        return FieldList()

    # ----------------------------------------------------------------
    # Create a dictionary keyed by nc variable names where each key's
    # value is a dictionary of that variable's nc
    # attributes. E.g. attributes['tas']['units']='K'
    # ----------------------------------------------------------------
    attributes = {}
    for ncvar in variables:
        attributes[ncvar] = {}
        for attr in map(str, nc.variables[ncvar].ncattrs()):
            try:
                attributes[ncvar][attr] = nc.variables[ncvar].getncattr(attr)
                if isinstance(attributes[ncvar][attr], basestring):
                    try:
                        attributes[ncvar][attr] = str(attributes[ncvar][attr])
                    except UnicodeEncodeError:
                        attributes[ncvar][attr] = attributes[ncvar][attr].encode(errors='ignore')
            except UnicodeDecodeError:
                pass
        #--- End: for  

        # Check for bad units
        try:
            Units(attributes[ncvar].get('units', None), 
                  attributes[ncvar].get('calendar', None))
        except (ValueError, TypeError):
            # Units in file have been set to unknown units so 1) give
            # a warning, 2) set the 'nonCF_units' property to the bad
            # units and 3) remove the offending units.
            attributes[ncvar]['nonCF_Units'] = \
                attributes[ncvar].pop('units', '')
#            attributes[ncvar]['nonCF_Units'] += \
#                ' '+attributes[ncvar].pop('calendar', '')
            try:
                attributes[ncvar]['nonCF_Units'] += \
                 ' '+attributes[ncvar].pop('calendar', '')
            except:
                pass
            if verbose:
                print(
"WARNING: Moving unsupported units to 'nonCF_Units': {0}".format(
    attributes[ncvar]['nonCF_Units']))
    #--- End: for

    # ----------------------------------------------------------------
    # Remove everything bar data variables from the list of
    # variables. I.e. remove dimension and auxiliary coordinates,
    # their bounds and grid_mapping variables
    # ----------------------------------------------------------------
    nc_dimensions = map(str, nc.dimensions)
    if _debug:
        print 'nc_dimensions =', nc_dimensions

    sample_ncdimension   = None
    instance_ncdimension = None
        
    for ncvar in variables.copy():
        if ncvar not in variables:
            # Skip netCDF variables which have already been checked
            continue
        
        if _debug:
            print 'Pre-processing', ncvar

        # Remove list, index and count variables
        compressed_ncdims = attributes[ncvar].get('compressed', None)
        if compressed_ncdims is not None:
            # List variable (compression by gathering)
            if _debug:
                print '    List variable: compressed =', compressed_ncdims
            _uuu(nc, ncvar, compressed_ncdims, g=g)
            variables.discard(ncvar)
            
        if 'sample_dimension' in attributes[ncvar]:
            # Count variable (DSG contiguous ragged arrays)
            sample_ncdimension = attributes[ncvar]['sample_dimension']        
            element_dimension_2 = _parse_DSG_contiguous_compression(nc, ncvar,
                                                                    attributes,
                                                                    sample_ncdimension,
                                                                    g=g)
            variables.discard(ncvar)
            
        if 'instance_dimension' in attributes[ncvar]:
            # Index variable (DSG indexed ragged arrays)
            instance_ncdimension = attributes[ncvar]['instance_dimension']
            element_dimension_1 = _parse_DSG_indexed_compression(nc, ncvar,
                                                                 attributes,
                                                                 instance_ncdimension,
                                                                 g=g)
            variables.discard(ncvar)

        if sample_ncdimension and instance_ncdimension:
            _parse_DSG_indexed_contiguous_compression(nc, ncvar,
                                                      sample_ncdimension,
                                                      instance_ncdimension,
                                                      g=g)
            sample_ncdimension   = None
            instance_ncdimension = None

        # Remove dimension coordinates and their bounds
        if ncvar in nc_dimensions:

            if ncvar in variables:

                if 'dimension_coordinate' in field:
                    # Add the dimension coordinate to the set of
                    # top-level fields, so that it doesn't get demoted
                    # if the auxiliary coordinate is also in a
                    # coordinate reference.
                    g['promoted'].append(ncvar)
                else:
                    # Do not promote a dimension coordinate to also
                    # appear as a top-level field
                    if _debug:
                        print '    Is a coordinatevariable'
                    variables.discard(ncvar)

                for attr in ('bounds', 'climatology'):
                    if attr not in attributes[ncvar]:
                        continue
                
                    # Check the dimensionality of the coordinate's
                    # bounds. If it is not right, then it can't be a
                    # bounds variable and so promote to an independent
                    # data variable
                    bounds = attributes[ncvar][attr]
                    if bounds in nc.variables:
                        if nc.variables[bounds].ndim == nc.variables[ncvar].ndim+1:
                            variables.discard(bounds)
                        else:
                            del attributes[ncvar][attr]

                        break
                    else:
                        del attributes[ncvar][attr]
                        if verbose:
                            print(
"WARNING: Missing bounds variable {0!r} in {1}".format(bounds, filename))
                #--- End: for


                # Remove domain ancillaries (unless they have been
                # promoted) and their bounds.
                if 'formula_terms' in attributes[ncvar]:
                    formula_terms = attributes[ncvar]['formula_terms']
                    if _debug:
                        print '        Has formula_terms'
                            
                    _formula_terms_variables(ncvar, formula_terms,
                                             variables, coord=True, g=g)
    
                    bounds = attributes[ncvar].get('bounds', None)
                    if bounds is not None and 'formula_terms' in attributes[bounds]:
                        bounds_formula_terms = attributes[bounds]['formula_terms']
                        
                        _formula_terms_variables(ncvar,
                                                 bounds_formula_terms,
                                                 variables,
                                                 bounds=True, g=g)
                #--- End: if
    

#                if 'formula_terms' in attributes[ncvar]:
#                    formula_terms = re.split('\s+|\s*:\s+',
#                                             attributes[ncvar]['formula_terms'])
#                    
#                    for var in formula_terms[1::2]:
#                        # Skip terms which are in the list but not in the file
#                        if var not in nc.variables:
#                            continue
#                        if _ncdimensions(nc, var, g=g):
#                            if 'domain_ancillary' not in field:
#                                # Do not promote a domain ancillary to
#                                # also appear as a top-level field
#                                variables.discard(var)
#                        else:
#                            # Value is a scalar
#                            if 'domain_ancillary' not in field:
#                                # Do not promote a parameter to also
#                                # appear as a top-level field
#                                variables.discard(var)
            #--- End: if

            continue
        #--- End: if

        # Still here? Then remove auxiliary coordinates (unless they
        # have been promoted) and their bounds.
        if 'coordinates' in attributes[ncvar]:
            # Allow for (incorrect) comma separated lists
            for aux in re.split('\s+|\s*,\s*', attributes[ncvar]['coordinates']):
                if aux in variables:
                    
                    if 'auxiliary_coordinate' in field:
                        # Add the auxiliary coordinate to the set of
                        # top-level fields, so that it doesn't get
                        # demoted if the auxiliary coordinate is also
                        # in a coordinate reference.
                        g['promoted'].append(ncvar)
                    else:
                        # Do not promote an auxiliary coordinate to
                        # also appear as a top-level field
                        if _debug:
                            print '    Has auxiliary coordinate:', aux
                        variables.discard(aux)

                    for attr in ('bounds', 'climatology'):
                        if attr not in attributes[aux]:
                            continue

                        # Check the dimensionality of the coordinate's
                        # bounds. If it is not right, then it can't be
                        # a bounds variable and so promote to an
                        # independent data variable.
                        bounds = attributes[aux][attr]
                        if bounds in nc.variables:
                            if nc.variables[bounds].ndim == nc.variables[aux].ndim+1:
                                variables.discard(bounds)
                            else:
                                del attributes[aux][attr]

                            break
                        else:
                            del attributes[aux][attr]
                            if verbose:
                                print(
"WARNING: Missing bounds variable {0!r} in {1}".format(bounds, filename))
            #--- End: for
        #--- End: if
        
        # Remove field ancillaries (unless they have been promoted).
        if ('field_ancillary' not in field and
            'ancillary_variables' in attributes[ncvar]):
            # Allow for (incorrect) comma separated lists
            for anc in re.split('\s+|\s*,\s*',
                                attributes[ncvar]['ancillary_variables']):
                if _debug:
                    print '    Has field ancillary:', anc
                variables.discard(anc)
        #--- End: if

        # Remove grid mapping variables
        if 'grid_mapping' in attributes[ncvar]:
            if _debug:
                print '    Has grid mapping:', ncvar
            variables.discard(attributes[ncvar]['grid_mapping'])

        # Remove cell measure variables (unless they have been promoted).
        if 'cell_measure' not in field and 'cell_measures' in attributes[ncvar]:
            cell_measures = re.split('\s*(\w+):\s*',
                                     attributes[ncvar]['cell_measures'])
            for msr in cell_measures[2::2]:
                if _debug:
                    print '    Has cell measure:', msr
                variables.discard(msr)
        #--- End: if
    #--- End: for

    g['DSG'] = global_attributes.get('featureType', False)
            
    # ----------------------------------------------------------------
    # Everything left in the variables set is now a proper data
    # variable, so make a list of fields, each of which contains one
    # data variable and the relevant shared metadata.
    # ----------------------------------------------------------------
    if _debug:
        print 'Data variables that will become fields:'
        for ncvar in variables:
            print '   ', ncvar

    domain_ancillaries    = {}
    field_ancillaries     = {}
    dimension_coordinates = {}
    auxiliary_coordinates = {}
    cell_measures         = {}
    coordref_parameters   = {}
    list_variables        = {}

    fields_in_file = FieldList()

    for data_ncvar in variables:
        if _is_cfa_private_variable(nc.variables[data_ncvar], g=g):
            # This netCDF variable is private CFA variable, so don't
            # turn it into a field.
            continue

        f = _create_Field(filename,
                          nc,
                          data_ncvar,
                          attributes,
                          dimension_coordinates,
                          auxiliary_coordinates,
                          cell_measures,
                          domain_ancillaries,
                          field_ancillaries,
                          coordref_parameters,
                          list_variables,
                          g=g,
                          verbose=verbose)

        fields_in_file.append(f)
    #--- End: for

    return fields_in_file
#--- End: def

def _uuu(nc, ncvar, attributes, compressed_ncdims, g=None):
    '''
'''
    compression_type = 'gathered'
    gathered_ncdimension = nc[ncvar].dimensions[0]
    list_array = _create_Variable(nc, ncvar, attributes, g=g).array
    
    compression[gathered_ncdimension] = {
        compression_type: {'array'               : list_array,
                           'implied_ncdimensions': compressed_ncdims.split()}}
    
    return compression
#--- End: def

def _parse_DSG_contiguous_compression(nc, ncvar, attributes,
                                      sample_ncdimension, g=None):
    '''
    ncvar: `str`
        The netCDF variable name of the DSG count variable.

    attributes: `dict`

    sample_ncdimension: `str`
        The netCDF variable name of the DSG sample dimension.
'''
    _debug = g['_debug']
    if _debug:
        print '    DSG count variable: sample_dimension =', sample_ncdimension

    filename = nc.filepath()
    
    compression_type = _compression_type['DSG_contiguous']

    variable = nc[ncvar]
    instance_ncdimension    = variable.dimensions[0]
    instance_dimension_size = variable.size

    count = _create_Variable(nc, ncvar, attributes, uncompress=False, g=g)
    count_array = count.array

    del count
    if not nc.isopen():
        # Re-read the netCDF file if it has been closed during the
        # deletion of count
        nc = _open_netcdf_file(filename, 'r')

    element_dimension_size = count_array.max()

    # Create an empty Data array which has dimensions (instance
    # dimension, element dimension).
    data = Data.empty(shape=(instance_dimension_size,
                             element_dimension_size),
                      chunk=False)

    data.chunk(total=[0], omit_axes=[1])
    if _debug:
        print '    DSG contiguous array implied shape:', data.shape

    start = 0
    for n, partition in izip(count_array, data.partitions.flat):
        end = start + n
        partition.subarray = CompressedArray(
            array=None,   # Will be set later
            shape=partition.shape,
            compression={compression_type: {
                'instance_axis'    : 0,
                'instance_index'   : 0,
                'c_element_axis'   : 1,
                'c_element_indices': slice(start, end)}})
        partition.part = []
        
        start += n
    #--- End: for

    # Make up a netCDF dimension name for the element dimension
    featureType = g['global_attributes'].get('featureType')
    if featureType in ('timeSeries', 'trajectory', 'profile'):
        element_dimension = featureType.lower()
    elif featureType == 'timeSeriesProfile':
        element_dimension = 'profile'
    elif featureType == 'trajectoryProfile':
        element_dimension = 'profile'
    else:
        element_dimension = 'element'
    if _debug:        
        print '    featureType =', featureType

    base = element_dimension
    n = 0
    while (element_dimension in nc.dimensions or
           element_dimension in g['new_dimensions']):
        n += 1
        element_dimension = '{0}_{1}'.format(base, n)
         
    g['compression'].setdefault(sample_ncdimension, {})[compression_type] = {
        'array'               : count_array,
        'empty_data'          : data,
        'implied_ncdimensions': (instance_ncdimension,
                                 element_dimension),
        'profile_ncdimension' : instance_ncdimension,
        'element_dimension'   : element_dimension,
    }

    g['new_dimensions'][element_dimension] = element_dimension_size
    
    if _debug:
        print "    Creating g['compression'][{!r}][{!r}]".format(sample_ncdimension,
                                                                 compression_type)

    return element_dimension
#--- End: def

def _parse_DSG_indexed_compression(nc, ncvar, attributes,
                                   instance_ncdimension, g=None):
    '''
    ncvar: `str`
        The netCDF variable name of the DSG index variable.

    attributes: `dict`

    instance_ncdimension: `str`
        The netCDF variable name of the DSG instance dimension.

    '''
    _debug = g['_debug']
    if _debug:
        print '    DSG index variable: instance_dimension =', instance_ncdimension

    filename = nc.filepath()
    
    compression_type = _compression_type['DSG_indexed']

    instance_dimension_size = nc.dimensions[instance_ncdimension].size
    
    index = _create_Variable(nc, ncvar, attributes, uncompress=False, g=g)
    index_array = index.array
    
    del index
    if not nc.isopen():
        # Re-read the netCDF file if it has been closed during the
        # deletion of index
        nc = _open_netcdf_file(filename, 'r')

    (instances, inverse, counts) = numpy_unique(index_array,
                                                return_inverse=True,
                                                return_counts=True)
    element_dimension_size = counts.max()
    
    # Create an empty Data array which has dimensions
    # (instance dimension, element dimension)
    data = Data.empty(shape=(instance_dimension_size,
                             element_dimension_size),
                      chunk=False)
    data.chunk(total=[0], omit_axes=[1])
    if _debug:        
        print '    DSG indexed array implied shape:', data.shape

    for i, partition in izip(numpy_unique(inverse), data.partitions.flat):
        partition.subarray = CompressedArray(
            array=None, # Will be set later
            shape=partition.shape,
            compression={compression_type: {
                'instance_axis'    : 0,
                'instance_index'   : 0,
                'i_element_axis'   : 1,
                'i_element_indices': numpy_where(inverse == i)[0]}})
        partition.part = []

    # Make up a netCDF dimension name for the element dimension
    featureType = g['global_attributes'].get('featureType')
    if featureType in ('timeSeries', 'trajectory', 'profile'):
        element_dimension = featureType.lower()
    elif featureType == 'timeSeriesProfile':
        element_dimension = 'timeseries'
    elif featureType == 'trajectoryProfile':
        element_dimension = 'trajectory'
    else:
        element_dimension = 'element'
    if _debug:        
        print '    featureType =', featureType

    base = element_dimension
    n = 0
    while (element_dimension in nc.dimensions or
           element_dimension in g['new_dimensions']):
        print  element_dimension
        n += 1
        element_dimension = '{0}_{1}'.format(base, n)
        
    indexed_sample_dimension = nc[ncvar].dimensions[0]
    
    g['compression'].setdefault(indexed_sample_dimension, {})[compression_type] = {
        'array'               : index_array,
        'empty_data'          : data,
        'implied_ncdimensions': (instance_ncdimension,
                                 element_dimension),
        'element_dimension'   : element_dimension,
    }

    g['new_dimensions'][element_dimension] = element_dimension_size
    
    if _debug:
        print "    Created g['compression'][{!r}][{!r}]".format(indexed_sample_dimension,
                                                                compression_type)

    return element_dimension
#--- End: def

def _parse_DSG_indexed_contiguous_compression(nc, ncvar,
                                              sample_ncdimension,
                                              instance_ncdimension,
                                              g=None):
    ''':Parameters:

    sample_ncdimension: `str`
        The netCDF dimension name of the DSG sample dimension.

    element_dimension_1: `str`
        The name of the implied element dimension whose size is the
        maximum number of sub-features in any instance.

    element_dimension_2: `str`
        The name of the implied element dimension whose size is the
        maximum number of elements in any sub-feature.

    '''
    _debug = g['_debug']
    if _debug:
        print 'Pre-processing DSG indexed and contiguous compression'

    compression_type = _compression_type['DSG_indexed_contiguous']

    profile_ncdimension = g['compression'][sample_ncdimension][_compression_type['DSG_contiguous']]['profile_ncdimension']

    if _debug:
        print '    sample_ncdimension  :', sample_ncdimension
        print '    instance_ncdimension:', instance_ncdimension
        print '    profile_ncdimension :', profile_ncdimension
        
    contiguous = g['compression'][sample_ncdimension][_compression_type['DSG_contiguous']]
    indexed    = g['compression'][profile_ncdimension][_compression_type['DSG_indexed']]

    count_array = contiguous['array']
    index_array = indexed['array']

    (instances, inverse, features_per_instance) = numpy_unique(
        index_array,
        return_counts=True,
        return_inverse=True)

    instance_dimension_size  = instances.size
    element_dimension_1_size = features_per_instance.max()
    element_dimension_2_size = count_array.max()

    # Create an empty Data array which has dimensions
    # (instance_dimension, element_dimension_1, element_dimension_2)
    data = Data.empty(
        shape=(instance_dimension_size,
               element_dimension_1_size,
               element_dimension_2_size),
        chunk=False)
    data.chunk(total=[0, 1], omit_axes=[2])
    if _debug:
        print '    DSG indexed and contiguous array implied shape:', data.shape

    f = {}
    for ind, partition in data.partitions.ndenumerate():
        (i, j) = ind

        partition = data.partitions[ind]
        partition.part = []
        
        x = numpy_where(inverse == instances[i])[0]
        if j < x.size:
            start = count_array[:x[j]].sum()
            stop  = start + count_array[x[j]]
            
            partition.subarray = CompressedArray(
                array=None, # Will be set later
                shape=partition.shape,
                compression = {compression_type: {
                    'instance_axis'    : 0,
                    'instance_index'   : 0,
                    'i_element_axis'   : 1,
                    'i_element_index'  : 0,
                    'c_element_axis'   : 2,
                    'c_element_indices': slice(start, stop)}})
        else:
            # This subarray will get replaced with missing data in
            # _set_Data
            partition.subarray = None            
    #--- End: for
    
    if _debug:
        print "    Creating g['compression'][{!r}][{!r}]".format(sample_ncdimension,
                                                                 compression_type)
    g['compression'][sample_ncdimension][compression_type] = {
        'empty_data'          : data,
        'implied_ncdimensions': (instance_ncdimension,
                                 indexed['element_dimension'],
                                 contiguous['element_dimension'])
    }

    if _debug:
        print '    Implied dimensions: {} -> {}'.format(
            sample_ncdimension,
            g['compression'][sample_ncdimension][compression_type]['implied_ncdimensions'])

    if _debug:
        print "    Removing g['compression'][{!r}][{!r}]".format(sample_ncdimension,
                                                                 _compression_type['DSG_contiguous'])
    del g['compression'][sample_ncdimension][_compression_type['DSG_contiguous']]
#--- End: def

def _formula_terms_variables(ncvar, formula_terms, variables,
                             coord=False, bounds=False, g=None):
    '''
:Parameters:

    ncvar: `str`

    formula_terms: `str`
        A CF-netCDF formula_terms attribute.

    variables: `set`
    '''
    g['formula_terms'].setdefault(ncvar, {'coord' : {},
                                          'bounds': {}})
    
    formula_terms = re.split('\s+|\s*:\s+',formula_terms)

    if bounds:
        b = ' bounds'
    else:
        b = ''
        
    for name, term in zip(formula_terms[0::2],
                          formula_terms[1::2]):
        # Skip terms which are in the list but not in the file
        if term not in g['nc'].variables:
            continue
        
        if g['_debug']:
            print '        Has domain ancillary{}: {}'.format(b, term)

        if 'domain_ancillary' not in g['field']:
            # Do not promote a domain ancillary to also appear as a
            # top-level field
            variables.discard(term)
        else:
            g['promoted'].append(term)
            
        if bounds and term not in g['formula_terms'][ncvar]['coord'].values():
            # Do not promote a domain ancillary's bounds to also
            # appear as a top-level field
            variables.discard(term)
            g['promoted'].append(term)

        if coord:
            g['formula_terms'][ncvar]['coord'][name] = term
        elif bounds:
            g['formula_terms'][ncvar]['bounds'][name] = term
#--- End: def
    
def _create_Field(filename,
                  nc,
                  data_ncvar,
                  attributes,
                  dimension_coordinates,
                  auxiliary_coordinates,
                  cell_measures,
                  domain_ancillaries,
                  field_ancillaries,
                  coordref_parameters,
                  list_variables,
                  g=None,
                  verbose=False):
    '''

Create a field for a given netCDF variable.

:Parameters:

    filename: `str`
        The name of the netCDF file.

    nc: `netCDF4.Dataset`
        The entire netCDF file in a `netCDF4.Dataset` instance.

    data_ncvar: `str`
        The name of the netCDF variable to be turned into a field.

    attributes: `dict`
        Dictionary of the data variable's netCDF attributes.

:Returns:

    out : Field
        The new field.

'''
    _debug = g['_debug']
    if _debug:
        print 'Converting data variable {} to a Field:'.format(data_ncvar)
    
    compression = g['compression']
    
    properties = attributes[data_ncvar]

    # Add global attributes to the data variable's properties, unless
    # the data variables already has a property with the same name.
    for attr, value in g['global_attributes'].iteritems():
        if attr not in properties:
            properties[attr] = value

    # Take cell_methods out of the data variable's properties since it
    # will need special processing once the domain has been defined
    cell_methods = properties.pop('cell_methods', None)
    if cell_methods is not None:
        try:
            cell_methods = CellMethods(cell_methods)
        except:
            # Something went wrong whilst trying to parse the cell
            # methods string
            properties['nonCF_cell_methods'] = cell_methods
            cell_methods = None
            if verbose:
                print(
"WARNING: Moving unsupported cell methods to 'nonCF_cell_methods': {0!r}".format(
    cell_methods))

    # Take add_offset and scale_factor out of the data variable's
    # properties since they will be dealt with by the variable's Data
    # object. Makes sure we note that they were there so we can adjust
    # the field's dtype accordingly
    values = [properties.pop(k, None) for k in ('add_offset', 'scale_factor')]
    unpacked_dtype = values != [None, None]
    if unpacked_dtype:
        try:
            values.remove(None)
        except ValueError:
            pass

        unpacked_dtype = numpy_result_type(*values)
    #--- End: if    

    # Change numpy arrays to tuples for selected attributes
    for attr in ('valid_range',):
#        if attr in attributes[data_ncvar]:
#            attributes[data_ncvar][attr] = tuple(attributes[data_ncvar][attr])
        if attr in properties:
            properties[attr] = tuple(properties[attr])

    # ----------------------------------------------------------------
    # Initialize the field with the data variable and its attributes
    # ----------------------------------------------------------------
    f_Units = Units(properties.pop('units', None),
                    properties.pop('calendar', None))

    f = Field(properties=properties, copy=False)

    f.ncvar = data_ncvar
    f.file  = filename
    f.Units = f_Units

    f._global_attributes = tuple(g['global_attributes'])

    # Map netCDF dimension dimension names to domain axis names.
    # 
    # For example:
    # >>> ncdim_to_axis
    # {'lat': 'dim0', 'time': 'dim1'}
    ncdim_to_axis = {}

    ncscalar_to_axis = {}

    ncvar_to_key = {}
        
    f._data_axes = []
#    f.ncdimensions = {}

    # ----------------------------------------------------------------
    # Add axes and non-scalar dimension coordinates to the field
    # ----------------------------------------------------------------
    field_ncdimensions = _ncdimensions(nc, data_ncvar, g=g)
    if _debug:
        print '    Field dimensions:', field_ncdimensions
        
    for ncdim in field_ncdimensions:
        if ncdim in nc.variables:

            # There is a Unidata coordinate variable for this dimension, so
            # create the coordinate and the dimension.
            if ncdim in dimension_coordinates:
                coord = dimension_coordinates[ncdim].copy()
            else:
                coord = _create_bounded_item(nc, ncdim, attributes, f,
                                             dimension=True, g=g,
                                             verbose=verbose)
                dimension_coordinates[ncdim] = coord
            #--- End: if
            
            if _debug:
                print '    Inserting', repr(coord)
            dim = f.insert_dim(coord, copy=False)
            # Record the netCDF dimension name for this axis
#            f.Axes[dim].ncdim = ncdim
            f.axes()[dim].ncdim = ncdim

            # Set unlimited status of axis
            if nc.dimensions[ncdim].isunlimited():
                f.unlimited({dim: True})

            ncvar_to_key[ncdim] = dim
        else:

            # There is no dimension coordinate for this dimension, so
            # just create a dimension with the correct size.
            if ncdim in g['new_dimensions']:
                size = g['new_dimensions'][ncdim]
            else:
                size = len(nc.dimensions[ncdim])

            axis = DomainAxis(size)
            if _debug:
                print '    Inserting', repr(axis)
            dim = f.insert_axis(axis)
            # Record the netCDF dimension name for this axis
#            f.Axes[dim].ncdim = ncdim
            f.axes()[dim].ncdim = ncdim
            
            # Set unlimited status of axis
            try:
                if nc.dimensions[ncdim].isunlimited():
                    f.unlimited({dim: True})
            except KeyError:
                # This dimension is not in the netCDF file (as might
                # be the case for an element dimension implied by a
                # DSG ragged array).
                pass            
        #--- End: if

        # Update data dimension name and set dimension size
        f._data_axes.append(dim)
        
        ncdim_to_axis[ncdim] = dim
    #--- End: for

    f.Data = _set_Data(nc, nc.variables[data_ncvar], f,
                       unpacked_dtype=unpacked_dtype, g=g)

    # ----------------------------------------------------------------
    # Add scalar dimension coordinates and auxiliary coordinates to
    # the field
    # ----------------------------------------------------------------
    coordinates = f.getprop('coordinates', None)
    if coordinates is not None:
        
        # Split the list (allowing for incorrect comma separated
        # lists).
        for ncvar in re.split('\s+|\s*,\s*', coordinates):
            # Skip dimension coordinates which are in the list
            if ncvar in field_ncdimensions:
                continue

            # Skip auxiliary coordinates which are in the list but not
            # in the file
            if ncvar not in nc.variables:
                continue

            # Set dimensions for this variable 
            aux_ncdimensions = _ncdimensions(nc, ncvar, g=g)
            dimensions = [ncdim_to_axis[ncdim] for ncdim in aux_ncdimensions
                          if ncdim in ncdim_to_axis]

            if ncvar in auxiliary_coordinates:
                coord = auxiliary_coordinates[ncvar].copy()
            else:
                coord = _create_bounded_item(nc, ncvar, attributes, f,
                                             auxiliary=True, g=g,
                                             verbose=verbose)
                auxiliary_coordinates[ncvar] = coord
            #--- End: if

            # --------------------------------------------------------
            # Turn a 
            # --------------------------------------------------------
            is_dimension_coordinate = False
            scalar = False
            if not dimensions:
                scalar = True
                if nc.variables[ncvar].dtype.kind is 'S':
                    # String valued scalar coordinate. Is this CF
                    # compliant? Don't worry about it - we'll just
                    # turn it into a 1-d, size 1 auxiliary coordinate
                    # construct.
                    axis = DomainAxis(1)
                    if _debug:
                        print '    Inserting', repr(axis)
                    dim = f.insert_axis(axis)
                    # Record the netCDF dimension name for this axis
#                    f.Axes[dim].ncdim = ncdim                    
                    f.axes()[dim].ncdim = ncdim
                    dimensions = [dim]
                else:  
                    # Numeric valued scalar coordinate
                    is_dimension_coordinate = True
            #--- End: if

            if is_dimension_coordinate:
                # Insert dimension coordinate
                coord = coord.asdimension(copy=False)
                if _debug:
                    print '    Inserting', repr(coord)
                dim = f.insert_dim(coord, copy=False)
                # Record the netCDF dimension name for this axis
#                f.Axes[dim].ncdim = ncvar
                f.axes()[dim].ncdim = ncvar
                dimensions = [dim]
                ncvar_to_key[ncvar] = dim
                dimension_coordinates[ncvar] = coord
                del auxiliary_coordinates[ncvar]
            else:
                # Insert auxiliary coordinate
                if _debug:
                    print '    Inserting', repr(coord)
                aux = f.insert_aux(coord, axes=dimensions, copy=False)
                ncvar_to_key[ncvar] = aux
            
            if scalar:
                ncscalar_to_axis[ncvar] = dimensions[0]
        #--- End: for

        f.delprop('coordinates')
    #--- End: if

    # ----------------------------------------------------------------
    # Add coordinate references from formula_terms properties
    # ----------------------------------------------------------------
    for key, coord in f.coords().iteritems():
        if data_ncvar in g['promoted']:
            break
        
        formula_terms = attributes[coord.ncvar].get('formula_terms', None)
        if formula_terms is None:
            # This coordinate doesn't have a formula_terms attribute
            continue

        formula_terms = re.split('\s+|\s*:\s+', formula_terms)

        for term, ncvar in zip(formula_terms[0::2], formula_terms[1::2]):
            # Skip terms which are in the list but not in the file
            if ncvar not in nc.variables:
                continue

            # Set dimensions 
            anc_ncdimensions = _ncdimensions(nc, ncvar, g=g)
            axes = [ncdim_to_axis[ncdim] for ncdim in anc_ncdimensions
                    if ncdim in ncdim_to_axis]    
            
#            if not axes:
#                # Variable is scalar => term is a parameter, not a
#                # DomainAncillary
#                if ncvar not in coordref_parameters:
#                    variable = _create_Variable(nc, ncvar, attributes, g=g)
#                    coordref_parameters[ncvar] = variable
#                continue
#
#            # Still here? Then the term is a DomainAncillary, not a
#            # parameter.
            if ncvar in domain_ancillaries:
                domain_anc = domain_ancillaries[ncvar][1].copy()
            else: 
                bounds = g['formula_terms'][coord.ncvar]['bounds'].get(term)
                if bounds == ncvar:
                    bounds = None

                domain_anc = _create_bounded_item(nc, ncvar, attributes, f,
                                                  domainancillary=True, g=g,
                                                  bounds=bounds,
                                                  verbose=verbose)
#                domain_ancillaries[ncvar] = domain_anc

            # Insert domain ancillary
            da_key = f.insert_domain_anc(domain_anc, axes=axes, copy=False)
            if ncvar not in ncvar_to_key:
                ncvar_to_key[ncvar] = da_key

            domain_ancillaries[ncvar] = (da_key, domain_anc)
            
        #--- End: for

        _create_formula_terms_ref(f, key, coord,
                                  g['formula_terms'][coord.ncvar]['coord'],
                                  domain_ancillaries, g=g)
    #--- End: for

    # ----------------------------------------------------------------
    # Add grid mapping coordinate references
    # ----------------------------------------------------------------
    grid_mapping = f.getprop('grid_mapping', None)
    if grid_mapping is not None:
        _create_grid_mapping_ref(f, grid_mapping, attributes, ncvar_to_key)

    # ----------------------------------------------------------------
    # Add cell measures to the field
    # ----------------------------------------------------------------
    measures = f.getprop('cell_measures', None)
    if measures is not None:

        # Parse the cell measures attribute
        measures = re.split('\s*(\w+):\s*', measures)
        
        for measure, ncvar in zip(measures[1::2], 
                                  measures[2::2]):

            if ncvar not in attributes:
                continue

            # Set cell measures' dimensions 
            cm_ncdimensions = _ncdimensions(nc, ncvar, g=g)
            axes = [ncdim_to_axis[ncdim] for ncdim in cm_ncdimensions]

            if ncvar in cell_measures:
                # Copy the cell measure as it already exists
                cell = cell_measures[ncvar].copy()
            else:
                cell = _create_item(nc, ncvar, attributes, f,
                                    cell_measure=True, g=g)
                cell.measure = measure
                cell_measures[ncvar] = cell
            #--- End: if

            clm = f.insert_measure(cell, axes=axes, copy=False)

            ncvar_to_key[ncvar] = clm
        #--- End: for

        f.delprop('cell_measures')
    #--- End: if

    # ----------------------------------------------------------------
    # Add cell methods to the field
    # ----------------------------------------------------------------
    if cell_methods is not None:
        name_to_axis = ncdim_to_axis.copy()
        name_to_axis.update(ncscalar_to_axis)
        for cm in cell_methods:
            cm.axes = tuple([name_to_axis.get(axis, axis) for axis in cm.axes])
            
        f.insert_cell_methods(cell_methods)

    # ----------------------------------------------------------------
    # Add field ancillaries to the field
    # ----------------------------------------------------------------
    ancillary_variables = f.getprop('ancillary_variables', None)
    if ancillary_variables is not None:
        f.delprop('ancillary_variables')
        # Allow for incorrect comma separated lists
        for ncvar in re.split('\s+|\s*,\s*', ancillary_variables):
            # Skip variables which are in the list but not in the file
            if ncvar not in nc.variables:
                continue

            # Set dimensions 
            anc_ncdimensions = _ncdimensions(nc, ncvar, g=g)
            axes = [ncdim_to_axis[ncdim] for ncdim in anc_ncdimensions
                    if ncdim in ncdim_to_axis]    
            
            if ncvar in field_ancillaries:
                field_anc = field_ancillaries[ncvar].copy()
            else:
                field_anc = _create_item(nc, ncvar, attributes, f,
                                         field_ancillary=True, g=g)
                field_ancillaries[ncvar] = field_anc
                
            # Insert the field ancillary
            key = f.insert_field_anc(field_anc, axes=axes, copy=False)
            ncvar_to_key[ncvar] = key
    #--- End: if

    f.autocyclic()

    # Return the finished field
    return f
#--- End: def

def _create_bounded_item(nc, ncvar, attributes, f, dimension=False,
                         auxiliary=False, domainancillary=False,
                         bounds=None, g=None, verbose=False):
    '''Create a variable which might have bounds.

:Parameters:

    nc: `netCDF4.Dataset`
        The entire netCDF file in a `netCDF4.Dataset` object.

    ncvar: `str`
        The netCDF name of the variable.

    attributes: `dict`
        Dictionary of the variable's netCDF attributes.

    f: `cf.Field`

    dimension: `bool`, optional
        If True then a dimension coordinate is created.

    auxiliary: `bool`, optional
        If True then an auxiliary coordinate is created.

    domainancillary: `bool`, optional
        If True then a domain ancillary is created.

:Returns:

    out : `cf.DimensionCoordinate` or `cf.AuxiliaryCoordinate` or `cf.DomainAncillary`
        The new item.

    '''
    properties = attributes[ncvar].copy()

    c_Units = Units(properties.pop('units', None),
                    properties.pop('calendar', None))

    properties.pop('formula_terms', None)

    if bounds is not None:
        properties['bounds'] = bounds
    
    ncbounds = properties.pop('bounds', None)
    if ncbounds is None:
        ncbounds = properties.pop('climatology', None)
        climatology = True
    else:
        climatology = False

    if dimension:
        c = DimensionCoordinate(properties=properties)
    elif auxiliary:
        c = AuxiliaryCoordinate(properties=properties)
    elif domainancillary:
        properties.pop('coordinates', None)
        properties.pop('grid_mapping', None)
        properties.pop('cell_measures', None)

        properties.pop('formula_terms', None)
        properties.pop('positive', None)

        c = DomainAncillary(properties=properties)
    else:
        raise ValueError(
"Must set one of the dimension, auxiliary or domainancillary parmaeters to True")

    c.ncvar = ncvar
    c.Units = c_Units
    if climatology:
        c.climatology = climatology

    data = _set_Data(nc, nc.variables[ncvar], c, g=g)

    # ------------------------------------------------------------
    # Add any bounds
    # ------------------------------------------------------------
    if ncbounds is None:
        bounds = None
    else:
        properties = attributes[ncbounds].copy()
        properties.pop('formula_terms', None)

        b_Units = Units(properties.pop('units', None),
                        properties.pop('calendar', None))

        bounds = Bounds(properties=properties, copy=False)

        bounds.ncvar = ncbounds
        bounds.Units = b_Units
    
        bounds.insert_data(
            _set_Data(nc, nc.variables[ncbounds], bounds, g=g),
            copy=False)

        if not b_Units:
            bounds.override_units(c_Units, i=True)
           
        if b_Units and not b_Units.equivalent(c_Units):
            bounds.override_units(c_Units, i=True)
            if verbose:
                print(
"WARNING: Overriding {0} of {1!r} bounds ({2!r}) with {3!r}".format(
    b_Units, ncvar, ncbounds, c_Units))
 
        # Make sure that the bounds dimensions are in the same order
        # as its parent's dimensions
        c_ncdims = nc.variables[ncvar].dimensions
        b_ncdims = nc.variables[ncbounds].dimensions
        if c_ncdims != b_ncdims[:-1]:
            iaxes = [c_ncdims.index(ncdim) for ncdim in b_ncdims[:-1]]
            iaxes.append(-1)
            bounds.transpose(iaxes, i=True)
    #--- End: if

    c.insert_data(data, copy=False)
    if bounds:
        c.insert_bounds(bounds, copy=False)

    # ---------------------------------------------------------
    # Return the bounded variable
    # ---------------------------------------------------------
    return c
#--- End: def

def _create_Variable(nc, ncvar, attributes, uncompress=True, g=None):
    '''

Create a variable.

:Parameters:

    nc : netCDF4.Dataset
        The entire netCDF file in a `netCDF4.Dataset` object.

    ncvar : str
        The netCDF name of the coordinate variable.

    attributes : dict
        Dictionary of the coordinate variable's netCDF attributes.

    g: `dict`

:Returns:

    out : cf.Variable
        The new variable.

'''
    v = Variable(properties=attributes[ncvar])

    data = _set_Data(nc, nc.variables[ncvar], v, uncompress=uncompress, g=g)

    v.insert_data(data, copy=False)

    v.ncvar = ncvar

    return v
#--- End: def

#def _create_CellMeasure(nc, ncvar, attributes, f, cfa=False): #, key=None):
#    '''
#
#Create a cell measure variable.
#
#:Parameters:
#
#    nc : netCDF4.Dataset
#        The entire netCDF file in a `netCDF4.Dataset` instance.
#
#    ncvar : str
#        The netCDF name of the cell measure variable.
#
#    attributes : dict
#        Dictionary of the cell measure variable's netCDF attributes.
#
#    f : Field
#
#    cfa : bool, optional
#        If True then netCDF file is a CFA file. By default it is
#        assumed that the file is not a CFA file.
#
#:Returns:
#
#    out : CellMeasure
#        The new cell measure.
#
#'''
#    clm       = CellMeasure(properties=attributes[ncvar])
#    clm.ncvar = ncvar
#
#    data = _set_Data(nc, nc.variables[ncvar], clm, g=g)
#
#    clm.insert_data(data, copy=False)
#
#    return clm
##--- End: def

def _create_item(nc, ncvar, attributes, f, cell_measure=False,
                 field_ancillary=False, g=None):
    '''

Create a cell measure or field ancillary object.

:Parameters:

    nc : netCDF4.Dataset
        The entire netCDF file in a `netCDF4.Dataset` instance.

    ncvar : str
        The netCDF name of the cell measure variable.

    attributes : dict
        Dictionary of the cell measure variable's netCDF attributes.

    f : Field

:Returns:

    out : CellMeasure
        The new cell measure.

'''
    if cell_measure:
        clm = CellMeasure(properties=attributes[ncvar])
    elif field_ancillary:
        clm = FieldAncillary(properties=attributes[ncvar])

    data = _set_Data(nc, nc.variables[ncvar], clm, g=g)

    clm.insert_data(data, copy=False)

    clm.ncvar = ncvar

    return clm
#--- End: def

def _ncdimensions(nc, ncvar, g=None):
    '''

Return a list of the netCDF dimensions corresponding to netCDF variable.

:Parameters:

    nc: `netCDF4.Dataset`
        The netCDF dataset.

    ncvar: `str`
        The netCDF variable name.

    g: `dict`

:Returns:

    out: `list`
        The list of netCDF dimension names.

:Examples: 

>>> _ncdimensions(nc, 'humidity', g=g)
['time', 'lat', 'lon']
'''
    ncvariable = nc.variables[ncvar]

    ncattrs = ncvariable.ncattrs()

    cfa = g['cfa']
    
    if (cfa and 
        'cf_role' in ncattrs and 
        ncvariable.getncattr('cf_role') == 'cfa_variable'):
        # The netCDF variable is a CFA variable
        if 'cfa_dimensions' in ncattrs:
            ncdimensions = ncvariable.getncattr('cfa_dimensions').split()
        else:
            ncdimensions = []
    else:
        # The netCDF variable is not a CFA variable
        ncdimensions = list(ncvariable.dimensions)
        cfa = False
      
    # Remove a string-length dimension, if there is one. DCH ALERT
    if (not cfa and 
        ncvariable.dtype.kind == 'S' and
        ncvariable.ndim >= 2 and ncvariable.shape[-1] > 1):
        ncdimensions.pop()

    # Check for dimensions which have been compressed. If there are
    # any, then return the netCDF dimensions for the uncompressed
    # variable.
    compression = g['compression']
    if compression and set(compression).intersection(ncdimensions):
        for ncdim in ncdimensions:
            if ncdim in compression:
                c = compression[ncdim]
                if 'gathered' in c:
                    # Compression by gathering
                    i = ncdimension.index(ncdim)
                    ncdimensions[i:i+1] = c['gathered']['implied_ncdimensions']
                elif 'DSG_indexed_contiguous' in c:
                    # DSG indexed contiguous ragged array.
                    #
                    # Check this before DSG_indexed and DSG_contiguous
                    # because both of these will exist for an array
                    # that is both indexed and contiguous.
                    i = ncdimensions.index(ncdim)
                    ncdimensions = c['DSG_indexed_contiguous']['implied_ncdimensions']
                elif 'DSG_contiguous' in c:
                    # DSG contiguous ragged array
                    ncdimensions = c['DSG_contiguous']['implied_ncdimensions']
                elif 'DSG_indexed' in c:
                    # DSG indexed ragged array
                    ncdimensions = c['DSG_indexed']['implied_ncdimensions']

                break
    #--- End: if
    
    return map(str, ncdimensions)
#--- End: def

def _create_grid_mapping_ref(f, grid_mapping, attributes, ncvar_to_key):
    '''

:Parameters:

    f : cf.Field

    grid_mapping : str

    attributes : dict

    ncvar_to_key : dict

:Returns:

    None

'''
    if ':' not in grid_mapping:
        grid_mapping = '{0}:'.format(grid_mapping)

    coordinates = []
    for x in re.sub('\s*:\s*', ': ', grid_mapping).split()[::-1]:
        if not x.endswith(':'):
            try:
                coordinates.append(ncvar_to_key[x])
            except KeyError:
                continue
        else:
            if not coordinates:
                coordinates = None

            grid_mapping = x[:-1]

            if grid_mapping not in attributes:
                coordinates = []      
                continue
                
                
            parameter_terms = attributes[grid_mapping].copy()
            
            name = parameter_terms.pop('grid_mapping_name', None)                 
  
            coordref = CoordinateReference(name,
                                           crtype='grid_mapping',
                                           coordinates=coordinates,
                                           parameters=parameter_terms)
            coordref.ncvar = grid_mapping

            f.insert_ref(coordref, copy=False)

            coordinates = []      
    #--- End: for

    f.delprop('grid_mapping')
#--- End: def

def _create_formula_terms_ref(f, key, coord, formula_terms,
                              domain_ancillaries, g=None):
    '''

:Parameters:

    f: `cf.Field`

    key: `str`

    coord: `cf.Coordinate`

    formula_terms: `dict`

    domain_ancillaries: `dict`

    coordref_parameters: `dict`
        Ignored.

:Returns:

    out: `cf.CoordinateReference`

'''
    parameters  = {}
    ancillaries = {}

#    for term, ncvar in zip(formula_terms[0::2], formula_terms[1::2]):
    for term, ncvar in formula_terms.iteritems():
#        if ncvar in domain_ancillaries:
        # The term's value is a domain ancillary of the field, so
        # we put its identifier into the coordinate reference.
        ancillaries[term] = domain_ancillaries[ncvar][0]

#        elif ncvar in coordref_parameters:
#            # The term's value is a parameter
#            parameters[term] = coordref_parameters[ncvar].copy()
    #--- End: for 

    coordref = CoordinateReference(name=coord.getprop('standard_name', None),
                                   crtype='formula_terms',
                                   coordinates=(key,),
#                                   parameters=parameters,
                                   ancillaries=ancillaries)

    f.insert_ref(coordref, copy=False)

    return coordref
#--- End: def

def _set_Data(nc, ncvar, variable, unpacked_dtype=False,
              uncompress=True, g=None):
    '''

Set the Data attribute of a variable.

:Parameters:

    nc: `netCDf4.Dataset`

    ncvar: `netCDF4.Variable`

    variable : `cf.Variable`

    unpacked_dtype: `False` or `numpy.dtype`, optional

    uncompress: `bool`
        If True then uncompress the data array, if it has been compressed.

    g: `dict`

:Returns:

    out: `cf.Data`

:Examples: 

'''    
    is_cfa_variable = variable.getprop('cf_role', None) == 'cfa_variable'

    if g['cfa'] and is_cfa_variable:
        # ------------------------------------------------------------
        # The netCDF variable is a CFA variable
        # ------------------------------------------------------------
        try:
            cfa_data = json_loads(variable.getprop('cfa_array'))
        except ValueError as error:
            raise ValueError(
"Error during JSON-decoding of netCDF attribute 'cfa_array': {}".format(error))

        cfa_data['file']       = g['filename']
        cfa_data['Units']      = variable.Units      
        cfa_data['fill_value'] = variable.fill_value()
        cfa_data['_pmshape']   = cfa_data.pop('pmshape', ())
        cfa_data['_pmaxes']    = cfa_data.pop('pmdimensions', ())
        
        base = cfa_data.get('base', None)
        if base is not None:
            cfa_data['base'] = pathjoin(dirname(g['filename']), base)
            
        ncdimensions = variable.getprop('cfa_dimensions', '').split()
        dtype = ncvar.dtype
        if dtype.kind == 'S' and ncdimensions:
            strlen = len(nc.dimensions[ncdimensions[-1]])
            if strlen > 1:
                ncdimensions.pop()
                dtype = numpy_dtype('S{0}'.format(strlen))
        #--- End: if
        cfa_data['dtype'] = dtype
        cfa_data['_axes'] = ncdimensions
        cfa_data['shape'] = [len(nc.dimensions[ncdim])
                             for ncdim in ncdimensions]

        for attrs in cfa_data['Partitions']:

            # FORMAT
            sformat = attrs.get('subarray', {}).pop('format', 'netCDF')
            if sformat is not None:
                attrs['format'] = sformat

            # DTYPE
            dtype = attrs.get('subarray', {}).pop('dtype', None)
            if dtype not in (None, 'char'):
                attrs['subarray']['dtype'] = numpy_dtype(dtype)

            # UNITS and CALENDAR
            units    = attrs.pop('punits', None)
            calendar = attrs.pop('pcalendar', None)
            if units is not None or calendar is not None:
                attrs['Units'] = Units(units, calendar)

            # AXES
            pdimensions = attrs.pop('pdimensions', None)
            if pdimensions is not None:
                attrs['axes'] = pdimensions

            # REVERSE
            reverse = attrs.pop('reverse', None)
            if reverse is not None:
                attrs['reverse'] = reverse

            # LOCATION: Change to python indexing (i.e. range does not
            #           include the final index)
            for r in attrs['location']:
                r[1] += 1

            # PART: Change to python indexing (i.e. slice range does
            #       not include the final index)
            part = attrs.get('part', None)
            if part:
                p = []
                for x in ast_literal_eval(part):
                    if isinstance(x, list):
                        if x[2] > 0:
                            p.append(slice(x[0], x[1]+1, x[2]))
                        elif x[1] == 0:
                            p.append(slice(x[0], None, x[2]))
                        else:
                            p.append(slice(x[0], x[1]-1, x[2]))
                    else:
                        p.append(list(x))
                #--- End: for
                attrs['part'] = p
        #--- End: for

        variable.delprop('cf_role')
        variable.delprop('cfa_array')
        if variable.hasprop('cfa_dimensions'):
            variable.delprop('cfa_dimensions')

        data = Data(loadd=cfa_data, chunk=g['chunk'])

    else:
        # ------------------------------------------------------------
        # The netCDF variable is not a CFA variable
        # ------------------------------------------------------------
        dtype = ncvar.dtype
        if unpacked_dtype is not False:
            dtype = numpy_result_type(dtype, unpacked_dtype)

        ndim  = ncvar.ndim
        shape = ncvar.shape
        size  = ncvar.size
        if size < 2:
            size = int(size)

        if dtype.kind == 'S' and ndim >= 1: #shape[-1] > 1:
            # Has a trailing string-length dimension
            strlen = shape[-1]
            shape = shape[:-1]
            size /= strlen
            ndim -= 1
            dtype = numpy_dtype('S{0}'.format(strlen))
        #--- End: if

        filearray = NetCDFFileArray(file=g['filename'],
                                    ncvar=ncvar._name,
                                    dtype=dtype,
                                    ndim=ndim,
                                    shape=shape,
                                    size=size)

        compression = g['compression']

        if (not uncompress or
            not compression or
            not set(compression).intersection(ncvar.dimensions)):
            # Either A) there is no compression in the file or B) some
            # variables in the file are compressed but this one isn't
            # or C) we have been instructed to not uncompress this
            # compressed variable.
            data = Data(filearray, units=variable.Units,
                        fill_value=variable.fill_value(),
                        chunk=g['chunk'])

        else:
            # --------------------------------------------------------
            # The array of the netCDF is compressed
            # --------------------------------------------------------
            # Loop round the data variables dimensions as they are in
            # the netCDF file
            for ncdim in ncvar.dimensions:
                if ncdim in compression:
                    c = compression[ncdim]
                    if 'gathered' in c:
                        # Compression by gathering
                        compression_type = 'gathered'

                        indices = c['gathered']['indices']

                        uncompressed_shape = [nc[ncdim].size for ncdim in ncvar.dimensions]
                        sample_axis = ncvar.dimensions.index(ncdim)

                        data = Data.empty(shape=tuple(uncompressed_shape),
                                          units=variable.units,
                                          dtype=variable.dtype,
                                          chunk=False)
                        data.fill_value = variable.fill_value()
                        data.chunk(omit_axes=[sample_axis])
                        
                        for partition in data.partitions.flat:
                            partition.subarray = CompressedArray(
                                array=filearray,
                                shape=partition.shape,
                                compression = {compression_type: {
                                    'sample_axis': sample_axis,
                                    'indices'    : indices}})
                            partition.part = []

                    elif _compression_type['DSG_indexed_contiguous'] in c:
                        # DSG contiguous indexed ragged array. Check
                        # this before DSG_indexed and DSG_contiguous
                        # because both of these will exist for an
                        # indexed and contiguous array.
                        data = c['DSG_indexed_contiguous']['empty_data'].copy()
                        data.dtype = filearray.dtype
                        data.Units = variable.Units
                        data.fill_value = variable.fill_value()
                        for partition in data.partitions.flat:
                            partition.Units = data.Units
                            if isinstance(partition.subarray, CompressedArray):
                                partition.subarray = partition.subarray.copy()
                                partition.subarray.array = filearray
                            else:
                                # This partition is full of missing data
                                partition.subarray = FilledArray(shape=partition.shape,
                                                                 size=partition.size,
                                                                 ndim=partition.ndim,
                                                                 dtype=filearray.dtype,
                                                                 masked_all=True,
                                                                 fill_value=0)
                        #--- End: for

                    elif _compression_type['DSG_contiguous'] in c:
                        # DSG contiguous ragged array
                        data = c['DSG_contiguous']['empty_data'].copy()
                        data.dtype = filearray.dtype
                        data.Units = variable.Units
                        data.fill_value = variable.fill_value()
                        for partition in data.partitions.flat:
                            partition.subarray = partition.subarray.copy()
                            partition.subarray.array = filearray
                            partition.Units          = data.Units
                            
                    elif _compression_type['DSG_indexed'] in c:
                        # DSG indexed ragged array
                        data = c['DSG_indexed']['empty_data'].copy()
                        data.dtype = filearray.dtype
                        data.Units = variable.Units
                        data.fill_value = variable.fill_value()
                        for partition in data.partitions.flat:
                            partition.subarray = partition.subarray.copy()
                            partition.subarray.array = filearray
                            partition.Units          = data.Units
                            
                    else:
                        raise ValueError("Bad compression vibes. c.keys()={}".format(c.keys()))
    #--- End: if

    return data
#--- End: def

def _is_cfa_private_variable(ncvar, g=None):
    '''

Return True if a netCDF variable is a CFA private variable.

:Parameters:

    ncvar: `netCDF4.Variable`

:Returns:

    out: `bool`
        True if ``g['cfa']`` is True and *ncvar* is a CFA private
        variable. Otherwise False.

:Examples: 

>>> if _is_cfa_private_variable(x, g):
...     print 'This is private CFA'

>>> False == _is_cfa_private_variable(x, g)
True

'''  
    return (g['cfa'] and 
            'cf_role' in ncvar.ncattrs() and 
            ncvar.getncattr('cf_role') == 'cfa_private')
#--- End: def

def is_netcdf_file(filename):
    '''Return True if the file is a netCDF file.

Note that the file type is determined by inspecting the file's
contents and any file suffix is not not considered.

:Parameters:

    filename : str

:Returns:

    out : bool

:Examples:

>>> is_netcdf_file('myfile.nc')
True
>>> is_netcdf_file('myfile.pp')
False
>>> is_netcdf_file('myfile.pdf')
False
>>> is_netcdf_file('myfile.txt')
False

    '''
    # Read the magic number 
    try:
        fh = open(filename, 'rb')
        magic_number = struct_unpack('=L', fh.read(4))[0]
    except:
        magic_number = None

    try:
        fh.close()
    except:
        pass

    if magic_number in (21382211, 1128547841, 1178880137, 38159427):
        return True
    else:
        return False
#--- End: def
