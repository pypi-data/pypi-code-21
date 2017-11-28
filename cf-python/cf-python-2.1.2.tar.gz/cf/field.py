from collections           import OrderedDict
from copy                  import deepcopy
from itertools             import izip, izip_longest
from operator              import mul as operator_mul
from operator              import itemgetter
from scipy.ndimage.filters import convolve1d
from scipy.signal          import get_window

use_matplotlib = True
if use_matplotlib:
    from matplotlib.path import Path

from numpy import arange      as numpy_arange
from numpy import argmax      as numpy_argmax
from numpy import array       as numpy_array
from numpy import array_equal as numpy_array_equal
from numpy import asanyarray  as numpy_asanyarray
from numpy import can_cast    as numpy_can_cast
from numpy import diff        as numpy_diff
from numpy import empty       as numpy_empty
from numpy import errstate    as numpy_errstate
from numpy import finfo       as numpy_finfo
from numpy import isnan       as numpy_isnan
from numpy import nan         as numpy_nan
from numpy import ndarray     as numpy_ndarray
from numpy import size        as numpy_size
from numpy import squeeze     as numpy_squeeze
from numpy import tile        as numpy_tile
from numpy import unique      as numpy_unique
from numpy import where       as numpy_where
from numpy import zeros       as numpy_zeros

from numpy.ma import is_masked   as numpy_ma_is_masked
from numpy.ma import isMA        as numpy_ma_isMA
from numpy.ma import MaskedArray as numpy_ma_MaskedArray
from numpy.ma import where       as numpy_ma_where
from numpy.ma import masked_invalid as numpy_ma_masked_invalid

from .cellmeasure     import CellMeasure
from .cellmethods     import CellMethod, CellMethods
from .constants       import masked as cf_masked
from .coordinate      import DimensionCoordinate
from .domainancillary import DomainAncillary
from .domainaxis      import DomainAxis, Axes
from .fieldancillary  import FieldAncillary
from .flags           import Flags
from .functions       import (parse_indices, CHUNKSIZE, equals, RTOL,
                              ATOL, RELAXED_IDENTITIES,
                              IGNORE_IDENTITIES, _section)
from .functions       import inspect as cf_inspect
from .query           import Query, ge, gt, le, lt, ne, eq, wi
from .regrid          import Regrid
from .timeduration    import TimeDuration
from .units           import Units
from .variable        import Variable, SubspaceVariable #, RewriteDocstringMeta

from .data.data import Data

_debug = False

# --------------------------------------------------------------------
# Commonly used units
# --------------------------------------------------------------------
_units_radians = Units('radians')
_units_metres  = Units('m')

# --------------------------------------------------------------------
# Map each allowed input collapse method name to its corresponding
# cf.Data method. Input collapse methods not in this sictionary are
# assumed to have a corresponding cf.Data method with the same name.
# --------------------------------------------------------------------
_collapse_methods = {
    'mean'              : 'mean',
    'avg'               : 'mean',
    'average'           : 'mean',
    'max'               : 'max',
    'maximum'           : 'max',
    'min'               : 'min',
    'minimum'           : 'min',
    'mid_range'         : 'mid_range',
    'range'             : 'range',
    'standard_deviation': 'sd',
    'sd'                : 'sd',
    'sum'               : 'sum',
    'variance'          : 'var',
    'var'               : 'var',
    'sample_size'       : 'sample_size', 
    'sum_of_weights'    : 'sum_of_weights',
    'sum_of_weights2'   : 'sum_of_weights2',
}

# --------------------------------------------------------------------
# Map each allowed input collapse method name to its corresponding
# cf.Data method. Input collapse methods not in this sictionary are
# assumed to have a corresponding cf.Data method with the same name.
# --------------------------------------------------------------------
_collapse_cell_methods = {
    'point'             : 'point',
    'mean'              : 'mean',
    'avg'               : 'mean',
    'average'           : 'mean',
    'max'               : 'maximum',
    'maximum'           : 'maximum',
    'min'               : 'minimum',
    'minimum'           : 'minimum',
    'mid_range'         : 'mid_range',
    'range'             : 'range',
    'standard_deviation': 'standard_deviation',
    'sd'                : 'standard_deviation',
    'sum'               : 'sum',
    'variance'          : 'variance',
    'var'               : 'variance',
    'sample_size'       : None,
    'sum_of_weights'    : None,
    'sum_of_weights2'   : None,
}

# --------------------------------------------------------------------
# Map each cf.Data method to its corresponding minimum number of
# elements. cf.Data methods not in this dictionary are assumed to have
# a minimum number of elements equal to 1.
# --------------------------------------------------------------------
_collapse_min_size = {'sd' : 2,
                      'var': 2,
                      }

# --------------------------------------------------------------------
# These cf.Data methods may be weighted
# --------------------------------------------------------------------
_collapse_weighted_methods = set(('mean',
                                  'avg',
                                  'average',
                                  'sd',
                                  'standard_deviation',
                                  'var',
                                  'variance',
                                  'sum_of_weights',
                                  'sum_of_weights2',
                                  ))

# --------------------------------------------------------------------
# These cf.Data methods may specify a number of degrees of freedom
# --------------------------------------------------------------------
_collapse_ddof_methods = set(('sd',
                              'var',
                              ))

class DeprecationError(Exception):
    '''Exception for removed methods'''
    pass

# ====================================================================
#
# Field object
#
# ====================================================================

class Field(Variable):
    '''A CF field construct.

The field construct is central to the CF data model, and includes all
the other constructs. A field corresponds to a CF-netCDF data variable
with all of its metadata. All CF-netCDF elements are mapped to some
element of the CF field construct and the field constructs completely
contain all the data and metadata which can be extracted from the file
using the CF conventions.

The field construct consists of a data array (stored in a `cf.Data`
object) and the definition of its domain, ancillary metadata fields
defined over the same domain (stored in `cf.DomainAncillary` objects),
and cell methods constructs to describe how the cell values represent
the variation of the physical quantity within the cells of the domain
(stored in `cf.CellMethod` objects).

The domain is defined collectively by various other constructs
included in the field:

====================  ================================================
Domain construct      Description
====================  ================================================
Domain axis           Independent axes of the domain stored in
                      `cf.DomainAxis` objects

Dimension coordinate  Domain cell locations stored in
                      `cf.DimensionCoordinate` objects

Auxiliary coordinate  Domain cell locations stored in
                      `cf.AuxiliaryCoordinate` objects

Coordinate reference  Domain coordinate systems stored in
                      `cf.CoordinateReference` objects

Domain ancillary      Cell locations in alternative coordinate systems
                      stored in `cf.DomainAncillary` objects

Cell measure          Domain cell size or shape stored in
                      `cf.CellMeasure` objects
====================  ================================================

All of the constructs contained by the field construct are optional.

The field construct also has optional properties to describe aspects
of the data that are independent of the domain. These correspond to
some netCDF attributes of variables (e.g. units, long_name and
standard_name), and some netCDF global file attributes (e.g. history
and institution).

**Miscellaneous**

Field objects are picklable.

    '''

    _special_properties = Variable._special_properties.union(        
        ('cell_methods',
         'flag_values',
         'flag_masks',
         'flag_meanings')
         )
    
    def __init__(self, properties={}, attributes={}, data=None,
                 flags=None, field_anc=None, dim=None, aux=None,
                 measure=None, ref=None, domain_anc=None,
                 auto_cyclic=True, source=None, copy=True):
        '''**Initialization**

:Parameters:

    properties: `dict`, optional
        Provide the new field with CF properties from the dictionary's
        key/value pairs.

    data: `cf.Data`, optional
        Provide the new field with a data array.

    attributes: `dict`, optional
        Provide the new field with attributes from the dictionary's
        key/value pairs.

    flags: `cf.Flags`, optional
        Provide the new field with self-describing flag values.

    axes: sequence of `str`, optional
        A list of domain axis identifiers (``'dimN'``), stating the
        axes, in order, of the field's data array. By default these
        axis identifiers will be the sequence of consecutive axis
        identifiers ``'dim0'`` up to ``'dimM'``, where ``M`` is the
        number of axes of the data array, or an empty sequence if the
        data array is a scalar.

        If an axis of the data array already exists in the domain then
        the it must have the same size as the domain axis. If it does
        not exist in the domain then a new axis will be created.

        By default the axes will either be those defined for the data
        array by the domain or, if these do not exist, the domain axis
        identifiers whose sizes unambiguously match the data array.

    auto_cyclic: `bool`, optional
        If False then do not auto-detect cyclic axes. By default
        cyclic axes are auto-detected with the `autocyclic` method.

    copy: `bool`, optional
        If False then do not deep copy arguments prior to
        initialization. By default arguments are deep copied.

        '''

        if source is not None:
            if data is None:
                data = Data.asdata(source)

            if isinstance(source, Variable):
                p = source.properties()
                if properties:
                    p.update(properties)
                properties = p

                a = source.attributes()
                if attributes:
                    a.update(attributes) 
                attributes = a
        #--- End: if
        
        # Initialize the new field with attributes and CF properties
        super(Field, self).__init__(properties=properties,
                                    attributes=attributes,
                                    copy=copy) 

        # 
        self._unlimited = None

        # Domain axes and items
        self._private['special_attributes']['items'] = Items()

        if source is not None and isinstance(source, Field):
            # Initialise items and axes from an input source
#            self.Items = source.Items.copy(shallow=not copy)
            self._private['special_attributes']['items'] = source.Items.copy(shallow=not copy)

        # Dimension coordinates. Do these first, as they create new
        # axes.
        if dim:
            for item in dim:
                self.insert_dim(item, copy=copy)

        # Auxiliary coordinates
        if aux:
            for item in aux:
                self.insert_aux(item, copy=copy)

        # Domain ancillary variables
        if domain_anc:
            for item in domain_anc:
                self.insert_domain_anc(item, copy=copy)

        # Cell measures
        if measure:
            for item in measure:
                self.insert_measure(item, copy=copy)

        # Field ancillary variables
        if field_anc:
            for item in field_anc:
                self.insert_field_anc(item, copy=copy)

        # Coordinate references
        if ref:
            for item in ref:
                self.insert_ref(item, copy=copy)

        # Data array
        if data is not None:
            self.insert_data(data, copy=copy)

        # Flags
        if flags is not None:
            if not copy:
                self.Flags = flags
            else:
                self.Flags = flags.copy()
        #--- End: if

        # Cyclic axes
        if auto_cyclic:
            self.autocyclic()
    #--- End: def

#1.x     def __getitem__(self, index):
#1.x         '''
#1.x 
#1.x Called to implement evaluation of f[index].
#1.x 
#1.x f.__getitem__(index) <==> f[index]
#1.x 
#1.x The field is treated as if it were a single element field list
#1.x containing itself, i.e. ``f[index]`` is equivalent to
#1.x ``cf.FieldList(f)[index]``.
#1.x 
#1.x :Examples 1:
#1.x 
#1.x >>> g = f[0]
#1.x >>> g = f[:1]
#1.x >>> g = f[1:]
#1.x 
#1.x :Returns:
#1.x 
#1.x     out: `cf.Field` or `cf.FieldList`
#1.x         If *index* is the integer 0 or -1 then the field itself is
#1.x         returned. If *index* is a slice then a field list is returned
#1.x         which is either empty or else contains a single element of the
#1.x         field itself.
#1.x           
#1.x .. seealso:: `cf.FieldList.__getitem__`, `subspace`
#1.x 
#1.x :Examples 2:
#1.x 
#1.x >>> f[0] is f[-1] is f
#1.x True
#1.x >>> f[0:1].equals(cf.FieldList(f))   
#1.x True
#1.x >>> f[0:1][0] is f
#1.x True
#1.x >>> f[1:].equals(cf.FieldList())
#1.x True
#1.x >>> f[1:]       
#1.x []
#1.x >>> f[-1::3][0] is f
#1.x True
#1.x 
#1.x '''
#1.x         return FieldList((self,))[index]
#1.x     #--- End: def
    
    def __getitem__(self, indices):
        '''f.__getitem__(indices) <==> f[indices]

Return a subspace of the field defined by index values

Subspacing by axis indices uses an extended Python slicing syntax,
which is similar to :ref:`numpy array indexing
<numpy:arrays.indexing>`. There are extensions to the numpy indexing
functionality:

* Size 1 axes are never removed.

  An integer index *i* takes the *i*-th element but does not reduce
  the rank of the output array by one:

  >>> f.shape
  (12, 73, 96)
  >>> f[0].shape
  (1, 73, 96)
  >>> f[3, slice(10, 0, -2), 95:93:-1].shape
  (1, 5, 2)

* The indices for each axis work independently.

  When more than one axis's slice is a 1-d boolean sequence or 1-d
  sequence of integers, then these indices work independently along
  each axis (similar to the way vector subscripts work in Fortran),
  rather than by their elements:

  >>> f.shape
  (12, 73, 96)
  >>> f[:, [0, 72], [5, 4, 3]].shape
  (12, 2, 3)

  Note that the indices of the last example would raise an error when
  given to a numpy array.

* Boolean indices may be any object which exposes the numpy array
  interface, such as the field's coordinate objects:

  >>> f[:, f.coord('latitude')<0].shape
  (12, 36, 96)

.. seealso `subspace`

>>> f.shape
(12, 73, 96)
>>> f[...].shape
(12, 73, 96)
>>> f[slice(0, 12), :, 10:0:-2].shape
(12, 73, 5)
>>> f[..., f.coord('longitude')<180].shape
(12, 73, 48)

.. versionadded:: 2.0

:Examples 1:

>>> g = f[..., 0, :6, 9:1:-2, [1, 3, 4]]

:Returns:

    out: `cf.{+Variable}`

        '''
        if _debug:
            print self.__class__.__name__+'.__getitem__'
            print '    input indices =', indices
            
        if indices is Ellipsis:
            return self.copy()

        data  = self.Data
        shape = data.shape

        # Parse the index
        if not isinstance(indices, tuple):
            indices = (indices,)

        if isinstance(indices[0], basestring) and indices[0] == 'mask':
            auxiliary_mask = indices[:2]
            indices2       = indices[2:]
        else:
            auxiliary_mask = None
            indices2       = indices

#        print indices2
        indices, roll = parse_indices(shape, indices2, cyclic=True)
#        print indices, roll

        if roll:
            new = self
            axes = data._axes
            cyclic_axes = data._cyclic
            for iaxis, shift in roll.iteritems():
                if axes[iaxis] not in cyclic_axes:
                    raise IndexError(
"Can't take a cyclic slice from non-cyclic {!r} axis".format(self.axis_name(iaxis)))

                if _debug:
                    print '    roll, iaxis, shift =',  roll. iaxis, shift

                new = new.roll(iaxis, shift)
            #--- End: for
        else:            
            new = self.copy(_omit_Data=True)

        # ------------------------------------------------------------
        # Subspace the field's data
        # ------------------------------------------------------------
        if auxiliary_mask:
            auxiliary_mask = list(auxiliary_mask)
            findices = auxiliary_mask + indices
        else:
            findices = indices

        if _debug:
            print '    shape    =', shape
            print '    indices  =', indices
            print '    indices2 =', indices2
            print '    findices =', findices

        if roll:
            new.Data = new.Data[tuple(findices)]
        else:
            new.Data = self.Data[tuple(findices)]

        # ------------------------------------------------------------
        # Subspace items
        # ------------------------------------------------------------
        Items = new.Items
        data_axes = new.data_axes()

        items = new.items(role=('d', 'a', 'm', 'f', 'c'), axes=data_axes)
        for key, item in items.iteritems():
            item_axes = new.item_axes(key)
            dice = []
            for axis in item_axes:
                if axis in data_axes:
                    dice.append(indices[data_axes.index(axis)])
                else:
                    dice.append(slice(None))
            #--- End: for

            # Generally we do not apply an auxiliary mask to the
            # metadata items, but for DSGs we do.
            if auxiliary_mask and new.DSG:
                item_mask = []
                for mask in auxiliary_mask[1]:                    
                    iaxes = [data_axes.index(axis) for axis in item_axes if axis in data_axes]
                    for i, (axis, size) in enumerate(zip(data_axes, mask.shape)):
                        if axis not in item_axes:
                            if size > 1:
                                iaxes = None
                                break

                            mask = mask.squeeze(i)
                    #--- End: for
                    
                    if iaxes is None:
                        item_mask = None
                        break
                    else:
                        mask1 = mask.transpose(iaxes)
                        for i, axis in enumerate(item_axes):
                            if axis not in data_axes:
                                mask1.expand_dims(i)
                        #--- End: for
                        item_mask.append(mask1)
                #--- End: for                
                if item_mask:
                    dice = [auxiliary_mask[0], item_mask] + dice
            #--- End: if
            
            if _debug:
                print '    item:', repr(item)
                print '    dice = ', dice
                
            # Replace existing item with its subspace
            Items[key] = item[tuple(dice)]
        #--- End: for

        # Replace existing domain axes
        Axes = new._Axes
        for axis, size in izip(data_axes, new.shape):
            Axes[axis] = DomainAxis(size, Axes[axis].ncdim)
            
        return new
    #--- End: def

    def __setitem__(self, indices, value):
        '''

Called to implement assignment to x[indices]=value

x.__setitem__(indices, value) <==> x[indices]=value

.. versionadded:: 2.0

'''
        if isinstance(value, self.__class__):
           value = self._conform_for_assignment(value)
           value = value.Data

        elif numpy_size(value) != 1:
            raise ValueError(
                "Can't assign a size %d %r to a %s data array" %
                (numpy_size(value), value.__class__.__name__,
                 self.__class__.__name__))

        elif isinstance(value, Variable):
            value = value.Data

        self.Data[indices] = value
    #--- End: def

    def analyse_items(self, relaxed_identities=None):
        '''
Analyse a domain.

:Returns:

    out: `dict`
        A description of the domain.

:Examples:

>>> print f
Axes           : time(3) = [1979-05-01 12:00:00, ..., 1979-05-03 12:00:00] gregorian
               : air_pressure(5) = [850.000061035, ..., 50.0000038147] hPa
               : grid_longitude(106) = [-20.5400109887, ..., 25.6599887609] degrees
               : grid_latitude(110) = [23.3200002313, ..., -24.6399995089] degrees
Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.1246607722, ..., 22.8886948065]] degrees_N
               : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98136251, ..., 35.2925499052]] degrees_E
Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>

>>> f.analyse_items()
{
 'dim_coords': {'dim0': <CF Dim ....>,

 'aux_coords': {'N-d': {'aux0': <CF AuxiliaryCoordinate: latitude(110, 106) degrees_N>,
                        'aux1': <CF AuxiliaryCoordinate: longitude(110, 106) degrees_E>},
                'dim0': {'1-d': {},
                         'N-d': {}},
                'dim1': {'1-d': {},
                         'N-d': {}},
                'dim2': {'1-d': {},
                         'N-d': {'aux0': <CF AuxiliaryCoordinate: latitude(110, 106) degrees_N>,
                                 'aux1': <CF AuxiliaryCoordinate: longitude(110, 106) degrees_E>}},
                'dim3': {'1-d': {},
                         'N-d': {'aux0': <CF AuxiliaryCoordinate: latitude(110, 106) degrees_N>,
                                 'aux1': <CF AuxiliaryCoordinate: longitude(110, 106) degrees_E>}}},
 'axis_to_coord': {'dim0': <CF DimensionCoordinate: time(3) gregorian>,
                   'dim1': <CF DimensionCoordinate: air_pressure(5) hPa>,
                   'dim2': <CF DimensionCoordinate: grid_latitude(110) degrees>,
                   'dim3': <CF DimensionCoordinate: grid_longitude(106) degrees>},
 'axis_to_id': {'dim0': 'time',
                'dim1': 'air_pressure',
                'dim2': 'grid_latitude',
                'dim3': 'grid_longitude'},
 'cell_measures': {'N-d': {},
                   'dim0': {'1-d': {},
                            'N-d': {}},
                   'dim1': {'1-d': {},
                            'N-d': {}},
                   'dim2': {'1-d': {},
                            'N-d': {}},
                   'dim3': {'1-d': {},
                            'N-d': {}}},
 'id_to_aux': {},
 'id_to_axis': {'air_pressure': 'dim1',
                'grid_latitude': 'dim2',
                'grid_longitude': 'dim3',
                'time': 'dim0'},
 'id_to_coord': {'air_pressure': <CF DimensionCoordinate: air_pressure(5) hPa>,
                 'grid_latitude': <CF DimensionCoordinate: grid_latitude(110) degrees>,
                 'grid_longitude': <CF DimensionCoordinate: grid_longitude(106) degrees>,
                 'time': <CF DimensionCoordinate: time(3) gregorian>},
 'id_to_key': {'air_pressure': 'dim1',
               'grid_latitude': 'dim2',
               'grid_longitude': 'dim3',
               'time': 'dim0'},
 'undefined_axes': [],
 'warnings': [],
}

'''
        a = {}

        # ------------------------------------------------------------
        # Map each axis identity to its identifier, if such a mapping
        # exists.
        #
        # For example:
        # >>> id_to_axis
        # {'time': 'dim0', 'height': dim1'}
        # ------------------------------------------------------------
        id_to_axis = {}

        # ------------------------------------------------------------
        # For each dimension that is identified by a 1-d auxiliary
        # coordinate, map its dimension's its identifier.
        #
        # For example:
        # >>> id_to_aux
        # {'region': 'aux0'}
        # ------------------------------------------------------------
        id_to_aux = {}

        # ------------------------------------------------------------
        # The keys of the coordinate items which provide axis
        # identities
        #
        # For example:
        # >>> id_to_key
        # {'region': 'aux0'}
        # ------------------------------------------------------------
#        id_to_key = {}

        axis_to_id = {}

        # ------------------------------------------------------------
        # Map each dimension's identity to the coordinate which
        # provides that identity.
        #
        # For example:
        # >>> id_to_coord
        # {'time': <CF Coordinate: time(12)>}
        # ------------------------------------------------------------
        id_to_coord = {}

        axis_to_coord = {}

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
#        aux_coords = {}
#        aux_coords['N-d'] = {}

#        cell_measures = {}
#        cell_measures['N-d'] = {}

#        field_ancillaries  = {}
#        domain_ancillaries = {}

#        coord_to_refs = {}

#        dim_coords = {}

        # ------------------------------------------------------------
        # List the dimensions which are undefined, in that no unique
        # identity can be assigned to them.
        #
        # For example:
        # >>> undefined_axes
        # ['dim2']
        # ------------------------------------------------------------
        undefined_axes = []

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        warnings = []
        id_to_dim = {}
        axis_to_aux = {}

        if relaxed_identities is None:
            relaxed_identities = RELAXED_IDENTITIES()
       
        for axis in self.axes():

#            # Find this axis's 1-d and N-d auxiliary coordinates
#            aux_coords[axis]        = {}
#            aux_coords[axis]['1-d'] = {}
#            aux_coords[axis]['N-d'] = {}
#            for aux, coord in self.items(role='a', axes=axis).iteritems():
#                if coord.ndim > 1:
#                    aux_coords['N-d'][aux] = coord
#                    aux_coords[axis]['N-d'][aux] = coord
#                else:
#                    aux_coords[axis]['1-d'][aux] = coord
            #--- End: for

#            # Find this axis's 1-d and N-d cell measures
#            cell_measures[axis]        = {}
#            cell_measures[axis]['1-d'] = {}
#            cell_measures[axis]['N-d'] = {}
#            for msr, cell_measure in self.items(role='m', axes=axis).iteritems():
#                if cell_measure.ndim > 1:
#                    cell_measures['N-d'][msr]       = cell_measure
#                    cell_measures[axis]['N-d'][msr] = cell_measure
#                else:
#                    cell_measures[axis]['1-d'][msr] = cell_measure
            #--- End: for            
            axis_to_dim = {}
 #           # Find this axis's field ancillaries
 #           field_ancillaries[axis] = {}
 #           for key, anc in self.items(role='f', axes=axis).iteritems():
 #               field_ancillary[axis][key] = anc
# 
#            # Find this axis's domain ancillaries
#            domain_ancillaries[axis] = {}
#            for key, anc in self.items(role='c', axes=axis).iteritems():
#                domain_ancillary[axis][key] = anc

            if axis in self.Items.d:
                # This axis of the domain has a dimension coordinate
                dim = self.Items[axis]

                identity = dim.identity(relaxed_identity=relaxed_identities)
                if identity is None:
                    # Dimension coordinate has no identity, but it may
                    # have a recognised axis.
                    for ctype in ('T', 'X', 'Y', 'Z'):
                        if getattr(dim, ctype):
                            identity = ctype
                            break
                #--- End: if

                if identity is not None and dim._hasData:
                    if identity in id_to_axis:
                        warnings.append(
                            "Field has multiple {!r} axes".format(identity))

                    axis_to_id[axis]      = identity
                    id_to_axis[identity]  = axis
                    axis_to_coord[axis]   = axis
                    id_to_coord[identity] = axis
                    axis_to_dim[axis]     = axis
                    id_to_dim[identity]   = axis
                    continue

            else:
                auxs = self.Items(role='a', ndim=1)
                if len(auxs) == 1:                
                    # This axis of the domain does not have a
                    # dimension coordinate but it does have exactly
                    # one 1-d auxiliary coordinate, so that will do.
                    key, aux = auxs.popitem()
                    identity = aux.identity(relaxed_identity=relaxed_identities)
                    if identity is not None and aux._hasData:
                        if identity in id_to_axis:
                            warnings.append(
                                "Field has multiple {!r} axes".format(identity))

                        axis_to_id[axis]      = identity
                        id_to_axis[identity]  = axis
                        axis_to_coord[axis]   = key
                        id_to_coord[identity] = key
                        axis_to_aux[axis]     = key
                        id_to_aux[identity]   = key
                        continue
            #--- End: if

#            for key, ref in self.Items.refs().iteritems():
#                for coord in ref.coordinates:
#                    coord_to_refs.set_default(coord, []).append(key)

            # Still here? Then this axis is undefined
            undefined_axes.append(axis)
        #--- End: for

        return {
                'axis_to_id'    : axis_to_id,
                'id_to_axis'    : id_to_axis,
                'axis_to_coord' : axis_to_coord,
                'axis_to_dim'   : axis_to_dim,
                'axis_to_aux'   : axis_to_aux,
                'id_to_coord'   : id_to_coord,
                'id_to_dim'     : id_to_dim,
                'id_to_aux'     : id_to_aux,
                'undefined_axes': undefined_axes,
                'warnings'      : warnings,                
                }    
    #--- End def 

#    def broadcastable(self, g, relaxed_identities=None):
#        '''
#'''
#        # ------------------------------------------------------------
#        # Analyse each domain
#        # ------------------------------------------------------------
#        if relaxed_identities is None:
#            relaxed_identities = RELAXED_IDENTITIES()
#
#        s = self.analyse_items(relaxed_identities=relaxed_identities)
#        v = g.analyse_items(relaxed_identities=relaxed_identities)
#
#        if s['warnings'] or v['warnings']:
#            return False
#
#        matching_size_gt1_ids = []
#        for x, coord0 in s['id_to_coord']:
#            size0 = coord0.size
#            if size0 == 1:
#                continue
#            
#            if x in v['id_to_coord']:
#                coord1 = v['id_to_coord']['x']
#                size1 = coord1.size
#                if size1 == 1:
#                    continue
#                if size0 != size1:
#                    return False
#
#                matching_size_gt1_ids.append(x)
#        #--- End: for                    
#
#        for x, coord1 in v['id_to_coord']:
#            if x in matching_size_gt1_ids:
#                continue
#            
#            size1 = coord1.size
#            if size1 == 1:
#                continue
#            
#            if x in s['id_to_coord']:
#                coord0 = s['id_to_coord']['x']
#                size0 = coord0.size
#                if size0 == 1:
#                    continue
#                if size0 != size1:
#                    return False
#
#                matching_size_gt1_ids.append(x)
#        #--- End: for                    
#
#        # Check that at most one field has undefined axes
#        if s['undefined_axes'] and v['undefined_axes']:
#            raise ValueError(
#"Can't combine fields: Both fields have undefined axes: {0}, {1}".format(
#    tuple(self.axis_name(a) for a in s['undefined_axes']),
#    tuple(other.axis_name(a) for a in v['undefined_axes'])))
#
#        # Find the axis names which are present in both fields
#        matching_ids = set(s['id_to_axis']).intersection(v['id_to_axis'])
#        
#        # Check that any matching axes defined by an auxiliary
#        # coordinate are done so in both fields.
#        for identity in set(s['id_to_aux']).symmetric_difference(v['id_to_aux']):
#            if identity in matching_ids:
#                raise ValueError(
#"Can't combine fields: Incompatible {!r} axes (identified by auxiliary coordinates in only one field)".format(
#    standard_name)) ########~WRONG
#        #--- End: for
#
#
#        #-------------------------------------------------------------
#        #
#        #-------------------------------------------------------------
#        for identity in matching_size_gt1_ids:
#            coord0 = s['id_to_coord'][identity]  ## FIX
#            coord1 = v['id_to_coord'][identity]   ## FIX
#
#            # Check that the 'defining coordinate' data arrays are
#            # compatible
#            if not coord0._equivalent_data(coord1):
#                # Can't broadcast: The 'defining coordinates' have
#                # unequivalent data arrays and are both size > 1.
#                return False
#
#            # Still here? Then the 'defining coordinates' have
#            # equivalent data arrays
#
#            # If the 'defining coordinates' are attached to coordinate
#            # references then check that those coordinate references
#            # are equivalent
#            key0 = s['id_to_coord'][identity]                
#            key1 = v['id_to_coord'][identity]
#
#            equivalent_refs = True
#            for ref0 in self.refs().itervalues():
#                if key0 not in ref0.coords:
#                    continue
#
#                equivalent_refs = False
#                for ref1 in g.refs().itervalues():
#                    if key1 not in ref1.coords:
#                        continue
#
#                    # Each defining coordinate is referenced by a
#                    # coordinate reference ...
#                    if self.domain.equivalent_refs(ref0,
#                                                   ref1,
#                                                   g.domain):
#                        # ... and those coordinate references are equivalent
#                        equivalent_refs = True
#                    #--- End: if
#
#                    break
#                #--- End: for
#
#                break
#            #--- End: for
#
#            if not equivalent_refs:
#                # Can't broadcast: Defining coordinates have
#                # incompatible coordinate references are and are both size >
#                # 1.
#                return False
#        #--- End: for
#
#        # --------------------------------------------------------
#        # Still here? Then the two fields are broadcastable!
#        # --------------------------------------------------------
#        return True
#    #--- End: def

    def _no_None_dict(self, d):
        '''
        '''
        return dict((key, value) for key, value in d.iteritems() if value is not None)
    #--- End: def

    def _binary_operation(self, other, method):
        '''

Implement binary arithmetic and comparison operations on the master
data array with metadata-aware broadcasting.

It is intended to be called by the binary arithmetic and comparison
methods, such as `__sub__`, `__imul__`, `__rdiv__`, `__lt__`, etc.

:Parameters:

    other: standard Python scalar object, `cf.Field` or `cf.Query` or `cf.Data`

    method: `str`
        The binary arithmetic or comparison method name (such as
        ``'__idiv__'`` or ``'__ge__'``).

:Returns:

    out: `cf.Field`
        The new field, or the same field if the operation was an in
        place augmented arithmetic assignment.

:Examples:

>>> h = f._binary_operation(g, '__add__')
>>> h = f._binary_operation(g, '__ge__')
>>> f._binary_operation(g, '__isub__')
>>> f._binary_operation(g, '__rdiv__')

'''
        _debug = False

        if IGNORE_IDENTITIES():
            inplace = method[2] == 'i'
            data = self.Data._binary_operation(other, method)
            if self.shape != data.shape:
                pass
        
            if inplace:
                out = self
            else:
                out = self.copy()

            out.Data = data

            return out
        #--- End: if

        if (isinstance(other, (float, int, long, bool, basestring)) or
            other is self):
            # ========================================================
            # CASE 1a: No changes are to the field's items are
            #          required so can use the metadata-unaware
            #          Variable._binary_operation method.
            # ========================================================
            return super(Field, self)._binary_operation(other, method)

        if isinstance(other, Data) and other.size == 1:
            # ========================================================
            # CASE 1b: No changes are to the field's items are
            #          required so can use the metadata-unaware
            #          Variable._binary_operation method.
            # ========================================================
            if other.ndim > 0:
                other = other.squeeze()

            return super(Field, self)._binary_operation(other, method)
        #--- End: if

        if isinstance(other, Query):
            # ========================================================
            # CASE 2: Combine the field with a cf.Query object
            # ========================================================
            return NotImplemented

#        if isinstance(other, FieldList):
#            # ========================================================
#            # CASE 3: Combine the field with a cf.FieldList object
#            # ========================================================
#            return NotImplemented
#        #--- End: if

        if not isinstance(other, self.__class__):
            raise ValueError(
                "Can't combine {!r} with {!r}".format(
                    self.__class__.__name__, other.__class__.__name__))


        # ============================================================
        # Still here? Then combine the field with another field
        # ============================================================

        # ------------------------------------------------------------
        # Analyse each domain
        # ------------------------------------------------------------
        relaxed_identities = RELAXED_IDENTITIES()
        s = self.analyse_items(relaxed_identities=relaxed_identities)
        v = other.analyse_items(relaxed_identities=relaxed_identities)

        if _debug:
            print s
            print
            print v

        if s['warnings'] or v['warnings']:
            raise ValueError(
"Can't combine fields: {}".format(s['warnings'] or v['warnings']))
            
        # Check that at most one field has undefined axes
        if s['undefined_axes'] and v['undefined_axes']:
            raise ValueError(
"Can't combine fields: Both fields have undefined axes: {0}, {1}".format(
    tuple(self.axis_name(a) for a in s['undefined_axes']),
    tuple(other.axis_name(a) for a in v['undefined_axes'])))

        # Find the axis names which are present in both fields
        matching_ids = set(s['id_to_axis']).intersection(v['id_to_axis'])
        if _debug:
            print "s['id_to_axis'] =", s['id_to_axis']
            print "v['id_to_axis'] =", v['id_to_axis']
            print 'matching_ids    =', matching_ids
        
        # Check that any matching axes defined by an auxiliary
        # coordinate are done so in both fields.
        for identity in set(s['id_to_aux']).symmetric_difference(v['id_to_aux']):
            if identity in matching_ids:
                raise ValueError(
"Can't combine fields: {!r} axis defined by auxiliary in only 1 field".format(
    standard_name)) ########~WRONG
        #--- End: for

        # ------------------------------------------------------------
        # For matching dimension coordinates check that they have
        # consistent coordinate references and that one of the following is
        # true:
        #
        # 1) They have equal size > 1 and their data arrays are
        #    equivalent
        #
        # 2) They have unequal sizes and one of them has size 1
        #
        # 3) They have equal size = 1. In this case, if the data
        #    arrays are not equivalent then the axis will be omitted
        #    from the result field.
        #-------------------------------------------------------------

        # List of size 1 axes to be completely removed from the result
        # field. Such an axis's size 1 defining coordinates have
        # unequivalent data arrays.
        #
        # For example:
        # >>> remove_size1_axes0
        # ['dim2']
        remove_size1_axes0 = []

        # List of matching axes with equivalent defining dimension
        # coordinate data arrays.
        #
        # Note that we don't need to include matching axes with
        # equivalent defining *auxiliary* coordinate data arrays.
        #
        # For example:
        # >>> 
        # [('dim2', 'dim0')]
        matching_axes_with_equivalent_data = {}

        # For each field, list those of its matching axes which need
        # to be broadcast against the other field. I.e. those axes
        # which are size 1 but size > 1 in the other field.
        #
        # For example:
        # >>> s['size1_broadcast_axes']
        # ['dim1']
        s['size1_broadcast_axes'] = []
        v['size1_broadcast_axes'] = []

#DO SOMETING WITH v['size1_broadcast_axes'] to be symmetrial with regards coord refs!!!!!
        
        # Map axes in field1 to axes in field0 and vice versa
        #
        # For example:
        # >>> axis1_to_axis0
        # {'dim1': 'dim0', 'dim2': 'dim1', 'dim0': 'dim2'}
        # >>> axis0_to_axis1
        # {'dim0': 'dim1', 'dim1': 'dim2', 'dim2': 'dim0'}
        axis1_to_axis0 = {}
        axis0_to_axis1 = {}

        remove_items = set()
        
        for identity in matching_ids:
            axis0  = s['id_to_axis'][identity]
            axis1  = v['id_to_axis'][identity]

            axis1_to_axis0[axis1] = axis0
            axis0_to_axis1[axis0] = axis1

            key0 = s['id_to_coord'][identity]
            key1 = v['id_to_coord'][identity]

            coord0 = self.Items[key0]
            coord1 = other.Items[key1]

            # Check the sizes of the defining coordinates
            size0 = coord0.size
            size1 = coord1.size
            if size0 != size1:
                # Defining coordinates have different sizes
                if size0 == 1:
                    # Broadcast
                    s['size1_broadcast_axes'].append(axis0)
                elif size1 == 1:
                    # Broadcast
                    v['size1_broadcast_axes'].append(axis1)
                else:
                    # Can't broadcast
                    raise ValueError(
"Can't combine fields: Can't broadcast {!r} axes with sizes {} and {}".format(
    identity, size0, size1))

                # Move on to the next identity if the defining
                # coordinates have different sizes
                continue
            #--- End: if

            # Still here? Then the defining coordinates have the same
            # size.

            # Check that equally sized defining coordinate data arrays
            # are compatible
            if coord0._equivalent_data(coord1, traceback=_debug):
                # The defining coordinates have equivalent data
                # arrays
            
                # If the defining coordinates are attached to
                # coordinate references then check that those
                # coordinate references are equivalent

                # For each field, find the coordinate references which
                # contain the defining coordinate.
                refs0 = [ref for ref in self.Items.refs().itervalues()
                         if key0 in ref.coordinates]
                refs1 = [ref for ref in other.Items.refs().itervalues()
                         if key1 in ref.coordinates]

                nrefs = len(refs0)
                if nrefs > 1 or nrefs != len(refs1):
                    # The defining coordinate are associated with
                    # different numbers of coordinate references
                    equivalent_refs = False
                elif not nrefs:
                    # Neither defining coordinate is associated with a
                    # coordinate reference                    
                    equivalent_refs = True
                else:  
                    # Each defining coordinate is associated with
                    # exactly one coordinate reference
                    equivalent_refs = self._equivalent_refs(refs0[0], refs1[0],
                                                            other, s=s, t=v,
                                                            traceback=_debug)

                if not equivalent_refs:
                    # The defining coordinates have non-equivalent
                    # coordinate references
                    if coord0.size == 1:
                        # The defining coordinates have non-equivalent
                        # coordinate references but both defining
                        # coordinates are of size 1 => flag this axis
                        # to be omitted from the result field.
#dch                        remove_size1_axes0.append(axis0)
                        remove_items.add(refs0[0])
                        remove_items.update(refs0[0].ancillaries.values())
                    else:
                        # The defining coordinates have non-equivalent
                        # coordinate references and they are of size >
                        # 1 
                        raise ValueError(
"Can't combine fields: Incompatible coordinate references for {!r} coordinates".format(
    identity))

                elif identity not in s['id_to_aux']:
                    # The defining coordinates are both dimension
                    # coordinates, have equivalent data arrays and
                    # have equivalent coordinate references.
                    matching_axes_with_equivalent_data[axis0] = axis1
                else:
                    # The defining coordinates are both auxiliary
                    # coordinates, have equivalent data arrays and
                    # have equivalent coordinate references.
                    pass

            else:
                print repr(coord0), repr(coord1)
                if coord0.size > 1:
                    # The defining coordinates have non-equivalent
                    # data arrays and are both of size > 1
                    raise ValueError(
"Can't combine fields: Incompatible {!r} coordinate values: {}, {}".format(
    identity, coord0.data, coord1.data))
                else:
                    # The defining coordinates have non-equivalent
                    # data arrays and are both size 1 => this axis to
                    # be omitted from the result field
                    remove_size1_axes0.append(axis0)
        #--- End: for
        if _debug:
            print "1: s['size1_broadcast_axes'] =", s['size1_broadcast_axes']
            print "1: v['size1_broadcast_axes'] =", v['size1_broadcast_axes']
            print '1: remove_size1_axes0 =', remove_size1_axes0

        matching_axis1_to_axis0 = axis1_to_axis0.copy()
        matching_axis0_to_axis1 = axis0_to_axis1.copy()

        # ------------------------------------------------------------
        # Still here? Then the two fields are combinable!
        # ------------------------------------------------------------

        # ------------------------------------------------------------
        # 2.1 Create copies of the two fields, unless it is an in
        #     place combination, in which case we don't want to copy
        #     self)
        # ------------------------------------------------------------
        field1 = other.copy()

        inplace = method[2] == 'i'
        if not inplace:
            field0 = self.copy()
        else:
            field0 = self

        s['new_size1_axes'] = []
            
        # ------------------------------------------------------------
        # Permute the axes of the data array of field0 so that:
        #
        # * All of the matching axes are the inner (fastest varying)
        #   axes
        #
        # * All of the undefined axes are the outer (slowest varying)
        #   axes
        #
        # * All of the defined but unmatched axes are in the middle
        # ------------------------------------------------------------
        data_axes0 = field0.data_axes()
        axes_unD = []                     # Undefined axes
        axes_unM = []                     # Defined but unmatched axes
        axes0_M  = []                     # Defined and matched axes
        for axis0 in data_axes0:
            if axis0 in axis0_to_axis1:
                # Matching axis                
                axes0_M.append(axis0)
            elif axis0 in s['undefined_axes']:
                # Undefined axis
                axes_unD.append(axis0)
            else:
                # Defined but unmatched axis
                axes_unM.append(axis0)
        #--- End: for
        if _debug:
            print '2: axes_unD, axes_unM , axes0_M =', axes_unD , axes_unM , axes0_M

        field0.transpose(axes_unD + axes_unM + axes0_M, i=True)

        end_of_undefined0   = len(axes_unD)
        start_of_unmatched0 = end_of_undefined0
        start_of_matched0   = start_of_unmatched0 + len(axes_unM)
        if _debug: 
            print '2: end_of_undefined0   =', end_of_undefined0   
            print '2: start_of_unmatched0 =', start_of_unmatched0 
            print '2: start_of_matched0   =', start_of_matched0  

        # ------------------------------------------------------------
        # Permute the axes of the data array of field1 so that:
        #
        # * All of the matching axes are the inner (fastest varying)
        #   axes and in corresponding positions to data0
        #
        # * All of the undefined axes are the outer (slowest varying)
        #   axes
        #
        # * All of the defined but unmatched axes are in the middle
        # ------------------------------------------------------------
        data_axes1 = field1.data_axes()
        axes_unD = []
        axes_unM = []
        axes1_M  = [axis0_to_axis1[axis0] for axis0 in axes0_M]
        for  axis1 in data_axes1:          
            if axis1 in axes1_M:
                pass
            elif axis1 in axis1_to_axis0:
                # Matching axis
                axes_unM.append(axis1)
            elif axis1 in v['undefined_axes']:
                # Undefined axis
                axes_unD.append(axis1) 
            else:
                # Defined but unmatched axis
                axes_unM.append(axis1)
        #--- End: for
        if _debug:
            print '2: axes_unD , axes_unM , axes0_M =',axes_unD , axes_unM , axes0_M

        field1.transpose(axes_unD + axes_unM + axes1_M, i=True)

        start_of_unmatched1 = len(axes_unD)
        start_of_matched1   = start_of_unmatched1 + len(axes_unM)
        undefined_indices1  = slice(None, start_of_unmatched1)
        unmatched_indices1  = slice(start_of_unmatched1, start_of_matched1)
        if _debug: 
            print '2: start_of_unmatched1 =', start_of_unmatched1 
            print '2: start_of_matched1   =', start_of_matched1   
            print '2: undefined_indices1  =', undefined_indices1  
            print '2: unmatched_indices1  =', unmatched_indices1  

        # ------------------------------------------------------------
        # Make sure that each pair of matching axes run in the same
        # direction 
        #
        # Note that the axis0_to_axis1 dictionary currently only maps
        # matching axes
        # ------------------------------------------------------------
        if _debug:
            print '2: axis0_to_axis1 =',axis0_to_axis1

        for axis0, axis1 in axis0_to_axis1.iteritems():
            if field1.direction(axis1) != field0.direction(axis0):
                field1.flip(axis1, i=True)
        #--- End: for
    
        # ------------------------------------------------------------
        # 2f. Insert size 1 axes into the data array of field0 to
        #     correspond to defined but unmatched axes in field1
        #
        # For example, if   field0.Data is      1 3         T Y X
        #              and  field1.Data is          4 1 P Z   Y X
        #              then field0.Data becomes 1 3     1 1 T Y X
        # ------------------------------------------------------------
        unmatched_axes1 = data_axes1[unmatched_indices1]
        if _debug: 
            print '2: unmatched_axes1=', unmatched_axes1

        if unmatched_axes1:
            for axis1 in unmatched_axes1:
                field0.expand_dims(end_of_undefined0, i=True)
                if _debug: 
                    print '2: axis1, field0.shape =', axis1, field0.shape
                
                axis0 = set(field0.data_axes()).difference(data_axes0).pop()

                axis1_to_axis0[axis1] = axis0
                axis0_to_axis1[axis0] = axis1
                s['new_size1_axes'].append(axis0)

                start_of_unmatched0 += 1
                start_of_matched0   += 1 

                data_axes0 = field0.data_axes()
        #--- End: if

        # ------------------------------------------------------------
        # Insert size 1 axes into the data array of field1 to
        # correspond to defined but unmatched axes in field0
        #
        # For example, if   field0.Data is      1 3     1 1 T Y X
        #              and  field1.Data is          4 1 P Z   Y X 
        #              then field1.Data becomes     4 1 P Z 1 Y X 
        # ------------------------------------------------------------
        unmatched_axes0 = data_axes0[start_of_unmatched0:start_of_matched0]
        if _debug:
            print '2: unmatched_axes0 =', unmatched_axes0

        if unmatched_axes0:
            for axis0 in unmatched_axes0:
                field1.expand_dims(start_of_matched1, i=True)
                if _debug:
                    print '2: axis0, field1.shape =',axis0, field1.shape

                axis1 = set(field1.data_axes()).difference(data_axes1).pop()

                axis0_to_axis1[axis0] = axis1
                axis1_to_axis0[axis1] = axis0

                start_of_unmatched1 += 1

                data_axes1 = field1.data_axes()
            #--- End: for
         #--- End: if

        # ------------------------------------------------------------
        # Insert size 1 axes into the data array of field0 to
        # correspond to undefined axes (of any size) in field1
        #
        # For example, if   field0.Data is      1 3     1 1 T Y X
        #              and  field1.Data is          4 1 P Z 1 Y X 
        #              then field0.Data becomes 1 3 1 1 1 1 T Y X
        # ------------------------------------------------------------
        axes1 = data_axes1[undefined_indices1]
        if axes1:
            for axis1 in axes1:
                field0.expand_dims(end_of_undefined0, i=True)

                axis0 = set(field0.data_axes()).difference(data_axes0).pop()

                axis0_to_axis1[axis0] = axis1
                axis1_to_axis0[axis1] = axis0
                s['new_size1_axes'].append(axis0)

                data_axes0 = field0.data_axes()
            #--- End: for
        #--- End: if
        if _debug:
            print '2: axis0_to_axis1 =', axis0_to_axis1
            print '2: axis1_to_axis0 =', axis1_to_axis0
            print "2: s['new_size1_axes']  =", s['new_size1_axes']

        # ============================================================
        # 3. Combine the data objects
        #
        # Note that, by now, field0.ndim >= field1.ndim.
        # ============================================================
#dch        field0.Data = getattr(field0.Data, method)(field1.Data)
        if _debug:
            print '3: repr(field0) =', repr(field0)
            print '3: repr(field1) =', repr(field1)

        field0 = super(Field, field0)._binary_operation(field1, method)

        if _debug:
            print '3: field0.shape =', field0.shape
            print '3: repr(field0) =', repr(field0)

        # ============================================================
        # 4. Adjust the domain of field0 to accommodate its new data
        # ============================================================
        # Field 1 dimension coordinate to be inserted into field 0
        insert_dim        = {}
        # Field 1 auxiliary coordinate to be inserted into field 0
        insert_aux        = {}
        # Field 1 domain ancillaries to be inserted into field 0
        insert_domain_anc = {}
        # Field 1 coordinate references to be inserted into field 0
        insert_ref   = set()

        # ------------------------------------------------------------
        # 4a. Remove selected size 1 axes
        # ------------------------------------------------------------
        if _debug:
            print '4: field0.Items().keys() =', sorted(field0.Items().keys())
            print '4: field1.Items().keys() =', sorted(field1.Items().keys())

#AND HEREIN LIE TE PROBLEM            
        field0.remove_axes(remove_size1_axes0)

        # ------------------------------------------------------------
        # 4b. If broadcasting has grown any size 1 axes in field0
        #     then replace their size 1 coordinates with the
        #     corresponding size > 1 coordinates from field1.
        # ------------------------------------------------------------
        refs0 = field0.refs()
        refs1 = field1.refs()

        for axis0 in s['size1_broadcast_axes'] + s['new_size1_axes']:
            axis1 = axis0_to_axis1[axis0]
            field0._Axes[axis0] = field1._Axes[axis1]
            if _debug:
                print '4: field0 axes =',field0.axes()
                print '4: field1 axes =',field1.axes()

            # Copy field1 1-d coordinates for this axis to field0
            if axis1 in field1.Items.d:
                insert_dim[axis1] = [axis0]

            for key1 in field1.Items(role='a', axes_all=set((axis1,))):
                insert_aux[key1] = [axis0]

            # Copy field1 coordinate references which span this axis
            # to field0, along with all of their domain ancillaries
            # (even if those domain ancillaries do not span this
            # axis).
            for key1, ref1 in refs1.iteritems():
                if axis1 not in field1.Items.axes(key1):
                    continue
#                insert_ref.add(key1)
#                for identifier1 in ref1.ancillaries.values():
#                    key1 = field1.key(identifier1, exact=True, role='c')
#                    if key1 is not None:
#                        axes0 = [axis1_to_axis0[axis]ct2', 'dim1', 'dim2', 'fav0', 'fav1', 'fav2', 'fav3', 'msr0', 'ref1']
#5: field1.Items().keys() = ['aux0', 'aux1', 'aux2', 'c
#                                 for axis in field1.Items.axes(key1)]
#                        insert_domain_anc[key1] = axes0
            #--- End: for

            # Remove all field0 auxiliary coordinates and domain
            # ancillaries which span this axis
            remove_items.update(field0.Items(role='ac', axes=set((axis0,))))

            # Remove all field0 coordinate references which span this
            # axis, and their domain ancillaries (even if those domain
            # ancillaries do not span this axis).
            for key0 in refs0.keys():
                if axis0 in field0.Items.axes(key0):
                    remove_items.add(key0)
                    ref0 = refs0.pop(key0)
                    remove_items.update(field0.Items(ref0.ancillaries.values(), 
                                                     exact=True, role='c'))
            #--- End: for
        #--- End: for

        # ------------------------------------------------------------
        # Consolidate auxiliary coordinates for matching axes
        #
        # A field0 auxiliary coordinate is retained if:
        #
        # 1) it is the defining coordinate for its axis
        #
        # 2) there is a corresponding field1 auxiliary coordinate
        #    spanning the same axes which has the same identity and
        #    equivalent data array
        #
        # 3) there is a corresponding field1 auxiliary coordinate
        #    spanning the same axes which has the same identity and a
        #    size-1 data array.
        #-------------------------------------------------------------
        auxs1 = field1.auxs()
        if _debug:
            print '5: field0.auxs() =', field0.auxs()
            print '5: field1.auxs() =', auxs1
            print '5: remove_items =', remove_items

        for key0, aux0 in field0.auxs().iteritems():
            if key0 in remove_items:
                # Field0 auxiliary coordinate has already marked for
                # removal
                continue
            
            if key0 in s['id_to_aux'].values():
                # Field0 auxiliary coordinate has already been checked
                continue
            
            if aux0.identity() is None:
                # Auxiliary coordinate has no identity
                remove_items.add(key0)
                continue        

            axes0 = field0.item_axes(key0)
            if not set(axes0).issubset(matching_axis0_to_axis1):
                # Auxiliary coordinate spans at least on non-matching
                # axis
                remove_items.add(key0)
                continue
                
            found_equivalent_auxiliary_coordinates = False
            for key1, aux1 in auxs1.items():
                if key1 in v['id_to_aux'].values():
                    # Field1 auxiliary coordinate has already been checked
                    del auxs1[key1]
                    continue            

                if aux1.identity() is None:
                    # Field1 auxiliary coordinate has no identity
                    del auxs1[key1]
                    continue        

                axes1 = field1.item_axes(key0)
                if not set(axes1).issubset(matching_axis1_to_axis0):
                    # Field 1 auxiliary coordinate spans at least one
                    # non-matching axis
                    del auxs1[key1]
                    continue

                if field1.Items[key1].size == 1:
                    # Field1 auxiliary coordinate has size-1 data array
                    found_equivalent_auxiliary_coordinates = True
                    del auxs1[key1]
                    break

                if field0._equivalent_item_data(key0, key1, field1, s=s, t=v):
                    # Field 0 auxiliary coordinate has equivalent data
                    # to a field 1 auxiliary coordinate
                    found_equivalent_auxiliary_coordinates = True
                    del auxs1[key1]
                    break
            #--- End: for                

            if not found_equivalent_auxiliary_coordinates:
                remove_items.add(key0)
        #--- End: for

        # ------------------------------------------------------------
        # Copy field1 auxiliary coordinates which do not span any
        # matching axes to field0
        # ------------------------------------------------------------
        for key1 in field1.Items.auxs():
            if key1 in insert_aux:
                continue
            axes1 = field1.Items.axes(key1)
            if set(axes1).isdisjoint(matching_axis1_to_axis0):
                insert_aux[key1] = [axis1_to_axis0[axis1] for axis1 in axes1]
        #--- End: for

        # ------------------------------------------------------------
        # Insert field1 items into field0
        # ------------------------------------------------------------

        # Map field1 items keys to field0 item keys
        key1_to_key0 = {}

        if _debug:
            print '5: insert_dim        =', insert_dim
            print '5: insert_aux        =', insert_aux
            print '5: insert_domain_anc =', insert_domain_anc
            print '5: insert_ref        =', insert_ref
            print '5: field0.Items().keys() =', sorted(field0.Items().keys())
            print '5: field1.Items().keys() =', sorted(field1.Items().keys())

        for key1, axes0 in insert_dim.iteritems():
            try:
                key0 = field0.insert_dim(field1.Items[key1], axes=axes0)
            except ValueError:
                # There was some sort of problem with the insertion, so
                # just ignore this item.
                pass
            else:
                key1_to_key0[key1] = key0
            if _debug:
                print('axes0, key1, field1.Items[key1] =',
                      axes0, key1, repr(field1.Items[key1]))
                
        for key1, axes0 in insert_aux.iteritems():
            try:
                key0 = field0.insert_aux(field1.Items[key1], axes=axes0)
            except ValueError:
                # There was some sort of problem with the insertion, so
                # just ignore this item.
                pass
            else:
                key1_to_key0[key1] = key0
            if _debug:
                print('axes0, key1, field1.Items[key1] =',
                      axes0, key1, repr(field1.Items[key1]))
                
        for key1, axes0 in insert_domain_anc.iteritems():
            try:
                key0 = field0.insert_domain_anc(field1.Items[key1], axes=axes0)
            except ValueError as error:
                # There was some sort of problem with the insertion, so
                # just ignore this item.
                if _debug:
                    print 'Domain ancillary insertion problem:', error
                pass
            else:
                key1_to_key0[key1] = key0
            if _debug:
                print 'cct axes0, key1, field1.Items[key1] =', axes0, key1, repr(field1.Items[key1])

        # ------------------------------------------------------------
        # Remove field0 which are no longer required
        # ------------------------------------------------------------
        if remove_items:
            if _debug:
                print sorted(field0.items().keys())
                print 'Removing {!r} from field0'.format(sorted(remove_items))

            field0.remove_items(remove_items, role='facdmr')

        # ------------------------------------------------------------
        # Copy coordinate references from field1 to field0 (do this
        # after removing any coordinates and domain ancillaries)
        # ------------------------------------------------------------
        for key1 in insert_ref:
            ref1 = field1.Items[key1] # DCH alert
            if _debug:
                print 'Copying {!r} from field1 to field0'.format(ref1)                

            identity_map = field1.Items(role='dac')
            for key1, item1 in identity_map.iteritems():
#                identity_map[key1] = key1_to_key0.get(key1, None)
                identity_map[key1] = key1_to_key0.get(key1, item1.name())

            new_ref0 = ref1.change_identifiers(identity_map, strict=True)
            
            field0.insert_ref(new_ref0, copy=False)
        #--- End: for

        return field0
    #--- End: def

    def _conform_for_assignment(self, other):
        '''Conform *other* so that it is ready for metadata-unaware assignment
broadcasting across *self*.

*other* is not changed in place.

:Parameters:

    other: `cf.Field`
        The field to conform.

:Returns:

    out: `cf.Field`
        The conformed version of *other*.

:Examples:

>>> g = _conform_for_assignment(f)

        '''
        # Analyse each domain
        s = self.analyse_items()
        v = other.analyse_items()
    
        if s['warnings'] or v['warnings']:
            raise ValueError(
"Can't setitem: {0}".format(s['warnings'] or v['warnings']))
    
        # Find the set of matching axes
        matching_ids = set(s['id_to_axis']).intersection(v['id_to_axis'])
        if not matching_ids:
            raise ValueError("Can't assign: No matching axes")
    
        # ------------------------------------------------------------
        # Check that any matching axes defined by auxiliary
        # coordinates are done so in both fields.
        # ------------------------------------------------------------
        for identity in matching_ids:
            if (identity in s['id_to_aux']) + (identity in v['id_to_aux']) == 1:
                raise ValueError(
"Can't assign: {0!r} axis defined by auxiliary in only 1 field".format(identity))
        #--- End: for
    
        copied = False
    
        # ------------------------------------------------------------
        # Check that 1) all undefined axes in other have size 1 and 2)
        # that all of other's unmatched but defined axes have size 1
        # and squeeze any such axes out of its data array.
        #
        # For example, if   self.Data is        P T     Z Y   X   A
        #              and  other.Data is     1     B C   Y 1 X T
        #              then other.Data becomes            Y   X T
        # ------------------------------------------------------------
        squeeze_axes1 = []
        for axis1 in v['undefined_axes']:
            if other.axis_size(axis1) != 1:            
                raise ValueError(
"Can't assign: Can't broadcast undefined axis with size {}".format(
    other.axis_size(axis1)))

            squeeze_axes1.append(axis1)
        #--- End: for

        for identity in set(v['id_to_axis']).difference(matching_ids):
            axis1 = v['id_to_axis'][identity]
            if other.axis_size(axis1) != 1:
               raise ValueError(
                   "Can't assign: Can't broadcast size {0} {1!r} axis".format(
                       other.axis_size(axis1), identity))
            
            squeeze_axes1.append(axis1)    
        #--- End: for

        if squeeze_axes1:
            if not copied:
                other = other.copy()
                copied = True

            other.squeeze(squeeze_axes1, i=True)
        #--- End: if

        # ------------------------------------------------------------
        # Permute the axes of other.Data so that they are in the same
        # order as their matching counterparts in self.Data
        #
        # For example, if   self.Data is       P T Z Y X   A
        #              and  other.Data is            Y X T
        #              then other.Data becomes   T   Y X
        # ------------------------------------------------------------
        data_axes0 = self.data_axes()
        data_axes1 = other.data_axes()

        transpose_axes1 = []       
        for axis0 in data_axes0:
            identity = s['axis_to_id'][axis0]
            if identity in matching_ids:
                axis1 = v['id_to_axis'][identity]                
                if axis1 in data_axes1:
                    transpose_axes1.append(axis1)
        #--- End: for
        if transpose_axes1 != data_axes1: 
            if not copied:
                other = other.copy()
                copied = True

            other.transpose(transpose_axes1, i=True)
        #--- End: if

        # ------------------------------------------------------------
        # Insert size 1 axes into other.Data to match axes in
        # self.Data which other.Data doesn't have.
        #
        # For example, if   self.Data is       P T Z Y X A
        #              and  other.Data is        T   Y X
        #              then other.Data becomes 1 T 1 Y X 1
        # ------------------------------------------------------------
        expand_positions1 = []
        for i, axis0 in enumerate(data_axes0):
            identity = s['axis_to_id'][axis0]
            if identity in matching_ids:
                axis1 = v['id_to_axis'][identity]
                if axis1 not in data_axes1:
                    expand_positions1.append(i)
            else:     
                expand_positions1.append(i)
        #--- End: for

        if expand_positions1:
            if not copied:
                other = other.copy()
                copied = True

            for i in expand_positions1:
                other.expand_dims(i, i=True)
        #--- End: if

        # ----------------------------------------------------------------
        # Make sure that each pair of matching axes has the same
        # direction
        # ----------------------------------------------------------------
        flip_axes1 = []
        for identity in matching_ids:
            axis1 = v['id_to_axis'][identity]
            axis0 = s['id_to_axis'][identity]
            if other.direction(axis1) != self.direction(axis0):
                flip_axes1.append(axis1)
         #--- End: for

        if flip_axes1:
            if not copied:
                other = other.copy()
                copied = True

            other = other.flip(flip_axes1, i=True)
        #--- End: if

        return other
    #--- End: def

    def _equivalent_item_data(self, key0, key1, field1, s=None,
                              t=None, atol=None, rtol=None,
                              traceback=False):
        ''':Parameters:
        
    key0: `str`

    key1: `str`

    field1: `cf.Field`

    s: `dict`, optional

    t: `dict`, optional

    {+atol}

    {+rtol}

    traceback: `bool`, optional
        If True then print a traceback highlighting where the two
        items differ.

        '''
        self_Items = self.Items
        field1_Items = field1.Items

        item0 = self_Items[key0]
        item1 = field1_Items[key1]
       
        if item0._hasData != item1._hasData:
            if traceback:
                print "{0}: Only one item has data".format(self.__class__.__name__)
                return False
        
        if not item0._hasData:
            # Neither field has a data array
            return True

        if item0.size != item1.size:
            if traceback:
                print("{}: Different data array sizes ({}, {})".format(
                    self.__class__.__name__, item0.size, item1.size))
            return False

        if item0.ndim != item1.ndim:
            if traceback:
                print("{0}: Different data array ranks ({1}, {2})".format(
                    self.__class__.__name__, item0.ndim, item1.ndim))
            return False

        axes0 = self_Items.axes(key0)
        axes1 = field1_Items.axes(key1)
        
        if s is None:
            s = self.analyse_items()
        if t is None:
            t = field1.analyse_items()
            
        transpose_axes = []
        for axis0 in axes0:
            axis1 = t['id_to_axis'].get(s['axis_to_id'][axis0], None)
            if axis1 is None:
                if traceback:
                    print("%s: TTTTTTTTTTT w2345nb34589*D*&" % self.__class__.__name__)
                return False

            transpose_axes.append(axes1.index(axis1))
        #--- End: for
                
        copy1 = True

        if transpose_axes != range(item1.ndim):
            if copy1:
                item1 = item1.copy()
                copy1 = False
                
            item1.transpose(transpose_axes, i=True)
        #--- End: if

        if item0.shape != item1.shape:
            # add traceback
            return False              

        direction0 = self_Items.direction
        direction1 = field1_Items.direction
        
        flip_axes = [i
                     for i, (axis1, axis0) in enumerate(izip(axes1, axes0))
                     if direction1(axis1) != direction0(axis0)]
        
        if flip_axes:
            if copy1:
                item1 = item1.copy()                
                copy1 = False
                
            item1.flip(flip_axes, i=True)
        #--- End: if
        
        if not item0._equivalent_data(item1, rtol=rtol, atol=atol,
                                      traceback=traceback):
            # add traceback
            return False
            
        return True
    #--- End: for

    # ----------------------------------------------------------------
    # Worker functions for regridding
    # ----------------------------------------------------------------

    def _regrid_get_latlong(self, name, axes=None):
        '''

Retrieve the latitude and longitude coordinates of this field and
associated information. If 1D lat/long coordinates are found then
these are returned. Otherwise, 2D lat/long coordinates are searched
for and if found returned.

:Parameters:

    name: `str`
        A name to identify the field in error messages.

    axes: `dict`, optional
        A dictionary specifying the X and Y axes, with keys 'X' and
        'Y'.

:Returns:

    axis_keys: `list`
        The keys of the x and y dimension coodinates.
    
    axis_sizes: `list`
        The sizes of the x and y dimension coordinates.

    coord_keys: `list`
        The keys of the x and y coordinate (1D dimension coordinate,
        or 2D auxilliary coordinates).
    
    coords: `list`
        The x and y coordinates (1D dimension coordinates or 2D
        auxilliary coordinates).

    coords_2D: `bool`
        True if 2D auxiliary coordinates are returned or if 1D X and Y
        coordinates are returned, which are not long/lat.

        '''
        if axes is None:
            # Retrieve the field's X and Y dimension coordinates
            x = self.dims('X')
            len_x = len(x)
            if not len_x:
                raise ValueError('No X dimension coordinate found for the ' +
                                 name + ' field. If none is present you ' +
                                 'may need to specify the axes keyword, ' +
                                 'otherwise you may need to set the X ' +
                                 'attribute of the X dimension coordinate ' +
                                 'to True.')

            if len_x > 1:
                raise ValueError('X dimension coordinate for the ' + name +
                                 ' field is not unique.')

            y = self.dims('Y')
            len_y = len(y)
            
            if not len_y:
                raise ValueError('No Y dimension coordinate found for the ' +
                                 name + ' field. If none is present you ' +
                                 'may need to specify the axes keyword, ' +
                                 'otherwise you may need to set the Y ' +
                                 'attribute of the Y dimension coordinate ' +
                                 'to True.')

            if len_y > 1:
                raise ValueError('Y dimension coordinate for the ' + name +
                                 ' field is not unique.')
            #--- End: if
            x_axis, x = x.popitem()
            y_axis, y = y.popitem()
            x_key = x_axis
            y_key = y_axis        
            x_size = x.size
            y_size = y.size
        else:
            try:
                x_axis = self.axis(axes['X'], key=True)
            except KeyError:
                raise ValueError("Key 'X' must be specified for axes of " +
                                 name + " field.")
            #--- End: try

            if x_axis is None:
                raise ValueError('X axis specified for ' + name +
                                 ' field not found.')
            #--- End: if

            try:
                y_axis = self.axis(axes['Y'], key=True)
            except KeyError:
                raise ValueError("Key 'Y' must be specified for axes of " +
                                 name + " field.")
            #--- End: try

            if y_axis is None:
                raise ValueError('Y axis specified for ' + name +
                                 ' field not found.')
            #--- End: if

            x_size = self.axis_size(x_axis)
            y_size = self.axis_size(y_axis)
        #--- End: if

        axis_keys = [x_axis, y_axis]
        axis_sizes = [x_size, y_size]

        # If 1D latitude and longitude coordinates for the field are not found
        # search for 2D auxiliary coordinates.
        if axes is not None or not x.Units.islongitude \
                            or not y.Units.islatitude:
            lon_found = False
            lat_found = False
            for key, aux in self.auxs(ndim=2).iteritems():
                if aux.Units.islongitude:
                    if lon_found:
                        raise ValueError('The 2D auxiliary longitude' +
                                         ' coordinate of the ' + name +
                                         ' field is not unique.')
                    else:
                        lon_found = True
                        x = aux
                        x_key = key
                    #--- End: if
                #--- End: if
                if aux.Units.islatitude:
                    if lat_found:
                        raise ValueError('The 2D auxiliary latitude' +
                                         ' coordinate of the ' + name +
                                         ' field is not unique.')
                    else:
                        lat_found = True
                        y = aux
                        y_key = key
                    #--- End: if
                #--- End: if
            if not lon_found or not lat_found:
                raise ValueError('Both longitude and latitude ' +
                                 'coordinates were not found for the ' +
                                 name + ' field.')

            if axes is not None:
                if set(axis_keys) != set(self.item_axes(x_key)):
                    raise ValueError('Axes of longitude do not match ' +
                                     'those specified for ' + name + 
                                     ' field.')

                if set(axis_keys) != set(self.item_axes(y_key)):
                    raise ValueError('Axes of latitude do not match ' +
                                     'those specified for ' + name +
                                     ' field.')
            #--- End: if
            coords_2D = True
        else:
            coords_2D = False
            # Check for size 1 latitude or longitude dimensions
            if x_size == 1 or y_size == 1:
                raise ValueError('Neither the longitude nor latitude' +
                                 ' dimension coordinates of the ' + name +
                                 ' field can be of size 1.')
        #--- End: if
        
        coord_keys = [x_key, y_key]
        coords = [x, y]
        return axis_keys, axis_sizes, coord_keys, coords, coords_2D
    #--- End: def
    
    def _regrid_get_cartesian_coords(self, name, axes):
        '''

Retrieve the specified cartesian dimension coordinates of the field and their
corresponding keys.

:Parameters:

    name : string
        A name to identify the field in error messages.

    axes : sequence
        Specifiers for the dimension coordinates to be retrieved. See
        cf.Field.axes for details.

:Returns:

    axis_keys : list
        A list of the keys of the dimension coordinates retrieved.

    coords : list
        A list of the dimension coordinates retrieved.

        '''
        axis_keys = []
        for axis in axes:
            tmp = self.axes(axis).keys()
            len_tmp = len(tmp)
            if not len_tmp:
                raise ValueError('No ' + name + ' axis found: ' + str(axis))
            elif len(tmp) != 1:
                raise ValueError('Axis of ' + name + ' must be unique: ' +
                                 str(axis))
            #--- End: if
            axis_keys.append(tmp.pop())
        
        coords = []
        for key in axis_keys:
            d = self.dim(key)
            if d is None:
                raise ValueError('No ' + name + ' dimension coordinate ' +
                                 'matches key ' + key + '.')
            coords.append(d)
        
        return axis_keys, coords
    #--- End: def

    def _regrid_get_axis_indices(self, axis_keys, i=False):
        '''
Get axis indices and their orders in rank of this field.

:Parameters:

    axis_keys: sequence
        A sequence of axis specifiers.
        
    i: `bool`, optional
        Whether to change the field in place or not.

:Returns:

    axis_indices: list
        A list of the indices of the specified axes.
        
    order: ndarray
        A numpy array of the rank order of the axes.
        
    self: 
        A copy of the field, which may have unsqueezed axes.
        
        '''
        # Get the positions of the axes
        axis_indices = []
        for axis_key in axis_keys:
            try:
                axis_index = self.data_axes().index(axis_key)
            except ValueError:
                self = self.unsqueeze(axis_key, i=i)
                axis_index = self.data_axes().index(axis_key)
            #--- End: try
            axis_indices.append(axis_index)
        #--- End: for
                    
        # Get the rank order of the positions of the axes
        tmp = numpy_array(axis_indices)
        tmp = tmp.argsort()
        order = numpy_empty(len(tmp), int)
        order[tmp] = numpy_arange(len(tmp))
        
        return axis_indices, order, self
    #--- End: def

    def _regrid_get_coord_order(self, axis_keys, coord_keys):
        '''

Get the ordering of the axes for each N-D auxiliary coordinate.

:Parameters:

    axis_keys: sequence
        A sequence of axis keys.
        
    coord_keys: sequence
        A sequence of keys for each ot the N-D auxiliary
        coordinates.
        
:Returns:

    coord_order: `list`
        A list of lists specifying the ordering of the axes for
        each N-D auxiliary coordinate.
        
        '''
        coord_axes = [self.item_axes(coord_key) for coord_key in coord_keys]
        coord_order = [[coord_axis.index(axis_key) for axis_key in axis_keys]
                       for coord_axis in coord_axes]
        return coord_order
    #--- End: def

    def _regrid_get_section_shape(self, axis_sizes, axis_indices):
        '''
Get the shape of each regridded section.

:Parameters:

    axis_sizes: sequence
        A sequence of the sizes of each axis along which the section.
        will be taken
        
    axis_indices: sequence
        A sequence of the same length giving the axis index of each
        axis.
        
:Returns:
    
    shape: `list`
        A list defining the shape of each section.
        
        '''
        
        shape = [1] * self.ndim
        for i, axis_index in enumerate(axis_indices):
            shape[axis_index] = axis_sizes[i]
        
        return shape
    #--- End: def

    @staticmethod
    def _regrid_check_bounds(src_coords, dst_coords, method, ext_coords=None):
        '''Check the bounds of the coordinates for regridding and reassign the
regridding method if auto is selected.
        
:Parameters:

    src_coords: sequence
        A sequence of the source coordinates.
        
    dst_coords: sequence
        A sequence of the destination coordinates.
        
    method: `str`
        A string indicating the regrid method.
        
    ext_coords: `None` or sequence
        If a sequence of extension coordinates is present these are
        also checked. Only used for cartesian regridding when
        regridding only, 1 (only 1!) dimension of a n>2 dimensional
        field. In this then we need to provided the coordinates of the
        the dimensions that aren't being regridded (that are the same
        in both src and dst grids) so that we can create a sensible
        ESMF grid object.
        
:Returns:

    `None`
    method: `str`ing
        The new regrid method if auto was selected before.

        '''
        
#        if method == 'auto':
#            method = 'conservative'
#            for coord in src_coords:
#                if not coord.hasbounds or not coord.contiguous(overlap=False):
#                    method = 'bilinear'
#                    break
#                #--- End: if
#            #--- End: for
#            for coord in dst_coords:
#                if not coord.hasbounds or not coord.contiguous(overlap=False):
#                    method = 'bilinear'
#                    break
#                #--- End: if
#            #--- End: for
#            if ext_coords is not None:
#                for coord in ext_coords:
#                    if (not coord.hasbounds or
#                        not coord.contiguous(overlap=False)):
#                        method = 'bilinear'
#                        break
#                    #--- End: if
#                #--- End: for
#            #--- End: if
        if method == 'conservative':
            for coord in src_coords:
                if not coord.hasbounds or not coord.contiguous(overlap=False):
                    raise ValueError('Source coordinates must have' +
                                     ' contiguous, non-overlapping bounds' +
                                     ' for conservative regridding.')
            #--- End: for

            for coord in dst_coords:
                if not coord.hasbounds or not coord.contiguous(overlap=False):
                    raise ValueError('Destination coordinates must have' +
                                     ' contiguous, non-overlapping bounds' +
                                     ' for conservative regridding.')
            #--- End: for

            if ext_coords is not None:
                for coord in ext_coords:
                    if (not coord.hasbounds or
                        not coord.contiguous(overlap=False)):
                        raise ValueError('Dimension coordinates must have' +
                                         ' contiguous, non-overlapping bounds' +
                                         ' for conservative regridding.')
                #--- End: for
            #--- End: if
        #--- End: if

#        return method
    #--- End: def

    def _regrid_get_reordered_sections(self, axis_order, regrid_axes,
                                       regrid_axis_indices):
        '''Get a dictionary of the data sections for regridding and a list of
its keys reordered if necessary so that they will be looped over in
the order specified in axis_order.

:Parameters:

    axis_order: None or sequence
        None or a sequence of axes specifiers. If None then the
        sections keys will not be reordered. If a particular axis
        is one of the regridding axes or is not found then a
        ValueError will be raised.
        
    regrid_axes: sequence
        A sequence of the keys of the regridding axes.
    
    regrid_axis_indices: sequence
        A sequence of the indices of the regridding axes.
            
:Returns:

    sections: `dict`
        A dictionary of the data sections for regridding.
        
    section_keys: `list`
        An ordered list of the section keys.

        '''

# If we had dynamic masking, we wouldn't need this method, we could
# sdimply replace it in regrid[sc] with a call to
# Data.section. However, we don't have it, so this allows us to
# possibibly reduce the number of trasnistions between different masks
# - each change is slow.
        
        axis_indices = []
        if axis_order is not None:
            for axis in axis_order:
                axis_key = self.dim(axis, key=True)
                if axis_key is not None:
                    if axis_key in regrid_axes:
                        raise ValueError('Cannot loop over regridding axes.')
                    #--- End: if
                    try:
                        axis_indices.append(self.data_axes().index(axis_key))
                    except ValueError:
                        # The axis has been squeezed so do nothing
                        pass 
                    #--- End: try
                else:
                    raise ValueError('Axis not found: ' + str(axis))    
                #--- End: if
            #--- End: for
        #--- End: if
        
        # Section the data
        sections = self.Data.section(regrid_axis_indices)
        
        # Reorder keys correspondingly if required
        if axis_indices:
            section_keys = sorted(sections.keys(),
                                  key=operator_itemgetter(*axis_indices))
        else:
            section_keys = sections.keys()
        
        return section_keys, sections
    #--- End: def

    def _regrid_get_destination_mask(self, dst_order, axes=('X', 'Y'),
                                     cartesian=False, coords_ext=None):
        '''Get the mask of the destination field.

:Parameters:

    dst_order: sequence, optional
        The order of the destination axes.
    
    axes: optional
        The axes the data is to be sectioned along.
    
    cartesian: `bool`, optional
        Whether the regridding is Cartesian or spherical.
    
    coords_ext: sequence, optional
        In the case of Cartesian regridding, extension coordinates
        (see _regrid_check_bounds for details).

:Returns:

    dst_mask: ndarray
        A numpy array with the mask.

        '''
        dst_mask = self.section(axes, stop=1,
                                ndim=1)[0].squeeze().array.mask
        dst_mask = dst_mask.transpose(dst_order)
        if cartesian:
            tmp = []
            for coord in coords_ext:
                tmp.append(coord.size)
                dst_mask = numpy_tile(dst_mask, tmp + [1]*dst_mask.ndim)
            #--- End: for
        #--- End: if
        return dst_mask
    #--- End: def

    def _regrid_fill_fields(self, src_data, srcfield, dstfield):
        '''Fill the source field with data and the destination field with fill
values.

:Parameters:
    
    src_data: ndarray
        The data to fill the source field with.
        
    srcfield: ESMPy Field
        The source field.
        
    dstfield: ESMPy Field
        The destination field. This get always gets initialised with
        missing values.

        '''
        srcfield.data[...] = numpy_ma_MaskedArray(src_data, copy=False).filled(self.fill_value(default='netCDF'))
        dstfield.data[...] = self.fill_value(default='netCDF')
    #--- End: def

    def _regrid_compute_field_mass(self, _compute_field_mass, k,
                                   srcgrid, srcfield, srcfracfield, dstgrid,
                                   dstfield):
        '''
        
Compute the field mass for conservative regridding. The mass should be
the same before and after regridding.

:Parameters:

    _compute_field_mass: `dict`
        A dictionary for the results.
    
    k: `tuple`
        A key identifying the section of the field being regridded.
        
    srcgrid: ESMPy grid
        The source grid.
        
    srcfield: ESMPy grid
        The source field.
        
    srcfracfield: ESMPy field
        Information about the fraction of each cell of the source
        field used in regridding.
        
    dstgrid: ESMPy grid
        The destination grid.
        
    dstfield: ESMPy field
        The destination field.
        
        '''
        if not type(_compute_field_mass) == dict:
            raise ValueError('Expected _compute_field_mass to be a dictionary.')
        
        # Calculate the mass of the source field
        srcareafield = Regrid.create_field(srcgrid, 'srcareafield')
        srcmass = Regrid.compute_mass_grid(srcfield, srcareafield, dofrac=True, 
            fracfield=srcfracfield, uninitval=self.fill_value(default='netCDF'))
        
        # Calculate the mass of the destination field
        dstareafield = Regrid.create_field(dstgrid, 'dstareafield')
        dstmass = Regrid.compute_mass_grid(dstfield, dstareafield, 
            uninitval=self.fill_value(default='netCDF'))
        
        # Insert the two masses into the dictionary for comparison
        _compute_field_mass[k] = (srcmass, dstmass)
    #--- End: def

    def _regrid_get_regridded_data(self, method, fracfield, dstfield,
                                   dstfracfield):
        '''
        
Get the regridded data of frac field as a numpy array from the
ESMPy fields.

:Parameters:

    method: `str`
        The regridding method.
        
    fracfield: `bool`
        Whether to return the frac field or not in the case of
        conservative regridding.
        
    dstfield: ESMPy field
        The destination field.
        
    dstfracfield: ESMPy field
        Information about the fraction of each of the destination
        field cells involved in the regridding. For conservative
        regridding this must be taken into account.
        
        '''
        if method == 'conservative':
            frac = dstfracfield.data[...].copy()
            if fracfield:
                regridded_data = frac
            else:
                frac[frac == 0.0] = 1.0
                regridded_data = numpy_ma_MaskedArray(dstfield.data[...].copy()/frac, 
                    mask=(dstfield.data == self.fill_value(default='netCDF')))
            #--- End: if
        else:            
            regridded_data = numpy_ma_MaskedArray(dstfield.data[...].copy(), 
                mask=(dstfield.data == self.fill_value(default='netCDF')))
        #--- End: if
        return regridded_data
    #--- End: def

    def _regrid_update_coordinate_references(self, dst, src_axis_keys,
                                             method, use_dst_mask, i,
                                             cartesian=False,
                                             axes=('X', 'Y'),
                                             n_axes=2,
                                             src_cyclic=False,
                                             dst_cyclic=False):
        '''
        
Update the coordinate references of the new field after regridding.

:Parameters:

    dst: `cf.Field` or `dict`
        The object with the destination grid for regridding.
    
    src_axis_keys: sequence of `str`
        The keys of the source regridding axes.
        
    method: `bool`
        The regridding method.
        
    use_dst_mask: `bool`
        Whether to use the destination mask in regridding.
        
    i: `bool`
        Whether to do the regridding in place.
        
    cartesian: `bool`, optional
        Whether to do Cartesian regridding or spherical
        
    axes: sequence, optional
        Specifiers for the regridding axes.
        
    n_axes: `int`, optional
        The number of regridding axes.
        
    src_cyclic: `bool`, optional
        Whether the source longitude is cyclic for spherical
        regridding.
        
    dst_cyclic: `bool`, optional
        Whether the destination longitude is cyclic for
        spherical regridding.
        
        '''
        for key, ref in self.refs().iteritems():
            ref_axes = self.axes(ref.coordinates, exact=True)
            if set(ref_axes).intersection(src_axis_keys):
                self.remove_item(key)
                continue

            for term, value in ref.ancillaries.iteritems():
                key = self.domain_anc(value, key=True)
                if key is None:
                    continue

                # If this domain ancillary spans both X and Y axes
                # then regrid it, otherwise remove it
                if f.domain_anc(key, axes_all=('X', 'Y')):
                    # Turn the domain ancillary into an independent
                    # field
                    value = self.field(key)
                    try:
                        if cartesian:
                            new_value = value.regridc(dst, axes=axes,
                                                      method=method,
                                                      use_dst_mask=use_dst_mask,
                                                      i=i)
                        else:
                            new_value = value.regrids(dst,
                                                      src_cyclic=src_cyclic,
                                                      dst_cyclic=dst_cyclic,
                                                      method=method,
                                                      use_dst_mask=use_dst_mask,
                                                      i=i)
                    except ValueError:
                        ref[term] = None
                        self.remove_item(key)
                    else:
                        ref[term] = key
                        d_axes = self.axes(key)
                        self.remove_item(key)
                        self.insert_domain_anc(new_value, key=key, axes=d_axes, copy=False)
                #--- End: if
            #--- End: for
        #--- End: for
    #--- End: def
        
    def _regrid_copy_coordinate_references(self, dst, dst_axis_keys):
        '''Copy coordinate references from the destination field to the new,
regridded field.

:Parameters:

    dst: `cf.Field`
        The destination field.
        
    dst_axis_keys: sequence of `str`
        The keys of the regridding axes in the destination field.

:Returns:

    None
        '''
        for key, ref in dst.refs().iteritems():
            axes = dst.axes(ref.coordinates, exact=True)
            if axes and set(axes).issubset(dst_axis_keys):
                # This coordinate reference's coordinate span the X
                # and/or Y axes
                self.insert_ref(dst._unconform_ref(ref), copy=False)
        #--- End: for
    #--- End: def

    def _regrid_update_coordinates(self, dst, dst_dict, dst_coords,
                                   src_axis_keys, dst_axis_keys,
                                   cartesian=False,
                                   dst_axis_sizes=None,
                                   dst_coords_2D=False,
                                   dst_coord_order=None):
        '''
        
Update the coordinates of the new field.

:Parameters:

    dst: Field or `dict`
        The object containing the destination grid.
    
    dst_dict: `bool`
        Whether dst is a dictionary.
        
    dst_coords: sequence
        The destination coordinates.
        
    src_axis_keys: sequence
        The keys of the regridding axes in the source field.
        
    dst_axis_keys: sequence
        The keys of the regridding axes in the destination field.
        
    cartesian: `bool`, optional
        Whether regridding is Cartesian of spherical, False by
        default.
        
    dst_axis_sizes: sequence, optional
        The sizes of the destination axes.
        
    dst_coords_2D: `bool`, optional
        Whether the destination coordinates are 2D, currently only
        applies to spherical regridding.
        
    dst_coord_order: `list`, optional
        A list of lists specifying the ordering of the axes for
        each 2D destination coordinate.
        
        '''


# NOTE: May be common ground between cartesian and shperical that
# could save some lines of code.

        # Remove the source coordinates of new field
        self.remove_items(axes=src_axis_keys)
        
        if cartesian:
            # Make axes map
            if not dst_dict:
                axis_map = {}
                for k_s, k_d in zip(src_axis_keys, dst_axis_keys):
                    axis_map[k_d] = k_s
            #--- End: if
            
            # Insert coordinates from dst into new field
            if dst_dict:
                for k_s, d in zip(src_axis_keys, dst_coords):
                    self._Axes[k_s].size = d.size
                    self.insert_dim(d, key=k_s)
            else:
                for k_d in dst_axis_keys:
                    d = dst.dim(k_d)
                    k_s = axis_map[k_d]
                    self._Axes[k_s].size = d.size
                    self.insert_dim(d, key=k_s)

                for aux_key, aux in dst.auxs(axes_superset=dst_axis_keys).iteritems():
                    aux_axes = [axis_map[k_d] for k_d in dst.item_axes(aux_key)]
                    self.insert_aux(aux, axes=aux_axes)
        else:
            # Give destination grid latitude and longitude standard names
            dst_coords[0].standard_name = 'longitude'
            dst_coords[1].standard_name = 'latitude'
            
            # Insert 'X' and 'Y' coordinates from dst into new field
            for axis_key, axis_size in zip(src_axis_keys, dst_axis_sizes):
                self._Axes[axis_key].size = axis_size

            if dst_dict:
                if dst_coords_2D:
                    for coord, coord_order in zip(dst_coords, dst_coord_order):
                        axis_keys = [src_axis_keys[index] for index in coord_order]
                        self.insert_aux(coord, axes=axis_keys)
                else:
                    for coord, axis_key in zip(dst_coords, src_axis_keys):
                        self.insert_dim(coord, key=axis_key)
                #--- End: if
            else:
                for src_axis_key, dst_axis_key in zip(src_axis_keys, dst_axis_keys):
                    try:
                        self.insert_dim(dst.dim(dst_axis_key), key=src_axis_key)
                    except AttributeError:
                        pass

                    for aux in dst.auxs(axes_all=dst_axis_key).values():
                        self.insert_aux(aux, axes=src_axis_key)
                #--- End: for

                for aux_key, aux in dst.auxs(axes_all=dst_axis_keys).iteritems():
                    aux_axes = dst.item_axes(aux_key)
                    if aux_axes == list(dst_axis_keys):
                        self.insert_aux(aux, axes=src_axis_keys)
                    else:
                        self.insert_aux(aux, axes=src_axis_keys[::-1])
                #--- End: for
            #--- End: if
        #--- End: if

        # Copy names of dimensions from destination to source field
        if not dst_dict:
            for src_axis_key, dst_axis_key in zip(src_axis_keys, dst_axis_keys):
                ncdim = dst._Axes[dst_axis_key].ncdim
                if ncdim is not None:
                    self._Axes[src_axis_key].ncdim = ncdim
            #--- End: for
        #--- End: if
    #--- End: def

    # ----------------------------------------------------------------
    # End of worker functions for regridding
    # ----------------------------------------------------------------

    def __repr__(self):
        '''Called by the :py:obj:`repr` built-in function.

x.__repr__() <==> repr(x)

:Examples:

>>> f
<CF Field: air_temperature(latitude(73), longitude(96) K>

        '''
        if self._hasData:
            axis_name = self.axis_name
            axis_size = self.axis_size
            x = ['{0}({1})'.format(axis_name(axis), axis_size(axis))
                 for axis in self.data_axes()]
            axis_names = '(%s)' % ', '.join(x)
        else:
            axis_names = ''
            
        # Field units
        units = getattr(self, 'units', '')
        calendar = getattr(self, 'calendar', None)
        if calendar:
            units += '%s calendar' % calendar

        return '<CF Field: %s%s %s>' % (self.name(''), axis_names, units)
    #--- End: def

    def __str__(self):
        '''Called by the :py:obj:`str` built-in function.

x.__str__() <==> str(x)

:Examples:

>>> print f
eastward_wind field summary
---------------------------
Data           : eastward_wind(air_pressure(15), latitude(72), longitude(96)) m s-1
Cell methods   : time: mean
Axes           : time(1) = [2057-06-01T00:00:00Z] 360_day
               : air_pressure(15) = [1000.0, ..., 10.0] hPa
               : latitude(72) = [88.75, ..., -88.75] degrees_north
               : longitude(96) = [1.875, ..., 358.125] degrees_east

        '''
        title = "Field: {0}".format(self.name(''))
        ncvar = getattr(self, 'ncvar', None)
        if ncvar is not None:
            title += " (ncvar%{0})".format(ncvar)
        
        string = [title]
        string.append(''.ljust(len(string[0]), '-'))

        # Units
        units = getattr(self, 'units', '')
        calendar = getattr(self, 'calendar', None)
        if calendar:
            units += ' {0} calendar'.format(calendar)
            
        axis_name = self.axis_name
        axis_size = self.axis_size        
        
        # Data
        if self._hasData:
            x = ['{0}({1})'.format(axis_name(axis), axis_size(axis))
                 for axis in self.data_axes()]
            string.append('Data           : {0}({1}) {2}'.format(
                self.name(''), ', '.join(x), units))
        elif units:
            string.append('Data           : {0}'.format(units))

        # Cell methods
        cell_methods = getattr(self, 'cell_methods', None)
        if cell_methods:
            string.append('Cell methods   : {0}'.format(self.cell_methods))

        axis_to_name = {}
        def _print_item(self, key, variable, dimension_coord):
            '''Private function called by __str__'''

            if dimension_coord:
                name = "{0}({1})".format(axis_name(key), axis_size(key))
                axis_to_name[key] = name
                
                variable = self.Items.get(key, None)

                if variable is None:
                    return name
                
                x = [name]

            else:
                # Auxiliary coordinate/cell measure/field ancillary/domain ancillary
                shape = [axis_to_name[axis] for axis in self.Items.axes(key)]
                shape = str(tuple(shape)).replace("'", "")
                shape = shape.replace(',)', ')')
                x = [variable.name('domain%'+key)]
                x.append(shape)
            #--- End: if

            if variable._hasData:
                x.append(' = {}'.format(variable.Data))

            return ''.join(x)
        #--- End: def

        # Axes and dimension coordinates
        ddd = self.data_axes()
        if ddd is None:
            ddd = ()
        non_spanning_axes = set(self._Axes).difference(ddd)
        x1 = [_print_item(self, dim, None, True)
              for dim in sorted(non_spanning_axes)]
        x2 = [_print_item(self, dim, None, True)
              for dim in ddd]
        x = x1 + x2
        if x:
            string.append('Axes           : {}'.format(
                '\n               : '.join(x)))
            
        # Auxiliary coordinates
        x = [_print_item(self, aux, v, False) 
             for aux, v in sorted(self.Items.auxs().iteritems())]
        if x:
            string.append('Aux coords     : {}'.format(
                '\n               : '.join(x)))

        # Cell measures
        x = [_print_item(self, msr, v, False)
             for msr, v in sorted(self.Items.msrs().iteritems())]
        if x:
            string.append('Cell measures  : {}'.format(
                '\n               : '.join(x)))

        # Coordinate references
        x = sorted([ref.name(default='')
                    for ref in self.Items.refs().itervalues()])
        if x:
            string.append('Coord refs     : {}'.format(
                '\n               : '.join(x)))

        # Domain ancillary variables
        x = [_print_item(self, key, anc, False)
             for key, anc in sorted(self.Items.domain_ancs().iteritems())]
        if x:
            string.append('Domain ancils  : {}'.format(
                '\n               : '.join(x)))
            
        # Field ancillary variables
        x = [_print_item(self, key, anc, False)
             for key, anc in sorted(self.Items.field_ancs().iteritems())]
        if x:
            string.append('Field ancils   : {}'.format(
                '\n               : '.join(x)))
            
        string.append('')
        
        return '\n'.join(string)
    #--- End def

    # ----------------------------------------------------------------
    # Attributes
    # ----------------------------------------------------------------
    @property
    def _Axes(self):
        '''
        '''
#        try:
        return self._private['special_attributes']['items'].Axes
#        except KeyError:
#            return Axes()
    #--- End: def

    @property
    def CellMethods(self):
        '''

The `cf.CellMethods` object containing the CF cell methods.

:Examples:

>>> f.CellMethods
<CF CellMethods: time: maximum (interval: 1.0 month) area: mean (area-weighted)>

'''
        return self.Items.cell_methods
    @CellMethods.setter
    def CellMethods(self, value):
        self.Items.cell_methods = value
    @CellMethods.deleter
    def CellMethods(self):
        self.Items.cell_methods = CellMethods()

    @property
    def DSG(self):
        '''

True if the field contains a collection of discrete sampling geomtries.

.. versionadded:: 2.0

.. seealso:: `featureType`

:Examples:

>>> f.featureType
'timeSeries'
>>> f.DSG
True

>>> f.getprop('featureType', 'NOT SET')
NOT SET
>>> f.DSG
False

'''
        return self.hasprop('featureType')
    #--- End: def

    @property
    def Flags(self):
        '''

A `cf.Flags` object containing self-describing CF flag values.

Stores the `flag_values`, `flag_meanings` and `flag_masks` CF
properties in an internally consistent manner.

:Examples:

>>> f.Flags
<CF Flags: flag_values=[0 1 2], flag_masks=[0 2 2], flag_meanings=['low' 'medium' 'high']>

'''
        return self._get_special_attr('Flags')
    @Flags.setter
    def Flags(self, value):
        self._set_special_attr('Flags', value)
    @Flags.deleter
    def Flags(self):
        self._del_special_attr('Flags')

    @property
    def Items(self):
#        try:
        return self._private['special_attributes']['items']
#        except KeyError:
#            return Items()
        
    @property
    def ncdimensions(self):
        '''
        '''
        out = {}
        for dim, axis in self._Axes.iteritems():
            ncdim = axis.ncdim
            if ncdim is not None:
                out[dim] = ncdim

        return out
    #--- End: def

    @property
    def rank(self):
        '''

The number of axes in the domain.

Note that this may be greater the number of data array axes.

.. seealso:: `ndim`, `unsqueeze`

:Examples:

>>> print f
air_temperature field summary
-----------------------------
Data           : air_temperature(time(12), latitude(64), longitude(128)) K
Cell methods   : time: mean
Axes           : time(12) = [ 450-11-16 00:00:00, ...,  451-10-16 12:00:00] noleap
               : latitude(64) = [-87.8638000488, ..., 87.8638000488] degrees_north
               : longitude(128) = [0.0, ..., 357.1875] degrees_east
               : height(1) = [2.0] m
>>> f.rank
4
>>> f.ndim
3
>>> f
<CF Field: air_temperature(time(12), latitude(64), longitude(128)) K>
>>> f.unsqueeze(i=True)
<CF Field: air_temperature(height(1), time(12), latitude(64), longitude(128)) K>
>>> f.rank
4
>>> f.ndim
4

'''
        return len(self._Axes)
    #--- End: def

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def flag_values(self):
        '''The flag_values CF property.

Provides a list of the flag values. Use in conjunction with
`flag_meanings`. See http://cfconventions.org/latest.html for details.

Stored as a 1-d numpy array but may be set as any array-like object.

:Examples:

>>> f.flag_values = ['a', 'b', 'c']
>>> f.flag_values
array(['a', 'b', 'c'], dtype='|S1')
>>> f.flag_values = numpy.arange(4)
>>> f.flag_values
array([1, 2, 3, 4])
>>> del f.flag_values

>>> f.setprop('flag_values', 1)
>>> f.getprop('flag_values')
array([1])
>>> f.delprop('flag_values')

        '''
        try:
            return self.Flags.flag_values
        except AttributeError:
            raise AttributeError(
                "%s doesn't have CF property 'flag_values'" %
                self.__class__.__name__)
    #--- End: def
    @flag_values.setter
    def flag_values(self, value):
        try:
            flags = self.Flags
        except AttributeError:
            self.Flags = Flags(flag_values=value)
        else:
            flags.flag_values = value
    #--- End: def
    @flag_values.deleter
    def flag_values(self):
        try:
            del self.Flags.flag_values
        except AttributeError:
            raise AttributeError(
                "Can't delete non-existent %s CF property 'flag_values'" %
                self.__class__.__name__)
        else:
            if not self.Flags:
                del self.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def flag_masks(self):
        '''The flag_masks CF property.

Provides a list of bit fields expressing Boolean or enumerated
flags. See http://cfconventions.org/latest.html for details.

Stored as a 1-d numpy array but may be set as array-like object.

:Examples:

>>> f.flag_masks = numpy.array([1, 2, 4], dtype='int8')
>>> f.flag_masks
array([1, 2, 4], dtype=int8)
>>> f.flag_masks = (1, 2, 4, 8)
>>> f.flag_masks
array([1, 2, 4, 8], dtype=int8)
>>> del f.flag_masks

>>> f.setprop('flag_masks', 1)
>>> f.getprop('flag_masks')
array([1])
>>> f.delprop('flag_masks')

        '''
        try:
            return self.Flags.flag_masks
        except AttributeError:
            raise AttributeError(
                "%s doesn't have CF property 'flag_masks'" %
                self.__class__.__name__)
    #--- End: def
    @flag_masks.setter
    def flag_masks(self, value):
        try:
            flags = self.Flags
        except AttributeError:
            self.Flags = Flags(flag_masks=value)
        else:
            flags.flag_masks = value
    #--- End: def
    @flag_masks.deleter
    def flag_masks(self):
        try:
            del self.Flags.flag_masks
        except AttributeError:
            raise AttributeError(
                "Can't delete non-existent %s CF property 'flag_masks'" %
                self.__class__.__name__)
        else:
            if not self.Flags:
                del self.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def flag_meanings(self):
        '''The flag_meanings CF property.

Use in conjunction with `flag_values` to provide descriptive words or
phrases for each flag value. If multi-word phrases are used to
describe the flag values, then the words within a phrase should be
connected with underscores. See http://cfconventions.org/latest.html
for details.

Stored as a 1-d numpy string array but may be set as a space delimited
string or any array-like object.

:Examples:

>>> f.flag_meanings = 'low medium      high'
>>> f.flag_meanings
array(['low', 'medium', 'high'],
      dtype='|S6')
>>> del flag_meanings

>>> f.flag_meanings = ['left', 'right']
>>> f.flag_meanings
array(['left', 'right'],
      dtype='|S5')

>>> f.flag_meanings = 'ok'
>>> f.flag_meanings
array(['ok'],
      dtype='|S2')

>>> f.setprop('flag_meanings', numpy.array(['a', 'b'])
>>> f.getprop('flag_meanings')
array(['a', 'b'],
      dtype='|S1')
>>> f.delprop('flag_meanings')

        '''
        try:
            return self.Flags.flag_meanings
        except AttributeError:
            raise AttributeError(
                "%s doesn't have CF property 'flag_meanings'" %
                self.__class__.__name__)
    #--- End: def
    @flag_meanings.setter
    def flag_meanings(self, value): 
        try:
            flags = self.Flags
        except AttributeError:
            self.Flags = Flags(flag_meanings=value)
        else:
            flags.flag_meanings = value
    #--- End: def
    @flag_meanings.deleter
    def flag_meanings(self):
        try:
            del self.Flags.flag_meanings
        except AttributeError:
            raise AttributeError(
                "Can't delete non-existent %s CF property 'flag_meanings'" %
                self.__class__.__name__)
        else:
            if not self.Flags:
                del self.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def cell_methods(self):
        '''

The `cf.CellMethods` object containing the CF cell methods of the data
array.

:Examples:

>>> f.cell_methods
'time: maximum (interval: 1.0 month) area: mean (area-weighted)'

'''
        return self.Items.cell_methods.write(self.axes_names())
    @cell_methods.deleter
    def cell_methods(self):
        self.Items.cell_methods = CellMethods()
 
    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property 
    def Conventions(self):
        '''The Conventions CF property.

The name of the conventions followed by the field. See
http://cfconventions.org/latest.html for details.

:Examples:

>>> f.Conventions = 'CF-1.6'
>>> f.Conventions
'CF-1.6'
>>> del f.Conventions

>>> f.setprop('Conventions', 'CF-1.6')
>>> f.getprop('Conventions')
'CF-1.6'
>>> f.delprop('Conventions')

        '''
        return self.getprop('Conventions')
    #--- End: def

    @Conventions.setter
    def Conventions(self, value): self.setprop('Conventions', value)
    @Conventions.deleter
    def Conventions(self):        self.delprop('Conventions')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def featureType(self):
        '''The featureType CF property.

The type of discrete sampling geometry, such as ``point`` or
``timeSeriesProfile``. See http://cfconventions.org/latest.html for
details.

.. versionadded:: 2.0

.. seealso:: `DSG`

:Examples:

>>> f.featureType = 'trajectoryProfile'
>>> f.featureType
'trajectoryProfile'
>>> del f.featureType

>>> f.setprop('featureType', 'profile')
>>> f.getprop('featureType')
'profile'
>>> f.delprop('featureType')

        '''
        return self.getprop('featureType')
    #--- End: def

    @featureType.setter
    def featureType(self, value):
        self.setprop('featureType', value)
    @featureType.deleter
    def featureType(self):        
        self.delprop('featureType')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def institution(self):
        '''The institution CF property.

Specifies where the original data was produced. See
http://cfconventions.org/latest.html for details.

:Examples:

>>> f.institution = 'University of Reading'
>>> f.institution
'University of Reading'
>>> del f.institution

>>> f.setprop('institution', 'University of Reading')
>>> f.getprop('institution')
'University of Reading'
>>> f.delprop('institution')

        '''
        return self.getprop('institution')
    #--- End: def
    @institution.setter
    def institution(self, value): self.setprop('institution', value)
    @institution.deleter
    def institution(self):        self.delprop('institution')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def references(self):
        '''The references CF property.

Published or web-based references that describe the data or methods
used to produce it. See http://cfconventions.org/latest.html for
details.

:Examples:

>>> f.references = 'some references'
>>> f.references
'some references'
>>> del f.references

>>> f.setprop('references', 'some references')
>>> f.getprop('references')
'some references'
>>> f.delprop('references')

        '''
        return self.getprop('references')
    #--- End: def
    @references.setter
    def references(self, value): self.setprop('references', value)
    @references.deleter
    def references(self):        self.delprop('references')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def standard_error_multiplier(self):
        '''The standard_error_multiplier CF property.

If a data variable with a `standard_name` modifier of
``'standard_error'`` has this attribute, it indicates that the values
are the stated multiple of one standard error. See
http://cfconventions.org/latest.html for details.

:Examples:

>>> f.standard_error_multiplier = 2.0
>>> f.standard_error_multiplier
2.0
>>> del f.standard_error_multiplier

>>> f.setprop('standard_error_multiplier', 2.0)
>>> f.getprop('standard_error_multiplier')
2.0
>>> f.delprop('standard_error_multiplier')

        '''
        return self.getprop('standard_error_multiplier')
    #--- End: def

    @standard_error_multiplier.setter
    def standard_error_multiplier(self, value):
        self.setprop('standard_error_multiplier', value)
    @standard_error_multiplier.deleter
    def standard_error_multiplier(self):
        self.delprop('standard_error_multiplier')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def source(self):
        '''The source CF property.

The method of production of the original data. If it was
model-generated, `source` should name the model and its version, as
specifically as could be useful. If it is observational, `source`
should characterize it (for example, ``'surface observation'`` or
``'radiosonde'``). See http://cfconventions.org/latest.html for
details.

:Examples:

>>> f.source = 'radiosonde'
>>> f.source
'radiosonde'
>>> del f.source

>>> f.setprop('source', 'surface observation')
>>> f.getprop('source')
'surface observation'
>>> f.delprop('source')

        '''
        return self.getprop('source')
    #--- End: def

    @source.setter
    def source(self, value): self.setprop('source', value)
    @source.deleter
    def source(self):        self.delprop('source')

    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def title(self):
        '''The title CF property.

A short description of the file contents from which this field was
read, or is to be written to. See http://cfconventions.org/latest.html
for details.

:Examples:

>>> f.title = 'model data'
>>> f.title
'model data'
>>> del f.title

>>> f.setprop('title', 'model data')
>>> f.getprop('title')
'model data'
>>> f.delprop('title')

        '''
        return self.getprop('title')
    #--- End: def

    @title.setter
    def title(self, value): self.setprop('title', value)
    @title.deleter
    def title(self):        self.delprop('title')

    def CM(self, xxx):
        pass

#    def canonical_ref(self, ref):
#        '''
#'''
#        ref = ref.copy()
#
#        for term, value in ref.parameters.iteritems():
#            if value is None or isinstance(value, basestring):
#                continue
#
#            canonical_units = CoordinateReference.canonical_units(term)
#            if canonical_units is None:
#                continue
#
#            if isinstance(canonical_units, basestring):
#                # units is a standard_name of a coordinate
#                coord = self.coord(canonical_units, exact=True)
#                if coord is not None:
#                    canonical_units = coord.Units
#
#            if canonical_units is not None:
#                if hasattr(value, Units):                
#                    if not canonical_units.equivalent(value.Units):
#                        raise ValueError("asdddddddddddddd 87236768")                
#                    data.Units = canonical_units
#        #--- End: for
#
#        return ref
#    #--- End: def

    def cell_area(self, radius=6371229.0, insert=False, force=False):
        '''Return a field containing horizontal cell areas.

.. versionadded:: 1.0

.. seealso:: `weights`

:Examples 1:

>>> a = f.{+name}()

:Parameters:

    radius: data-like, optional
        The radius used for calculating spherical surface areas when
        both of the horizontal axes are part of a spherical polar
        coordinate system. By default *radius* has a value of
        6371229 metres. If units are not specified then units of
        metres are assumed.

        {+data-like}

          *Example:*         
            Five equivalent ways to set a radius of 6371200 metres:
            ``radius=6371200``, ``radius=numpy.array(6371200)``,
            ``radius=cf.Data(6371200)``, ``radius=cf.Data(6371200,
            'm')``, ``radius=cf.Data(6371.2, 'km')``.

    insert: `bool`, optional
        If True then{+,fef,} the calculated cell areas are also
        inserted in place as an area cell measure object. An existing
        area cell measure object for the horizontal axes will not be
        overwritten.

    force: `bool`, optional
        If True the always calculate the cell areas. By
        default{+,fef,} if there is already an area cell measure
        object for the horizontal axes then it will provide the area
        values.
        
:Returns:

    out: `cf.{+Variable}`

:Examples:

>>> a = f.{+name}()
>>> a = f.{+name}(insert=True)
>>> a = f.{+name}(force=True)
>>> a = f.{+name}(radius=cf.Data(3389.5, 'km'))

        '''
        area_clm = self.measure('area', axes=('X', 'Y'))

        if not force and area_clm:
            w = self.weights('area')
        else:
            x = self.dim('X')
            y = self.dim('Y')
            if (x is None or y is None or 
                not x.Units.equivalent(_units_radians) or
                not y.Units.equivalent(_units_radians)):
                raise ValueError("sd---------------------")
            
            # Got x and y coordinates in radians, so we can calc.
    
            # Parse the radius of the planet
            radius = Data.asdata(radius).squeeze()
            radius.dtype = float
            if radius.size != 1:
                raise ValueError("Multiple radii: radius=%r" % radius)
            if not radius.Units:
                radius.override_units(_units_metres, i=True)
            elif not radius.Units.equivalent(_units_metres):
                raise ValueError(
                    "Invalid units for radius: %r" % radius.Units)
                    
            w = self.weights('area')
            radius **= 2
            w *= radius
            w.override_units(radius.Units, i=True)   
        #--- End: if               

        if insert:
            # ----------------------------------------------------
            # Insert new cell measure
            # ----------------------------------------------------
            if area_clm:
                raise ValueError(
                    "Can't overwrite an existing area cell measure object")

            clm = CellMeasure(data=w.data, copy=True)
            clm.measure = 'area'
            map_axes = w.map_axes(self)
            data_axes = w.data_axes()
            axes = (map_axes[data_axes[0]], map_axes[data_axes[1]])
            self.insert_measure(clm, axes=axes, copy=False)
        #--- End: if               

        w.standard_name = 'area'
        w.long_name     = 'area'

        return w
    #--- End: def

    def map_axes(self, other):
        '''Map the axis identifiers of the field to their equivalent axis
identifiers of another.

:Parameters:

    other: `cf.Field`

:Returns:

    out: `dict`
        A dictionary whose keys are the axis identifiers of the field
        with corresponding values of axis identifiers of the of other
        field.

:Examples:

>>> f.map_axes(g)
{'dim0': 'dim1',
 'dim1': 'dim0',
 'dim2': 'dim2'}

        '''
        s = self.analyse_items()
        t = other.analyse_items()
        id_to_axis1 = t['id_to_axis']

        out = {}        
        for axis, identity in s['axis_to_id'].iteritems():
            if identity in id_to_axis1:
                out[axis] = id_to_axis1[identity]

        return out
    #--- End: def

    def close(self):
        '''Close all files referenced by the field.

Note that a closed file will be automatically reopened if its contents
are subsequently required.

:Examples 1:

>>> f.{+name}()

:Returns:

    `None`

        '''
#        # List functionality
#        if self._list:
#            print  "DEPRECATION WARNING: fl.close() has been deprecated. Use [f.close() for f in fl] inste#ad."
#            for f in self:
#                f.close()
#            return 

        super(Field, self).close()

        self.Items.close()
    #--- End: def

    def iscyclic(self, axes=None, **kwargs):
        '''
Returns True if the given axis is cyclic.

.. versionadded:: 1.0

.. seealso:: `axis`, `cyclic`, `period`

:Examples 1:

>>> b = f.{+name}('X')

:Parameters:

    {+axes, kwargs}

:Returns:

    out: `bool`
        True if the selected axis is cyclic, otherwise False.
        
:Examples 2:

>>> f.cyclic()
{}
>>> f.{+name}('X')
False
>>> f.cyclic('X', period=360)
{}
>>> f.{+name}('X')
True

'''
        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:
            raise ValueError("Can't identify unique %r axis" % axes)

        return axis in self.cyclic()
    #--- End: def

    @classmethod
    def concatenate(cls, fields, axis=0, _preserve=True):
        '''

Join a sequence of fields together.

This is different to `cf.aggregate` because it does not account for
all metadata. For example, it assumes that the axis order is the same
in each field.

.. versionadded:: 1.0

.. seealso:: `cf.aggregate`, `cf.Data.concatenate`

:Parameters:

    fields: `cf.FieldList`

    axis: `int`, optional

:Returns:

    out: `cf.Field`

:Examples:

'''         
        if isinstance(fields, Field):
            return fields.copy()

        field0 = fields[0]

#        # List functionality
#        if field0._list:
#            print  "DEPRECATION WARNING: fl.concatenateclose() has been deprecated. Use [f.close() for f i#n fl] instead."
#            return field0.concatenate(fields, axis=axis, _preserve=_preserve)

        if len(fields) == 1:
            return fields0.copy()
                                            
        out = super(cls, field0).concatenate(fields, axis=axis,
                                             _preserve=_preserve)
            
        # Change the axis size
        dim = field0.data_axes()[axis]        
        out.insert_axis(DomainAxis(out.shape[axis]), key=dim, replace=True)

        # ------------------------------------------------------------
        # Concatenate items
        # ------------------------------------------------------------
        for role in ('d', 'a', 'm', 'f', 'c'):
            for key, item in field0.items(role=role).iteritems():
                item_axes = field0.item_axes(key)

                if dim not in item_axes:
                    # This item does not span the concatenating axis in
                    # the first field
                    continue

                items = [item]
                for f in fields[1:]:
                    i = f.item(key)
                    if i is not None:
                        items.append(i)                    
                    else:
                        # This field does not have this item
                        items = None
                        break
                #--- End: for

                if not items:
                    # Not every field has this item, so remove it from the
                    # output field.
                    out.remove_item(key)
                    continue
                
                # Still here? Then try concatenating the items from
                # each field.
                try:
                    item = item.concatenate(items, axis=item_axes.index(dim),
                                            _preserve=_preserve)
                except ValueError:
                    # Couldn't concatenate this item, so remove it from
                    # the output field.
                    out.remove_item(key)
                else:
                    # Successfully concatenated this item, so insert
                    # it into the output field.
                    out.insert_item(role, item, key=key, axes=item_axes,
                                    copy=False, replace=True)
            #--- End: for
        #--- End: for

        return out
    #--- End: def

    def constructs(self):
        '''Return all of the data model constructs of the field.

.. versionadded:: 2.0

.. seealso:: `dump`

:Examples 1:

>>> f.{+name}()

:Returns:

    out: `list`
        The objects correposnding CF data model constructs.

:Examples 2:

>>> print f
eastward_wind field summary
---------------------------
Data           : eastward_wind(air_pressure(15), latitude(72), longitude(96)) m s-1
Cell methods   : time: mean
Axes           : time(1) = [2057-06-01T00:00:00Z] 360_day
               : air_pressure(15) = [1000.0, ..., 10.0] hPa
               : latitude(72) = [88.75, ..., -88.75] degrees_north
               : longitude(96) = [1.875, ..., 358.125] degrees_east
>>> f.{+name}()
[<CF Field: eastward_wind(air_pressure(15), latitude(72), longitude(96)) m s-1>,
 <CF DomainAxis: 96>,
 <CF DomainAxis: 1>,
 <CF DomainAxis: 15>,
 <CF DomainAxis: 72>,
 <CF CellMethod: dim3: mean>,
 <CF DimensionCoordinate: longitude(96) degrees_east>,
 <CF DimensionCoordinate: time(1) 360_day>,
 <CF DimensionCoordinate: air_pressure(15) hPa>,
 <CF DimensionCoordinate: latitude(72) degrees_north>]

        '''
        out = [self]
        out.extend(self._Axes.values())
        out.extend(self.CellMethods)
        out.extend(self.Items().values())
        return out
    #--- End: def

    def cyclic(self, axes=None, iscyclic=True, period=None, **kwargs):
        '''Set the cyclicity of an axis.

A unique axis is selected with the *axes* and *kwargs* parameters.

.. versionadded:: 1.0

.. seealso:: `autocyclic`, `axis`, `iscyclic`, `period`

`int`

:Examples 1:

>>> s = f.{+name}('X', period=360)

:Parameters:

    {+axes, kwargs}

    iscyclic: `bool`, optional
        If False then the axis is set to be non-cyclic. By default the
        selected axis is set to be cyclic.

    period: data-like object, optional       
        The period for a dimension coordinate object which spans the
        selected axis. The absolute value of *period* is used. If
        *period* has units then they must be compatible with those of
        the dimension coordinates, otherwise it is assumed to have the
        same units as the dimension coordinates.

        {+data-like}

:Returns:

    out: `set`
        The axes of the field which were cyclic prior to the new
        setting, or the current cyclic axes if no axis was specified.

:Examples:

>>> f.axes('X', key=True)
{'dim3': <CF DomainAxis: 192>}
>>> f.{+name}()
{}
>>> f.{+name}('X', period=360)
{}
>>> f.{+name}()
{'dim3'}
>>> f.{+name}('X', False)
{'dim3'}
>>> f.{+name}()
{}
>>> f.{+name}('longitude', period=360, exact=True)
{}
>>> f.{+name}()
{'dim3'}
>>> f.{+name}('dim3', False)
{'dim3'}
>>> f.{+name}()
{}

        '''       
        try:
            data = self.Data
        except AttributeError:
            return set()

        data_axes = self.data_axes()
        old = set([data_axes[i] for i in data.cyclic()])

        if axes is None and not kwargs:            
            return old
        
        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:
            raise ValueError("879534 k.j asdm,547`")

        try:
            data.cyclic(data_axes.index(axis), iscyclic)
        except ValueError:
            pass

        if iscyclic:
            dim = self.dim(axis)
            if dim is not None:
                if period is not None:
                    dim.period(period)
                elif dim.period() is None:
                    raise ValueError(
                        "A cyclic dimension coordinate must have a period")
        #--- End: if

        return old
    #--- End: def

    def weights(self, weights='auto', scale=False, components=False,
                methods=False, **kwargs):
        '''Return weights for the data array values.

The weights are those used during a statistical collapse of the
data. For example when computing a area weight average.

Weights for any combination of axes may be returned.

Weights are either derived from the field's metadata (such as
coordinate cell sizes) or provided explicitly in the form of other
`cf.Field` objects. In any case, the outer product of these weights
components is returned in a field which is broadcastable to the
orginal field (see the *components* parameter for returning the
components individually).

By default null, equal weights are returned.

.. versionadded:: 1.0

.. seealso:: `cell_area`, `collapse`

:Examples 1:

>>> g = f.{+name}()

:Parameters:

    weights, kwargs: *optional*
        Specify the weights to be created. There are two distinct
        methods: **type 1** will always succeed in creating weights
        for all axes of the field, at the expense of not always being
        able to control exactly how the weights are created (see the
        *methods* parameter); **type 2** allows particular types of
        weights to be defined for particular axes and an exception
        will be raised if it is not possible to the create weights.

          * **Type 1**: *weights* may be one of:
        
              ==========  ============================================
              *weights*   Description
              ==========  ============================================
              `None`      Equal weights for all axes. This the
                          default.

              ``'auto'``  Weights are created for non-overlapping
                          subsets of the axes by the methods
                          enumerated in the above notes. Set the
                          *methods* parameter to find out how the
                          weights were actually created.

                          In this case weights components are created
                          for all axes of the field by one or more of
                          the following methods, in order of
                          preference,
                        
                            1. Volume cell measures
                            2. Area cell measures
                            3. Area calculated from (grid) latitude
                               and (grid) longitude dimension
                               coordinates with bounds
                            4. Cell sizes of dimension coordinates
                               with bounds
                            5. Equal weights

                          and the outer product of these weights
                          components is returned in a field which is
                          broadcastable to the orginal field (see the
                          *components* parameter).
              ==========  ============================================

       ..

          * **Type 2**: *weights* may be one, or a sequence, of:
          
              ============  ==========================================
              *weights*     Description     
              ============  ==========================================
              ``'area'``    Cell area weights from the field's area
                            cell measure construct or, if one doesn't
                            exist, from (grid) latitude and (grid)
                            longitude dimension coordinates. Set the
                            *methods* parameter to find out how the
                            weights were actually created.
              
              ``'volume'``  Cell volume weights from the field's
                            volume cell measure construct.
              
              items         Weights from the cell sizes of the
                            dimension coordinate objects that would be
                            selected by this call of the field's
                            `~cf.Field.dims` method: ``f.dims(items,
                            **kwargs)``. See `cf.Field.dims` for
                            details.
              
              `cf.Field`    Take weights from the data array of
                            another field, which must be broadcastable
                            to this field.
              ============  ==========================================
 
            If *weights* is a sequence of any combination of the above
            then the returned field contains the outer product of the
            weights defined by each element of the sequence. The
            ordering of the sequence is irrelevant.

              *Example:*
                To create to 2-dimensional weights based on cell
                areas: ``f.weights('area')``. To create to
                3-dimensional weights based on cell areas and linear
                height: ``f.weights(['area', 'Z'])``.

    scale: `bool`, optional
        If True then scale the returned weights so that they are less
        than or equal to 1.

    components: `bool`, optional
        If True then a dictionary of orthogonal weights components is
        returned instead of a field. Each key is a tuple of integers
        representing axes positions in the field's data array with
        corresponding values of weights in `cf.Data` objects. The axes
        of weights match the axes of the field's data array in the
        order given by their dictionary keys.

    methods: `bool`, optional
        If True, then return a dictionary describing methods used to
        create the weights.

:Returns:

    out: `cf.Field` or `dict`
        The weights field or, if *components* is True, orthogonal
        weights in a dictionary.

:Examples 2:

>>> f
[+1]<CF Field: air_temperature(time(1800), latitude(145), longitude(192)) K>
[+N][<CF Field: air_temperature(time(1800), latitude(145), longitude(192)) K>]
>>> f.weights()
[+1]<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 86400 s.rad>
[+N][<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 86400 s.rad>]
>>> f.weights('auto', scale=True)
[+1]<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 1>
[+N][<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 1>]
[+1]>>> f.weights('auto', components=True)
[+1]{(0,): <CF Data: [1.0, ..., 1.0] d>,
[+1] (1,): <CF Data: [5.94949998503e-05, ..., 5.94949998503e-05]>,
[+1] (2,): <CF Data: [0.0327249234749, ..., 0.0327249234749] radians>}
[+1]>>> f.weights('auto', components=True, scale=True)
[+1]{(0,): <CF Data: [1.0, ..., 1.0]>,
[+1] (1,): <CF Data: [0.00272710399807, ..., 0.00272710399807]>,
[+1] (2,): <CF Data: [1.0, ..., 1.0]>}
[+1]>>> f.weights('auto', methods=True)
[+1]{(0,): 'linear time',
[+1] (1,): 'linear sine latitude',
[+1] (2,): 'linear longitude'}

        '''
#        def _field_of_weights(data, domain=None, axes=None):
        def _scalar_field_of_weights(data):
            '''Return a field of weights with long_name ``'weight'``.

    :Parameters:
    
        data: `cf.Data`
            The weights which comprise the data array of the weights
            field.

    :Returns:

        out: `cf.Field`

            '''
            w = type(self)(data=data, copy=False)
            w.long_name = 'weight'
            w.comment   = 'Weights for {!r}'.format(self)
            return w
        #--- End: def

        def _measure_weights(self, measure, comp, weights_axes, auto=False):
            '''
Cell measure weights
'''
            m = self.items(measure, role='m', exact=True)
           
            if not m:
                if measure == 'area':
                    return False
                if auto:
                    return
                raise ValueError(
                    "Can't get weights: No %r cell measure" % measure)
            
            key, clm = m.popitem()    
            
            if m:
                if auto:
                    return False
                raise ValueError("Multiple area cell measures")
                
            clm_axes0 = self.item_axes(key)
            
            clm_axes = [axis for axis, n in izip(clm_axes0, clm.shape)
                        if n > 1]
                
            for axis in clm_axes:
                if axis in weights_axes:
                    if auto:
                        return False
                    raise ValueError(
                        "Multiple weights specifications for %r axis" % 
                        self.axis_name(axis))
                
            clm = clm.Data.copy()
            if clm_axes != clm_axes0:
                iaxes = [clm_axes0.index(axis) for axis in clm_axes]
                clm.squeeze(iaxes, i=True)
            
            if methods:
                comp[tuple(clm_axes)] = measure+' cell measure'
            else:    
                comp[tuple(clm_axes)] = clm
                
            weights_axes.update(clm_axes)
            
            return True
        #--- End: def
        
        def _linear_weights(self, axis, comp, weights_axes, auto=False):
            # ------------------------------------------------------------
            # 1-d linear weights from dimension coordinates
            # ------------------------------------------------------------            
            d = self.dims(axis)
            if not d:
                if auto:
                    return
                raise ValueError("Can't find axis matching %r" % axis)

            axis, dim = d.popitem()

            if d:         
                if auto:
                    return
                raise ValueError("Multiple axes matching %r" % axis)
            
            if dim.size == 1:
                return

            if axis in weights_axes:
                if auto:
                    return
                raise ValueError(
"Multiple weights specifications for {0!r} axis".format(self.axis_name(axis)))

            if not dim.hasbounds:
                if auto:
                    return
                raise ValueError(
                    "Can't find linear weights for %r axis: No bounds" % 
                    dim.name(default=''))

            if dim.hasbounds:
                if methods:
                    comp[(axis,)] = 'linear '+dim.name(default='')
                else: 
                    comp[(axis,)] = dim.cellsize
            #--- End: if

            weights_axes.add(axis)
        #--- End: def
            
        def _area_weights_XY(self, comp, weights_axes, auto=False): 
            # ----------------------------------------------------
            # Calculate area weights from X and Y dimension
            # coordinates
            # ----------------------------------------------------
            xdims = self.dims({None: 'X', 'units': 'radians'})
            ydims = self.dims({None: 'Y', 'units': 'radians'})
            
            if not (xdims and ydims):
                if auto:
                    return
                raise ValueError(
"Insufficient coordinate constructs for calculating area weights")
                
            xaxis, xcoord = xdims.popitem()
            yaxis, ycoord = ydims.popitem()
                
            if xdims or ydims:
                if auto:
                    return
                raise ValueError(
"Ambiguous coordinate constructs for calculating area weights")
            
            for axis in (xaxis, yaxis):                
                if axis in weights_axes:
                    if auto:
                        return
                    raise ValueError(
                        "Multiple weights specifications for %r axis" % 
                        self.axis_name(axis))

            if xcoord.size > 1:
                if not xcoord.hasbounds: 
                    if auto:
                        return
                    raise ValueError(
                        "Can't find area weights: No bounds for %r axis" % 
                        xcoord.name(default=''))

                if methods:
                    comp[(xaxis,)] = 'linear '+xcoord.name(default='')
                else:
                    cells = xcoord.cellsize
                    cells.Units = _units_radians
                    comp[(xaxis,)] = cells

                weights_axes.add(xaxis)
            #--- End: if

            if ycoord.size > 1:
                if not ycoord.hasbounds:
                    if auto:
                        return
                    raise ValueError(
                        "Can't find area weights: No bounds for %r axis" % 
                        ycoord.name(default=''))

                ycoord = ycoord.clip(-90, 90, units=Units('degrees'))
                ycoord = ycoord.sin(i=True)
    
                if methods:
                    comp[(yaxis,)] = 'linear sine '+ycoord.name(default='')
                else:            
                    comp[(yaxis,)] = ycoord.cellsize

                weights_axes.add(yaxis)
            #--- End: if
        #--- End: def

        def _field_weights(self, fields, comp, weights_axes):
            # ------------------------------------------------------------
            # Field weights
            # ------------------------------------------------------------
            s = self.analyse_items()

            for w in fields:
                t = w.analyse_items()
    
                if t['undefined_axes']:
                    if t.axes(size=gt(1)).intersection(t['undefined_axes']):
                        raise ValueError("345jn456jn")
    
                w = w.squeeze()

                axis1_to_axis0 = {}

                for axis1 in w.data_axes():
                    identity = t['axis_to_id'].get(axis1, None)
                    if identity is None:
                        raise ValueError(
                            "Weights field has unmatched, size > 1 %r axis" %
                            w.axis_name(axis1))
                    
                    axis0 = s['id_to_axis'].get(identity, None)
                    if axis0 is None:
                        raise ValueError(
                            "Weights field has unmatched, size > 1 %r axis" %
                            identity)
                                    
                    if w.axis_size(axis1) != self.axis_size(axis0):
                        raise ValueError(
"Weights field has incorrectly sized {!r} axis ({} != {})".format(
    identity, w.axis_size(axis1), self.axis_size(axis0)))
    
                    axis1_to_axis0[axis1] = axis0                    

                    # Check that the defining coordinate data arrays are
                    # compatible
                    key0 = s['axis_to_coord'][axis0]                
                    key1 = t['axis_to_coord'][axis1]
   
                    if not self._equivalent_item_data(key0, key1, w, s=s, t=t):
                        raise ValueError(
"Weights field has incompatible {!r} coordinates".format(identity))
    
                    # Still here? Then the defining coordinates have
                    # equivalent data arrays
    
                    # If the defining coordinates are attached to
                    # coordinate references then check that those
                    # coordinate references are equivalent                    
                    refs0 = [ref for ref in self.Items.refs().itervalues()
                             if key0 in ref.coordinates]
                    refs1 = [ref for ref in w.Items.refs().itervalues()
                             if key1 in ref.coordinates]

                    nrefs = len(refs0)
                    if nrefs > 1 or nrefs != len(refs1):
                        # The defining coordinate are associated with
                        # different numbers of coordinate references
                        equivalent_refs = False
                    elif not nrefs:
                        # Neither defining coordinate is associated with a
                        # coordinate reference                    
                        equivalent_refs = True
                    else:  
                        # Each defining coordinate is associated with
                        # exactly one coordinate reference
                        equivalent_refs = self._equivalent_refs(refs0[0], refs1[0],
                                                                w, s=s, t=t)

                    if not equivalent_refs:
                        raise ValueError(
"Input weights field an incompatible coordinate reference")
                #--- End: for
    
                axes0 = tuple([axis1_to_axis0[axis1] for axis1 in w.data_axes()])
            
                for axis0 in axes0:
                    if axis0 in weights_axes:
                        raise ValueError(
                            "Multiple weights specified for {!r} axis".format(
                                self.axis_name(axis0)))
                #--- End: for
    
                comp[axes] = w.Data
            
                weights_axes.update(axes)
        #--- End: def

#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            if components:
#                raise ValueError("oooo 2")
#            if methods:
#                raise ValueError("oooo 3")
#            return self._list_method('weights', kwargs2)

        if weights is None:
            # --------------------------------------------------------
            # All equal weights
            # --------------------------------------------------------
            if components:
                # Return an empty components dictionary
                return {}
            
            # Return a field containing a single weight of 1
            return _scalar_field_of_weights(Data(1.0, '1'))
        #--- End: if

        # Still here?
        if methods:
            components = True

        comp         = {}
        data_axes    = self.data_axes()

        # All axes which have weights
        weights_axes = set()

        if isinstance(weights, basestring) and weights == 'auto':
            # --------------------------------------------------------
            # Autodetect all weights
            # --------------------------------------------------------

            # Volume weights
            _measure_weights(self, 'volume', comp, weights_axes, auto=True)

            # Area weights
            if not _measure_weights(self, 'area', comp, weights_axes, auto=True):
                _area_weights_XY(self, comp, weights_axes, auto=True)

            # 1-d linear weights from dimension coordinates
            for axis in self.dims(): #.keys():                
                _linear_weights(self, axis, comp, weights_axes, auto=True)
 
        elif isinstance(weights, dict):
            # --------------------------------------------------------
            # Dictionary of components
            # --------------------------------------------------------
            for key, value in weights.iteritems():                
                try:
                    key = [data_axes[iaxis] for iaxis in key]
                except IndexError:
                    raise ValueError("s ^^^^^^ csdcvd 3456 4")

                multiple_weights = weights_axes.intersection(key)
                if multiple_weights:
                    raise ValueError(
                        "Multiple weights specifications for {0!r} axis".format(
                            self.axis_name(multiple_weights.pop())))
                #--- End: if
                weights_axes.update(key)

                comp[tuple(key)] = value.copy()
            #--- End: for
        else:

            fields = []
            axes   = []
            
            if isinstance(weights, basestring) and weights in ('area', 'volume'):
                cell_measures = (weights,)
            else:
                cell_measures = []
                for w in tuple(weights):
                    if isinstance(w, self.__class__):
                        fields.append(w)
                    elif w in ('area', 'volume'):
                        cell_measures.append(w)
                    else:
                        axes.append(w)
            #--- End: if
            
            # Field weights
            _field_weights(self, fields, comp, weights_axes)

            # Volume weights
            if 'volume' in cell_measures:
                _measure_weights(self, 'volume', comp, weights_axes)
            
            # Area weights
            if 'area' in cell_measures:
                if not _measure_weights(self, 'area', comp, weights_axes):
                    _area_weights_XY(self, comp, weights_axes)      

            # 1-d linear weights from dimension coordinates
            for axis in axes:
                _linear_weights(self, axis, comp, weights_axes, auto=False)
        #--- End: if

        # ------------------------------------------------------------
        # Scale the weights so that they are <= 1.0
        # ------------------------------------------------------------
        if scale and not methods:
            # What to do about -ve weights? dch
            for key, w in comp.items(): 
                wmax = w.data.max()    
                if wmax > 0:
                    wmax.dtype = float
                    if not numpy_can_cast(wmax.dtype, w.dtype):
                        w = w / wmax
                    else:
                        w /= wmax
                    comp[key] = w
        #--- End: if

        if components:
            # --------------------------------------------------------
            # Return a dictionary of component weights, which may be
            # empty.
            # -------------------------------------------------------- 
            components = {}
            for key, v in comp.iteritems():
                key = [data_axes.index(axis) for axis in key]
                if not key:
                    continue

                components[tuple(key)] = v
            #--- End: for

            return components
        #--- End: if

        if methods:
            return components

        if not comp:
            # --------------------------------------------------------
            # No component weights have been defined so return an
            # equal weights field
            # --------------------------------------------------------
            return _scalar_field_of_weights(Data(1.0, '1'))
        
        # ------------------------------------------------------------
        # Return a weights field which is the outer product of the
        # component weights
        # ------------------------------------------------------------
        pp = sorted(comp.items())       
        waxes, wdata = pp.pop(0)
        while pp:
            a, y = pp.pop(0)
            wdata.outerproduct(y, i=True)
            waxes += a
        #--- End: while
        
        field = type(self)(source=self, copy=False)

        asd = set(field._Axes).difference(weights_axes)
        field.remove_items(axes=asd)
        field.remove_data()
        field.remove_axes(asd)
 
        field = field.copy()
        
        field.insert_data(wdata, axes=waxes)

        field.properties(clear=True)

        field.long_name = 'weights'
        
        return field
    #--- End: def
#(any object which may be used to
#            initialise a `cf.Data` instance)

# rolling_window=None, window_weights=None,
#
#    rolling_window: *optional*
#        Group the axis elements for a "rolling window" collapse. The
#        axis is grouped into **consecutive** runs of **overlapping**
#        elements. The first group starts at the first element of the
#        axis and each following group is offset by one element from
#        the previous group, so that an element may appear in multiple
#        groups. The collapse operation is applied to each group
#        independently and the collapsed axis in the returned field
#        will have a size equal to the number of groups. If weights
#        have been given by the *weights* parameter then they are
#        applied to each group, unless alternative weights have been
#        provided with the *window_weights* parameter. The
#        *rolling_window* parameter may be one of:
#
#          * An `int` defining the number of elements in each
#            group. Each group will have exactly this number of
#            elements. Note that if the group size does does not divide
#            exactly into the axis size then some elements at the end
#            of the axis will not be included in any group.
#            
#              Example: To define groups of 5 elements:
#              ``rolling_window=5``.
#
#        .. 
#
#          * A `cf.Data` defining the group size. Each group contains a
#            consecutive run of elements whose range of coordinate
#            bounds does not exceed the group size. Note that 1) if the
#            group size is sufficiently small then some groups may be
#            empty and some elements may not be inside any group may
#            not be inside any group; 2) different groups may contain
#            different numbers of elements.
#
#              Example: To create 10 kilometre windows:
#              ``rolling_window=cf.Data(10, 'km')``.
#
#    window_weights: ordered sequence of numbers, optional
#        Specify the weights for a rolling window collapse. Each
#        non-empty group uses these weights in its collapse, and all
#        non-empty groups must have the same number elements as the
#        window weights. If *window_weights* is not set then the groups
#        take their weights from the *weights* parameter, and in this
#        case the groups may have different sizes.
#
#          Example: To define a 1-2-1 smoothing filter:
#          ``rolling_window=3, window_weights=[1, 2, 1]``.

    def collapse(self, method, axes=None, squeeze=False, mtol=1,
                 weights=None, ddof=1, a=None, i=False, group=None,
                 regroup=False, within_days=None, within_years=None,
                 over_days=None, over_years=None,
                 coordinate='mid_range', group_by='coords',
                 group_span=None, group_contiguous=None, _debug=False,
                 **kwargs):
        r'''

Collapse axes of the field.

Collapsing an axis involves reducing its size with a given (typically
statistical) method.

By default all axes with size greater than 1 are collapsed completely
with the given method. For example, to find the minumum of the data
array:

>>> g = f.collapse('min')

By default the calculations of means, standard deviations and
variances are not weighted. For example to find the mean of the data
array, non-weighted:

>>> g = f.collapse('mean')

Specific weights may be forced with the weights parameter. For example
to find the variance of the data array, weighting the X and Y axes by
cell area, the T axis linearly and leaving all other axes unweighted:

>>> g = f.collapse('variance', weights=['area', 'T'])

A subset of the axes may be collapsed. For example, to find the mean
over the time axis:

>>> f
[+1]<CF Field: air_temperature(time(12), latitude(73), longitude(96) K>
[+N][<CF Field: air_temperature(time(12), latitude(73), longitude(96) K>]
>>> g = f.collapse('T: mean')
>>> g
[+1]<CF Field: air_temperature(time(1), latitude(73), longitude(96) K>
[+N][<CF Field: air_temperature(time(1), latitude(73), longitude(96) K>]

For example, to find the maximum over the time and height axes:

>>> g = f.collapse('T: Z: max')

or, equivalently:

>>> g = f.collapse('max', axes=['T', 'Z'])

An ordered sequence of collapses over different (or the same) subsets
of the axes may be specified. For example, to first find the mean over
the time axis and subequently the standard deviation over the latitude
and longitude axes:

>>> g = f.collapse('T: mean area: sd')

or, equivalently, in two steps:

>>> g = f.collapse('mean', axes='T').collapse('sd', axes='area')

Grouped collapses are possible, whereby groups of elements along an
axis are defined and each group is collapsed independently. The
collapsed groups are concatenated so that the collapsed axis in the
output field has a size equal to the number of groups. For example, to
find the variance along the longitude axis within each group of size
10 degrees:

>>> g = f.collapse('longitude: variance', group=cf.Data(10, 'degrees'))

Climatological statistics (a type of grouped collapse) as defined by
the CF conventions may be specified. For example, to collapse a time
axis into multiannual means of calendar monthly minima:

>>> g = f.collapse('time: minimum within years T: mean over years',
...                 within_years=cf.M())

In all collapses, missing data array elements are accounted for in the
calculation.

The following collapse methods are available, over any subset of the
axes:

=========================  =====================================================
Method                     Notes
=========================  =====================================================
Maximum                    The maximum of the values.
                           
Minimum                    The minimum of the values.
                                    
Sum                        The sum of the values.
                           
Mid-range                  The average of the maximum and the minimum of the
                           values.
                           
Range                      The absolute difference between the maximum and
                           the minimum of the values.
                           
Mean                       The unweighted mean :math:`N` values
                           :math:`x_i` is
                           
                           .. math:: \mu=\frac{1}{N}\sum_{i=1}^{N} x_i
                           
                           The weighted mean of :math:`N` values
                           :math:`x_i` with corresponding weights
                           :math:`w_i` is

                           .. math:: \hat{\mu}=\frac{1}{V_{1}}
                                                 \sum_{i=1}^{N} w_i
                                                 x_i

                           where :math:`V_{1}=\sum_{i=1}^{N} w_i`, the
                           sum of the weights.
                                
Variance                   The unweighted variance of :math:`N` values
                           :math:`x_i` and with :math:`N-ddof` degrees
                           of freedom (:math:`ddof\ge0`) is

                           .. math:: s_{N-ddof}^{2}=\frac{1}{N-ddof}
                                       \sum_{i=1}^{N} (x_i - \mu)^2

                           The unweighted biased estimate of the
                           variance (:math:`s_{N}^{2}`) is given by
                           :math:`ddof=0` and the unweighted unbiased
                           estimate of the variance using Bessel's
                           correction (:math:`s^{2}=s_{N-1}^{2}`) is
                           given by :math:`ddof=1`.

                           The weighted biased estimate of the
                           variance of :math:`N` values :math:`x_i`
                           with corresponding weights :math:`w_i` is

                           .. math:: \hat{s}_{N}^{2}=\frac{1}{V_{1}}
                                                     \sum_{i=1}^{N}
                                                     w_i(x_i -
                                                     \hat{\mu})^{2}
                                
                           The corresponding weighted unbiased
                           estimate of the variance is
                           
                           .. math:: \hat{s}^{2}=\frac{1}{V_{1} -
                                                 (V_{1}/V_{2})}
                                                 \sum_{i=1}^{N}
                                                 w_i(x_i -
                                                 \hat{\mu})^{2}

                           where :math:`V_{2}=\sum_{i=1}^{N} w_i^{2}`,
                           the sum of the squares of weights. In both
                           cases, the weights are assumed to be
                           non-random "reliability weights", as
                           opposed to frequency weights.
                               
Standard deviation         The variance is the square root of the variance.

Sample size                The sample size, :math:`N`, as would be used for 
                           other statistical calculations.
                           
Sum of weights             The sum of sample weights, :math:`V_{1}`,
                           as would be used for other statistical
                           calculations.

Sum of squares of weights  The sum of squares of sample weights,
                           :math:`V_{2}`, as would be used for other
                           statistical calculations.
=========================  =====================================================


.. versionadded:: 1.0

.. seealso:: `cell_area`, `weights`, `max`, `mean`, `mid_range`,
             `min`, `range`, `sample_size`, `sd`, `sum`, `var`


:Parameters:

    method: `str`
        Define the collapse method. All of the axes specified by the
        *axes* parameter are collapsed simultaneously by this
        method. The method is given by one of the following strings:

          ========================================  =========================
          *method*                                  Description
          ========================================  =========================
          ``'max'`` or ``'maximum'``                Maximum                  
          ``'min'`` or ``'minimum'``                Minimum                      
          ``'sum'``                                 Sum                      
          ``'mid_range'``                           Mid-range                
          ``'range'``                               Range                    
          ``'mean'`` or ``'average'`` or ``'avg'``  Mean                         
          ``'var'`` or ``'variance'``               Variance                 
          ``'sd'`` or ``'standard_deviation'``      Standard deviation       
          ``'sample_size'``                         Sample size                      
          ``'sum_of_weights'``                      Sum of weights           
          ``'sum_of_weights2'``                     Sum of squares of weights
          ========================================  =========================

        An alternative form is to provide a CF cell methods-like
        string. In this case an ordered sequence of collapses may be
        defined and both the collapse methods and their axes are
        provided. The axes are interpreted as for the *axes*
        parameter, which must not also be set. For example:
          
        >>> g = f.collapse('time: max (interval 1 hr) X: Y: mean dim3: sd')
        
        is equivalent to:
        
        >>> g = f.collapse('max', axes='time')
        >>> g = g.collapse('mean', axes=['X', 'Y'])
        >>> g = g.collapse('sd', axes='dim3')    

        Climatological collapses are carried out if a *method* string
        contains any of the modifiers ``'within days'``, ``'within
        years'``, ``'over days'`` or ``'over years'``. For example, to
        collapse a time axis into multiannual means of calendar
        monthly minima:

        >>> g = f.collapse('time: minimum within years T: mean over years',
        ...                 within_years=cf.M())
          
        which is equivalent to:
          
        >>> g = f.collapse('time: minimum within years', within_years=cf.M())
        >>> g = g.collapse('mean over years', axes='T')

    axes, kwargs: optional  
        The axes to be collapsed. The axes are those that would be
        selected by this call of the field's `axes` method:
        ``f.axes(axes, **kwargs)``. See `cf.Field.axes` for
        details. If an axis has size 1 then it is ignored. By default
        all axes with size greater than 1 are collapsed. If *axes* has
        the special value ``'area'`` then it is assumed that the X and
        Y axes are intended.

          *Example:*

            ``axes='area'`` is equivalent to ``axes=['X',
            'Y']``. ``axes=['area', Z']`` is equivalent to
            ``axes=['X', 'Y', 'Z']``.

    weights: optional
        Specify the weights for the collapse. **By default the
        collapse is unweighted**. The weights are those that would be
        returned by this call of the field's `~cf.Field.weights`
        method: ``f.weights(weights, components=True)``. See
        `cf.Field.weights` for details.  By default *weights* is
        `None` (``f.weights(None, components=True)`` creates equal
        weights for all elements).

          *Example:*
            To specify weights based on cell areas use
            ``weights='area'``.

          *Example:*
            To specify weights based on cell areas and linearly in
            time you could set ``weights=('area', 'T')``.

          *Example:*
            To automatically detect the best weights available for all
            axes from the metadata: ``weights='auto'``. See
            `cf.Field.weights` for details on how the weights are
            derived in this case.

    squeeze: `bool`, optional
        If True then size 1 collapsed axes are removed from the output
        data array. By default the axes which are collapsed are
        retained in the result's data array.

    mtol: number, optional        
        Set the fraction of input array elements which is allowed to
        contain missing data when contributing to an individual output
        array element. Where this fraction exceeds *mtol*, missing
        data is returned. The default is 1, meaning that a missing
        datum in the output array only occurs when its contributing
        input array elements are all missing data. A value of 0 means
        that a missing datum in the output array occurs whenever any
        of its contributing input array elements are missing data. Any
        intermediate value is permitted.

          *Example:*
            To ensure that an output array element is a missing datum
            if more than 25% of its input array elements are missing
            data: ``mtol=0.25``.

    ddof: number, optional
        The delta degrees of freedom in the calculation of a standard
        deviation or variance. The number of degrees of freedom used
        in the calculation is (N-*ddof*) where N represents the number
        of non-missing elements. By default *ddof* is 1, meaning the
        standard deviation and variance of the population is estimated
        according to the usual formula with (N-1) in the denominator
        to avoid the bias caused by the use of the sample mean
        (Bessel's correction).

    coordinate: `str`, optional
        Set how the cell coordinate values for collapsed axes are
        defined. This has no effect on the cell bounds for the
        collapsed axes, which always represent the extrema of the
        input coordinates. Valid values are:

          ===============  ===========================================
          *coordinate*     Description
          ===============  ===========================================        
          ``'mid_range'``  An output coordinate is the average of the
                           first and last input coordinate bounds (or
                           the first and last coordinates if there are
                           no bounds). This is the default.
                           
          ``'min'``        An output coordinate is the minimum of the
                           input coordinates.
                           
          ``'max'``        An output coordinate is the maximum of the
                           input coordinates.
          ===============  ===========================================
       
    group: optional        
        Independently collapse groups of axis elements. Upon output,
        the results of the collapses are concatenated so that the
        output axis has a size equal to the number of groups. The
        *group* parameter defines how the elements are partitioned
        into groups, and may be one of:

          * A `cf.Data` defining the group size in terms of ranges of
            coordinate values. The first group starts at the first
            coordinate bound of the first axis element (or its
            coordinate if there are no bounds) and spans the defined
            group size. Each susbsequent group immediately follows the
            preceeeding one. By default each group contains the
            consective run of elements whose coordinate values lie
            within the group limits (see the *group_by* parameter).

              *Example:*
                To define groups of 10 kilometres: ``group=cf.Data(10,
                'km')``.

              *Note:*
                * By default each element will be in exactly one group
                  (see the *group_by*, *group_span* and
                  *group_contiguous* parameters).
                * By default groups may contain different numbers of
                  elements.
                * If no units are specified then the units of the
                  coordinates are assumed.

        ..

          * A `cf.TimeDuration` defining the group size in terms of
            calendar months and years or other time intervals. The
            first group starts at or before the first coordinate bound
            of the first axis element (or its coordinate if there are
            no bounds) and spans the defined group size. Each
            susbsequent group immediately follows the preceeeding
            one. By default each group contains the consective run of
            elements whose coordinate values lie within the group
            limits (see the *group_by* parameter).

              *Example:*
                To define groups of 5 days, starting and ending at
                midnight on each day: ``group=cf.D(5)`` (see `cf.D`).

              *Example:*
                To define groups of 1 calendar month, starting and
                ending at day 16 of each month: ``group=cf.M(day=16)``
                (see `cf.M`).

              *Note:*
                * By default each element will be in exactly one group
                  (see the *group_by*, *group_span* and
                  *group_contiguous* parameters).
                * By default groups may contain different numbers of
                  elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.Y(month=12)`` then the first group will
                  start on the closest 1st December to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each
            maximally consecutive run within these elements.

              *Example:*
                To define groups of the season MAM in each year:
                ``group=cf.mam()`` (see `cf.mam`).
              
              *Example:*
                To define groups of the seasons DJF and JJA in each
                year: ``group=[cf.jja(), cf.djf()]``. To define groups
                for seasons DJF, MAM, JJA and SON in each year:
                ``group=cf.seasons()`` (see `cf.djf`, `cf.jja` and
                `cf.season`).
              
              *Example:*
                To define groups for longitude elements less than or
                equal to 90 degrees and greater than 90 degrees:
                ``group=[cf.le(90, 'degrees'), cf.gt(90, 'degrees')]``
                (see `cf.le` and `cf.gt`).

              *Note:*
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * By default groups may contain different numbers of
                  elements.
                * If no units are specified then the units of the
                  coordinates are assumed.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

        .. 

          * An `int` defining the number of elements in each
            group. The first group starts with the first axis element
            and spans the defined number of consecutive elements. Each
            susbsequent group immediately follows the preceeeding
            one.

              *Example:*
                To define groups of 5 elements: ``group=5``.

              *Note:*
                * By default each group has the defined number of
                  elements, apart from the last group which may
                  contain fewer elements (see the *group_span*
                  parameter).

        .. 

          * A `numpy.array` of integers defining groups. The array
            must have the same length as the axis to be collapsed and
            its sequence of values correspond to the axis
            elements. Each group contains the elements which
            correspond to a common non-negative integer value in the
            numpy array. Upon output, the collapsed axis is arranged
            in order of increasing group number. See the *regroup*
            parameter, which allows the creation of such a
            `numpy.array` for a given grouped collapse.

              *Example:*
                For an axis of size 8, create two groups, the first
                containing the first and last elements and the second
                containing the 3rd, 4th and 5th elements, whilst
                ignoring the 2nd, 6th and 7th elements:
                ``group=numpy.array([0, -1, 4, 4, 4, -1, -2, 0])``.

              *Note:* 
                * The groups do not have to be in runs of consective
                  elements; they may be scattered throughout the axis.
                * An element which corresponds to a negative integer
                  in the array will not be in any group.

    group_by: `str`, optional
        Specify how coordinates are assigned to the groups defined by
        the *group*, *within_days* or *within_years*
        parameter. Ignored unless one of these parameters is a
        `cf.Data` or `cf.TimeDuration` object. The *group_by*
        parameter may be one of:

          * ``'coords'``. This is the default. Each group contains the
            axis elements whose coordinate values lie within the group
            limits. Every element will be in a group.

        ..

          * ``'bounds'``. Each group contains the axis elements whose
            upper and lower coordinate bounds both lie within the
            group limits. Some elements may not be inside any group,
            either because the group limits do not coincide with
            coordinate bounds or because the group size is
            sufficiently small.

    group_span: optional
        Ignore groups whose span is less than a given value. By
        default all groups are collapsed, regardless of their
        size. Groups are defined by the *group*, *within_days* or
        *within_years* parameter.

        In general, the span of a group is the absolute difference
        between the lower bound of its first element and the upper
        bound of its last element. The only exception to this occurs
        if *group_span* is an `int`, in which case the span of a group
        is the number of elements in the group.

          *Note:*
            * To also ensure that elements within a group are
              contiguous, use the *group_contiguous* parameter.

        The *group_span* parameter may be one of:

          * `True`. Ignore groups whose span is less than the size
            defined by the *group* parameter. Only applicable if the
            *group* parameter is a `cf.Data`, `cf.TimeDuration` or
            `int`. If the *group* parameter is a (sequence of)
            `cf.Query` then one of the other options is required.

              *Example:*
                To collapse into groups of 10 km, ignoring any groups
                that span less than that distance: ``group=cf.Data(10,
                'km'), group_span=True``.

              *Example:*
                To collapse a daily timeseries into monthly groups,
                ignoring any groups that span less than 1 calendar
                month: monthly values: ``group=cf.M(),
                group_span=True`` (see `cf.M`).

        ..

          * `cf.Data`. Ignore groups whose span is less than the given
            size. If no units are specified then the units of the
            coordinates are assumed.

        ..
            
          * `cf.TimeDuration`. Ignore groups whose span is less than
            the given time duration.

              *Example:*
                To collapse a monthly timeseries into seasonal groups,
                ignoring any groups that contain fewer than three
                monthly values: ``group=cf.seasons(),
                group_span=cf.M(3)`` (see `cf.seasons` and `cf.M`).

        ..
            
          * `int`. Ignore groups that contain fewer than the given
            number of elements.

    group_contiguous: `int`, optional
        If set to 1 or 2 then ignore groups whose cells are not
        contiguous along the collapse axis. By default,
        *group_contiguous* is 0, meaning that non-contiguous groups
        are allowed. The *group_contiguous* parameter is only allowed
        for grouped collapses (i.e. if the *group*, *within_days* or
        *within_years* parameter is set) and may be one of:

          ===================  =======================================
          *group_contiguous*  Description
          ===================  =======================================
          ``0``                Allow non-contiguous groups.

          ``1``                Ignore non-contiguous groups, as well
                               as contiguous groups with overlapping
                               cells.

          ``2``                Ignore non-contiguous groups, but allow
                               contiguous groups with overlapping
                               cells.
          ===================  =======================================

          *Example:*
            To ignore non-contiguous groups, as well as any contiguous
            group with overlapping cells: ``group_contiguous=1``.

    regroup: `bool`, optional
        For grouped collapses, return a `numpy.array` of integers
        which identifies the groups defined by the *group*
        parameter. The array is interpreted as for a numpy array value
        of the *group* parameter, and thus may subsequently be used by
        *group* parameter in a separate collapse. For example:

        >>> groups = f.collapse('time: mean', group=10, regroup=True)
        >>> g = f.collapse('time: mean', group=groups)

        is equivalent to:

        >>> g = f.collapse('time: mean', group=10)

    within_days: optional
        Independently collapse groups of reference-time axis elements
        for CF "within days" climatological statistics. Each group
        contains elements whose coordinates span a time interval of up
        to one day. Upon output, the results of the collapses are
        concatenated so that the output axis has a size equal to the
        number of groups.

        *Note:*
          For CF compliance, a "within days" collapse should be
          followed by an "over days" collapse.

        The *within_days* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * A `cf.TimeDuration` defining the group size in terms of a
            time interval of up to one day. The first group starts at
            or before the first coordinate bound of the first axis
            element (or its coordinate if there are no bounds) and
            spans the defined group size. Each susbsequent group
            immediately follows the preceeeding one. By default each
            group contains the consective run of elements whose
            coordinate values lie within the group limits (see the
            *group_by* parameter).

              *Example:*
                To define groups of 6 hours, starting at 00:00, 06:00,
                12:00 and 18:00: ``within_days=cf.h(6)`` (see `cf.h`).

              *Example:*
                To define groups of 1 day, starting at 06:00:
                ``within_days=cf.D(1, hour=6)`` (see `cf.D`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.D(hour=12)`` then the first group will
                  start on the closest midday to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each
            maximally consecutive run within these elements.

              *Example:*
                To define groups of 00:00 to 06:00 within each day,
                ignoring the rest of each day:
                ``within_days=cf.hour(cf.le(6))`` (see `cf.hour` and
                `cf.le`).

              *Example:*
                To define groups of 00:00 to 06:00 and 18:00 to 24:00
                within each day, ignoring the rest of each day:
                ``within_days=[cf.hour(cf.le(6)),
                cf.hour(cf.gt(18))]`` (see `cf.gt`, `cf.hour` and
                `cf.le`).

              *Note:*
                * Groups may contain different numbers of elements.
                * If no units are specified then the units of the
                  coordinates are assumed.
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

    within_years: optional 
        Independently collapse groups of reference-time axis elements
        for CF "within years" climatological statistics. Each group
        contains elements whose coordinates span a time interval of up
        to one calendar year. Upon output, the results of the
        collapses are concatenated so that the output axis has a size
        equal to the number of groups.

          *Note:*
            For CF compliance, a "within years" collapse should be
            followed by an "over years" collapse.

        The *within_years* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * A `cf.TimeDuration` defining the group size in terms of a
            time interval of up to one calendar year. The first group
            starts at or before the first coordinate bound of the
            first axis element (or its coordinate if there are no
            bounds) and spans the defined group size. Each susbsequent
            group immediately follows the preceeeding one. By default
            each group contains the consective run of elements whose
            coordinate values lie within the group limits (see the
            *group_by* parameter).

              *Example:*
                To define groups of 90 days: ``within_years=cf.D(90)``
                (see `cf.D`).

              *Example:*  
                To define groups of 3 calendar months, starting on the
                15th of a month: ``within_years=cf.M(3, day=15)`` (see
                `cf.M`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.Y(month=12)`` then the first group will
                  start on the closest 1st December to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each
            maximally consecutive run within these elements.

              *Example:*
                To define groups for the season MAM within each year:
                ``within_years=cf.mam()`` (see `cf.mam`).

              *Example:*
                To define groups for February and for November to
                December within each year:
                ``within_years=[cf.month(2), cf.month(cf.ge(11))]``
                (see `cf.month` and `cf.ge`).

              *Note:*
                * The first group may start outside of the range of
                  coordinates (the start of the first group is
                  controlled by parameters of the `cf.TimeDuration`).
                * If group boundaries do not coincide with coordinate
                  bounds then some elements may not be inside any
                  group.
                * If the group size is sufficiently small then some
                  elements may not be inside any group.
                * Groups may contain different numbers of elements.

    over_days: optional
        Independently collapse groups of reference-time axis elements
        for CF "over days" climatological statistics. Each group
        contains elements whose coordinates are **matching**, in that
        their lower bounds have a common time of day but different
        dates of the year, and their upper bounds also have a common
        time of day but different dates of the year. Upon output, the
        results of the collapses are concatenated so that the output
        axis has a size equal to the number of groups.

          *Example:*
            An element with coordinate bounds {1999-12-31 06:00:00,
            1999-12-31 18:00:00} **matches** an element with
            coordinate bounds {2000-01-01 06:00:00, 2000-01-01
            18:00:00}.

          *Example:*
            An element with coordinate bounds {1999-12-31 00:00:00,
            2000-01-01 00:00:00} **matches** an element with
            coordinate bounds {2000-01-01 00:00:00, 2000-01-02
            00:00:00}.

          *Note:*       
            * A *coordinate* parameter value of ``'min'`` is assumed,
              regardless of its given value.
             
            * A *group_by* parameter value of ``'bounds'`` is assumed,
              regardless of its given value.
            
            * An "over days" collapse must be preceded by a "within
              days" collapse, as described by the CF conventions. If the
              field already contains sub-daily data, but does not have
              the "within days" cell methods flag then it may be added,
              for example, as follows (this example assumes that the
              appropriate cell method is the most recently applied,
              which need not be the case; see `cf.CellMethods` for
              details):
            
              >>> f.cell_methods[-1].within = 'days'

        The *over_days* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * `None`. This is the default. Each collection of
            **matching** elements forms a group.

        ..

          * A `cf.TimeDuration` defining the group size in terms of a
            time duration of at least one day. Multiple groups are
            created from each collection of **matching** elements -
            the first of which starts at or before the first
            coordinate bound of the first element and spans the
            defined group size. Each susbsequent group immediately
            follows the preceeeding one. By default each group
            contains the **matching** elements whose coordinate values
            lie within the group limits (see the *group_by*
            parameter).

              *Example:*
                To define groups spanning 90 days:
                ``over_days=cf.D(90)`` or
                ``over_days=cf.h(2160)``. (see `cf.D` and `cf.h`).

              *Example:*
                To define groups spanning 3 calendar months, starting
                and ending at 06:00 in the first day of each month:
                ``over_days=cf.M(3, hour=6)`` (see `cf.M`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.M(day=15)`` then the first group will
                  start on the closest 15th of a month to the first
                  axis element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each subset
            of **matching** elements.

              *Example:*
                To define groups for January and for June to December,
                ignoring all other months: ``over_days=[cf.month(1),
                cf.month(cf.wi(6, 12))]`` (see `cf.month` and
                `cf.wi`).

              *Note:*
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * Groups may contain different numbers of elements.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

    over_years: optional
        Independently collapse groups of reference-time axis elements
        for CF "over years" climatological statistics. Each group
        contains elements whose coordinates are **matching**, in that
        their lower bounds have a common sub-annual date but different
        years, and their upper bounds also have a common sub-annual
        date but different years. Upon output, the results of the
        collapses are concatenated so that the output axis has a size
        equal to the number of groups.

          *Example:*
            An element with coordinate bounds {1999-06-01 06:00:00,
            1999-09-01 06:00:00} **matches** an element with
            coordinate bounds {2000-06-01 06:00:00, 2000-09-01
            06:00:00}.

          *Example:*
            An element with coordinate bounds {1999-12-01 00:00:00,
            2000-12-01 00:00:00} **matches** an element with
            coordinate bounds {2000-12-01 00:00:00, 2001-12-01
            00:00:00}.

          *Note:*       
            * A *coordinate* parameter value of ``'min'`` is assumed,
              regardless of its given value.
             
            * A *group_by* parameter value of ``'bounds'`` is assumed,
              regardless of its given value.
            
            * An "over years" collapse must be preceded by a "within
              years" or an "over days" collapse, as described by the
              CF conventions. If the field already contains sub-annual
              data, but does not have the "within years" or "over
              days" cell methods flag then it may be added, for
              example, as follows (this example assumes that the
              appropriate cell method is the most recently applied,
              which need not be the case; see `cf.CellMethods` for
              details):

              >>> f.cell_methods[-1].over = 'days'

        The *over_years* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * `None`. Each collection of **matching** elements forms a
            group. This is the default.

        ..

          * A `cf.TimeDuration` defining the group size in terms of a
            time interval of at least one calendar year. Multiple
            groups are created from each collection of **matching**
            elements - the first of which starts at or before the
            first coordinate bound of the first element and spans the
            defined group size. Each susbsequent group immediately
            follows the preceeeding one. By default each group
            contains the **matching** elements whose coordinate values
            lie within the group limits (see the *group_by*
            parameter).

              *Example:*
                To define groups spanning 10 calendar years:
                ``over_years=cf.Y(10)`` or ``over_years=cf.M(120)``
                (see `cf.M` and `cf.Y`).

              *Example:*
                To define groups spanning 5 calendar years, starting
                and ending at 06:00 on 01 December of each year:
                ``over_years=cf.Y(5, month=12, hour=6)`` (see `cf.Y`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.Y(month=12)`` then the first group will
                  start on the closest 1st December to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each subset
            of **matching** elements.

              *Example:*
                To define one group spanning 1981 to 1990 and another
                spanning 2001 to 2005:
                ``over_years=[cf.year(cf.wi(1981, 1990),
                cf.year(cf.wi(2001, 2005)]`` (see `cf.year` and
                `cf.wi`).

              *Note:*
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * Groups may contain different numbers of elements.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

    {+i}

:Returns:
 
    out: `cf.Field` or `numpy.ndarray`
       The collapsed field. Alternatively, if the *regroup* parameter
       is True then a numpy array is returned.

:Examples:

Calculate the unweighted  mean over a the entire field:

>>> g = f.collapse('mean')

Five equivalent ways to calculate the unweighted  mean over a CF latitude axis:

>>> g = f.collapse('latitude: mean')
>>> g = f.collapse('lat: avg')
>>> g = f.collapse('Y: average')
>>> g = f.collapse('mean', 'Y')
>>> g = f.collapse('mean', ['latitude'])

Three equivalent ways to calculate an area weighted mean over CF
latitude and longitude axes:

>>> g = f.collapse('area: mean', weights='area')
>>> g = f.collapse('lat: lon: mean', weights='area')
>>> g = f.collapse('mean', axes=['Y', 'X'], weights='area')

Two equivalent ways to calculate a time weighted mean over CF
latitude, longitude and time axes:

>>> g = f.collapse('X: Y: T: mean', weights='T')
>>> g = f.collapse('mean', axes=['T', 'Y', 'X'], weights='T')

Find how many non-missing elements in each group of a grouped
collapse:

>>> f.collapse('latitude: sample_size', group=cf.Data(5 'degrees'))

'''        
        copy = not i
        if copy:
            f = self.copy()
        else:
            f = self

        # Whether or not to create null bounds for null
        # collapses. I.e. if the collapse axis has size 1 and no
        # bounds, whether or not to create upper and lower bounds to
        # the coordinate value. If this occurs it's because the null
        # collapse is part of a grouped collapse and so will be
        # concatenated to other collapses for the final result: bounds
        # will be made for the grouped collapse, so all elements need
        # bounds.
        _create_zero_size_cell_bounds = kwargs.get('_create_zero_size_cell_bounds', False)

        # ------------------------------------------------------------
        # Parse the methods and axes
        # ------------------------------------------------------------
        if ':' in method:
            # Convert a cell methods string (such as 'area: mean dim3:
            # dim2: max T: minimum height: variance') to a CellMethods
            # object
            if axes is not None:
                raise ValueError(
"Can't collapse: Can't set 'axes' when 'method' is CF cell methods-like string")

            cms = CellMethods(method)
        
            all_methods = cms.method
            all_axes    = cms.axes  
            all_within  = cms.within
            all_over    = cms.over  
        else:            
            x = method.split(' within ')
            if method == x[0]:
                within = None
                x = method.split(' over ')
                if method == x[0]:
                    over = None
                else:
                    method, over = x
            else:
                method, within = x
           
            if isinstance(axes, basestring):
                axes = (axes,)

            all_methods = (method,)
            all_within  = (within,)
            all_over    = (over,)
            all_axes    = (axes,)
        #--- End: if

        input_axes = all_axes
        
        # Convert axes into axis identifiers
        all_axes2 = []
        for axes in all_axes:
            if axes is None:
                all_axes2.append(axes)
                continue

            axes2 = []
            for axis in axes:
                if axis == 'area':
                    a = self.axes(('X', 'Y'), **kwargs)
                    if len(a) != 2:
                        raise ValueError("sdf  222222")
                    axes2.extend(a)
                elif axis == 'volume':
                    a = self.axes(('X', 'Y', 'Z'), **kwargs)
                    if len(a) != 3:
                        raise ValueError("sdf 3  ")
                    axes2.extend(a)
                else:
                    a = self.axis(axis, key=True, **kwargs)
                    if a is None:
                        raise ValueError("i lhsb ouyvkjh m")
                    axes2.append(a)
            #--- End: for
            all_axes2.append(axes2)
        #--- End: for
        all_axes = all_axes2

        if _debug:
            print '    all_methods, all_axes, all_within, all_over =', \
                  all_methods, all_axes, all_within, all_over

        if group is not None and len(all_axes) > 1:
            raise ValueError(
                "Can't use group parameter for multiple collapses")

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        for method, axes, within, over in izip(all_methods, all_axes,
                                               all_within, all_over):

            method2 = _collapse_methods.get(method, None)
            if method2 is None:
                raise ValueError(
                    "Can't collapse: Unknown method: {!r}".format(method))

            method = method2

            kwargs['ordered'] = True

            collapse_axes_all_sizes = f.axes(axes, **kwargs)
            if _debug:
                print '    method                  =', method
                print '    collapse_axes_all_sizes =', collapse_axes_all_sizes

            if not collapse_axes_all_sizes:
                raise ValueError("Can't collapse: Can not identify collapse axes")

            if method not in ('sample_size', 'sum_of_weights', 'sum_of_weights2'):
                kwargs['size'] = gt(1)

            collapse_axes = f.axes(axes, **kwargs)

            if _debug:
                print '    collapse_axes           =', collapse_axes

            if not collapse_axes:
               # Do nothing if there are no collapse axes
                if _create_zero_size_cell_bounds:
                    # Create null bounds if requested
                    for axis in f.axes(axes):
                        d = f.item(axes, role='d')
                        if d and not d.hasbounds:
                            d.get_bounds(create=True, insert=True, cellsize=0)
                #--- End: if                        
                continue
    
#            if axes != (None,) and len(collapse_axes) != len(axes):
#                raise ValueError("Can't collapse: Ambiguous collapse axes")

            # Check that there are enough elements to collapse
            collapse_axes_sizes = [int(x) for x in collapse_axes.values()]
            size = reduce(operator_mul, collapse_axes_sizes, 1)
            min_size = _collapse_min_size.get(method, 1)
            if size < min_size:
                raise ValueError(
"Can't calculate {0} from fewer than {1} values".format(
    _collapse_cell_methods[method], min_size))

            if _debug:
                print '    collapse_axes_sizes     =', collapse_axes_sizes

            grouped_collapse = (within is not None or
                                over   is not None or
                                group  is not None)

            if grouped_collapse:
                if len(collapse_axes) > 1:
                    raise ValueError(
                        "Can't group collapse multiple axes simultaneously")

                # ------------------------------------------------------------
                # Calculate weights
                # ------------------------------------------------------------
                g_weights = weights
                if method in _collapse_weighted_methods:
                    g_weights = f.weights(weights, scale=True, components=True)
                    if not g_weights:
                        g_weights = None
                #--- End: if

                axis = collapse_axes.keys()[0]
                
                f = f._collapse_grouped(method,
                                        axis,
                                        within=within,
                                        over=over,
                                        within_days=within_days,
                                        within_years=within_years,
                                        over_days=over_days,
                                        over_years=over_years,
                                        group=group,
                                        group_span=group_span,
                                        group_contiguous=group_contiguous,
                                        input_axis=input_axes[0],
                                        regroup=regroup,
                                        mtol=mtol,
                                        ddof=ddof,
                                        weights=g_weights,
                                        squeeze=squeeze,
                                        coordinate=coordinate,
                                        group_by=group_by,
                                        _debug=_debug)

                if regroup:
                    # Return the numpy array
                    return f
                
                # ----------------------------------------------------
                # Update the cell methods
                # ----------------------------------------------------
                f._collapse_update_cell_methods(method=method,
                                                collapse_axes=collapse_axes,
                                                within=within,
                                                over=over,
                                                _debug=_debug)
                
                continue
            elif regroup:
                raise ValueError(
                    "Can't return an array of groups for a non-grouped collapse")

            if group_contiguous:
                raise ValueError(
"Can't collapse: Can only set group_contiguous for grouped, 'within days' or 'within years' collapses.")
            
            if group_span is not None:
                raise ValueError(
"Can't collapse: Can only set group_span for grouped, 'within days' or 'within years' collapses.")
            
#            method = _collapse_methods.get(method, None)
#            if method is None:
#                raise ValueError("uih luh hbblui")
#
#            # Check that there are enough elements to collapse
#            size = reduce(operator_mul, domain.axes_sizes(collapse_axes).values())
#            min_size = _collapse_min_size.get(method, 1)
#            if size < min_size:
#                raise ValueError(
#                    "Can't calculate %s from fewer than %d elements" %
#                    (_collapse_cell_methods[method], min_size))
    
            data_axes = f.data_axes()
            iaxes = [data_axes.index(axis) for axis in collapse_axes]

            # ------------------------------------------------------------
            # Calculate weights
            # ------------------------------------------------------------
            d_kwargs = {}
            if weights is not None:
                if method in _collapse_weighted_methods:
                    d_weights = f.weights(weights, scale=True, components=True)
                    if d_weights:
                        d_kwargs['weights'] = d_weights
                elif not equals(weights, 'auto'):  # doc this
                    for x in iaxes:
                        if (x,) in d_kwargs:
                            raise ValueError(
"Can't collapse: Can't weight {!r} collapse method".format(method))
            #--- End: if


            if method in _collapse_ddof_methods:
                d_kwargs['ddof'] = ddof

            # ========================================================
            # Collapse the data array ppp
            # ========================================================
            if _debug:
                print '    iaxes, d_kwargs =', iaxes, d_kwargs
                print '    f.Data.shape = ', f.Data.shape
            
            getattr(f.Data, method)(axes=iaxes, squeeze=squeeze, mtol=mtol,
                                    i=True, **d_kwargs)

            if _debug:
                print '    f.Data.shape = ', f.Data.shape

            if squeeze:
                # ----------------------------------------------------
                # Remove the collapsed axes from the field's list of
                # data array axes
                # ----------------------------------------------------
                f._data_axes = [axis for axis in data_axes
                                if axis not in collapse_axes]
        
            #---------------------------------------------------------
            # Update dimension coordinates, auxiliary coordinates,
            # cell measures and domain ancillaries
            # ---------------------------------------------------------
            for axis, size in collapse_axes.iteritems():
                # Ignore axes which are already size 1
                if size == 1:
                    continue
                
                # REMOVE all cell measures and domain ancillaries
                # which span this axis
                f.remove_items(role=('m', 'c'), axes=axis)
    
                # REMOVE all 2+ dimensional auxiliary coordinates
                # which span this axis
                f.remove_items(role=('a',), axes=axis, ndim=gt(1))
                    
                # REMOVE all 1 dimensional auxiliary coordinates which
                # span this axis and have different values in their
                # data array and bounds.
                #
                # KEEP, after changing their data arrays, all 1
                # dimensional auxiliary coordinates which span this
                # axis and have the same values in their data array
                # and bounds.    
                for key, aux in f.Items(role='a', axes=set((axis,)),
                                        ndim=1).iteritems():
                    if _debug:
                        print 'key, aux, name =', key, aux, aux.name()
                        
                    d = aux[0]

                    if (aux.hasbounds or 
                        (aux[:-1] != aux[1:]).any()):
                        if _debug:
                            print 'Removing auxiliary coordinate:', key
                        f.remove_item(key)
                    else:
                        # Change the data array for this auxiliary
                        # coordinate
                        aux.insert_data(d.data, copy=False)
                        if d.hasbounds:
                            aux.insert_bounds(d.bounds.data, copy=False)
                #--- End: for

                # Reset the axis size
                ncdim = f._Axes[axis].ncdim
                f._Axes[axis] = DomainAxis(1, ncdim=ncdim)

                dim = f.Items.get(axis, None)

                if _debug:
                    print 'Changing axis size to 1:', axis

                if dim is None:
                    continue

                # Create a new dimension coordinate for this axis
                if dim.hasbounds:
                    bounds = [dim.bounds.datum(0), dim.bounds.datum(-1)]
                else:
                    bounds = [dim.datum(0), dim.datum(-1)]

                units = dim.Units

                if coordinate == 'mid_range':
                    data = Data([(bounds[0] + bounds[1])*0.5], units)
                elif coordinate == 'min':
                    data = dim.data.min()
                elif coordinate == 'max':
                    data = dim.data.max()
                else:
                    raise ValueError(
"Can't collapse: Bad parameter value: coordinate={0!r}".format(coordinate))

                bounds = Data([bounds], units)

                dim.insert_data(data, bounds=bounds, copy=False)        
            #--- End: for

            # --------------------------------------------------------
            # Update the cell methods
            # --------------------------------------------------------
            if kwargs.get('_update_cell_methods', True):
                f._collapse_update_cell_methods(method,
                                                collapse_axes=collapse_axes,
                                                within=within,
                                                over=over,
                                                _debug=_debug)
        #--- End: for

        # ------------------------------------------------------------
        # Return the collapsed field (or the classification array)
        # ------------------------------------------------------------
        return f
    #--- End: def

    def _collapse_grouped(self, method, axis, within=None, over=None,
                          within_days=None, within_years=None,
                          over_days=None, over_years=None, group=None,
                          group_span=None, group_contiguous=False,
                          input_axis=None, mtol=None, ddof=None,
                          regroup=None, coordinate=None, weights=None,
                          squeeze=None, group_by=None, _debug=False):
        '''
:Parameters:

    method: `str`

    axis: `str`

    over: `str`

    within: `str`


'''
        def _ddddd(classification, n, lower, upper, increasing, coord,
                   group_by_coords, extra_condition): 
            '''
:Returns:

    out: `numpy.ndarray`, `int`, date-time, date-time

'''         
            if group_by_coords:
                q = ge(lower) & lt(upper)
            else:
                q = (ge(lower, attr='lower_bounds') & 
                     le(upper, attr='upper_bounds'))
                
            if extra_condition:
                q &= extra_condition

            index = q.evaluate(coord).array
            classification[index] = n

            if increasing:
                lower = upper 
            else:
                upper = lower

            n += 1

            return classification, n, lower, upper
        #--- End: def

        def _time_interval(classification, n,
                           coord, interval,
                           lower, upper,
                           lower_limit, upper_limit,
                           group_by,
                           extra_condition=None):
            '''

:Parameters:

    classification: `numpy.ndarray`

    n: `int`

    coord: `cf.DimensionCoordinate`

    interval: `cf.TimeDuration`

    lower: `cf.Datetime`

    upper: `cf.Datetime`

    lower_limit: `cf.Datetime`

    upper_limit: `cf.Datetime`

    group_by: `str`

    extra_condition: optional

:Returns:

    out: `numpy.ndarray`, `int`

    '''
            group_by_coords = (group_by == 'coords')

#            months  = (interval.Units == Units('calendar_months'))
#            years   = (interval.Units == Units('calendar_years'))
#            days    = (interval.Units == Units('days'))
#            hours   = (interval.Units == Units('hours'))
#            minutes = (interval.Units == Units('minutes'))
#            seconds = (interval.Units == Units('seconds'))

#            calendar = coord.Units._calendar
                
            if coord.increasing:
                # Increasing dimension coordinate 
                lower, upper = interval.bounds(lower)
                while lower <= upper_limit:
                    lower, upper = interval.interval(lower)
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, True,
                        coord, group_by_coords, extra_condition)
            else: 
                # Decreasing dimension coordinate
                lower, upper = interval.bounds(upper)
                while upper >= lower_limit:
                    lower, upper = interval.interval(upper, end=True)
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, False,
                        coord, group_by_coords, extra_condition)
            #--- End: if
                        
            return classification, n
        #--- End: def

        def _data_interval(classification, n,
                           coord, interval,
                           lower, upper,
                           lower_limit, upper_limit,
                           group_by,
                           extra_condition=None):
            '''
    :Returns:

        out: `numpy.ndarray`, `int`

    '''          
            group_by_coords = group_by == 'coords'

            if coord.increasing:
                # Increasing dimension coordinate 
                lower= lower.squeeze()
                while lower <= upper_limit:
                    upper = lower + interval 
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, True,
                        coord, group_by_coords, extra_condition)
            else: 
                # Decreasing dimension coordinate
                upper = upper.squeeze()
                while upper >= lower_limit:
                    lower = upper - interval
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, False,
                        coord, group_by_coords, extra_condition)
            #--- End: if
                        
            return classification, n
        #--- End: def

        def _selection(classification, n, coord, selection, parameter,
                       extra_condition=None):
            '''

:Parameters:

    classification: `numpy.ndarray`

    n: `int`
    
    coord: `cf.DimensionCoordinate`

    selection: sequence of `cf.Query`

    parameter: `str`
        The name of the `cf.Field.collapse` parameter which
        defined *selection*. This is used in error messages.

          *Example:*
            ``parameter='within_years'``

    extra_condition: `cf.Query`, optional

:Returns:

    out: `numpy.ndarray`, `int`

'''        
            # Create an iterator for stepping through each cf.Query in
            # the selection sequence
            try:
                iterator = iter(selection)
            except TypeError:
                raise ValueError(
                    "Can't collapse: Bad parameter value: {0}={1!r}".format(
                        parameter, selection))
            
            for c in iterator:
                if not isinstance(c, Query):
                    raise ValueError(
"Can't collapse: {0} sequence contains a non-{1} object: {2!r}".format(
    parameter, Query.__name__, c))
                                
                if extra_condition:
                    c &= extra_condition

                index = c.evaluate(coord).array

                classification[index] = n

                n += 1
            #--- End: for

            return classification, n
        #--- End: def
        
        def _discern_runs(classification):
            '''
:Parameters:

    classification: `numpy.ndarray`

:Returns:

    out: `numpy.ndarray`

    '''            
            x = numpy_where(numpy_diff(classification))[0] + 1

            if not x.size:
                if classification[0] >= 0:
                    classification[:] = 0
                return classification     

            if classification[0] >= 0:
                classification[0:x[0]] = 0

            for n, (i, j) in enumerate(zip(x[:-1], x[1:])):
                if classification[i] >= 0:
                    classification[i:j] = n+1
            #-- End: for

            if classification[x[-1]] >= 0:
                classification[x[-1]:] = n+2

            return classification
        #--- End: def

        def _tyu(coord, group_by, time_interval):
            '''

:Parameters:

    coord: `cf.Coordinate`

    group_by: `str`
        As for the *group_by* parameter of the `collapse` method.

    time_interval: `bool`
        If True then then return a tuple of `cf.Datetime` objects,
        rather than a tuple of `cf.Data` objects.

:Returns:

    out: 4-`tuple` of date-time objects

            '''
            if coord.hasbounds:
                bounds = coord.bounds                       
                lower_bounds = bounds.lower_bounds
                upper_bounds = bounds.upper_bounds               
                lower = lower_bounds[0]
                upper = upper_bounds[0]
                lower_limit = lower_bounds[-1]
                upper_limit = upper_bounds[-1]
            elif group_by == 'coords':
                if coord.increasing:
                    lower = coord.data[0]
                    upper = coord.data[-1]
                else:
                    lower = coord.data[-1]
                    upper = coord.data[0]
                    
                lower_limit = lower
                upper_limit = upper
            else:
                raise ValueError(
"Can't collapse: {0!r} coordinate bounds are required with group_by={1!r}".format(
    coord.name(''), group_by))
               
            if time_interval:
                units = coord.Units
                if units.isreftime:
                    lower       = lower.dtarray[0]
                    upper       = upper.dtarray[0]
                    lower_limit = lower_limit.dtarray[0]
                    upper_limit = upper_limit.dtarray[0]
                elif not units.istime:
                    raise ValueError(
"Can't group by {0} when coordinates have units {1!r}".format(
    TimeDuration.__name__, coord.Units))
            #--- End: if

            return (lower, upper, lower_limit, upper_limit)
        #--- End: def
    
        def _group_weights(weights, iaxis, index):
            '''
            
Subspace weights components.

    :Parameters:

        weights: `dict` or None

        iaxis: `int`

        index: `list`

    :Returns:

        out: `dict` or `None`

    :Examples: 

    >>> print weights
    None
    >>> print _group_weights(weights, 2, [2, 3, 40])
    None
    >>> print _group_weights(weights, 1, slice(2, 56))    
    None

    >>> weights
    
    >>> _group_weights(weights, 2, [2, 3, 40])
    
    >>> _group_weights(weights, 1, slice(2, 56))    


    '''
            if not isinstance(weights, dict):
                return weights

            weights = weights.copy()
            for iaxes, value in weights.iteritems():
                if iaxis in iaxes:
                    indices = [slice(None)] * len(iaxes)
                    indices[iaxes.index(iaxis)] = index
                    weights[iaxes] = value[tuple(indices)]
                    break
            #--- End: for

            return weights
        #--- End: def

        # START OF MAIN CODE        

        if _debug:
            print '    Grouped collapse:'            
            print '        method            =', repr(method)
            print '        axis              =', repr(axis)
            print '        over              =', repr(over)
            print '        within            =', repr(within)
            print '        over              =', repr(over)
            print '        within_days       =', repr(within_days)
            print '        within_years      =', repr(within_years)
            print '        over_days         =', repr(over_days)
            print '        over_years        =', repr(over_years)
            print '        regroup           =', repr(regroup)
            print '        group             =', repr(group)
            print '        group_span        =', repr(group_span)
            print '        group_contiguous =', repr(group_contiguous)
            print '        input_axis        =', repr(input_axis)

        axis_size = self.axis_size(axis)         # Size of uncollapsed axis
        iaxis     = self.data_axes().index(axis) # Integer position of collapse axis

        fl = []

        # If group, rolling window, classification, etc, do something
        # special for size one axes - either return unchanged
        # (possibly mofiying cell methods with , e.g, within_dyas', or
        # raising an exception for 'can't match', I suppose.

        classification = None

        if group is not None:
            if within is not None or over is not None:
                raise ValueError(
                    "Can't set 'group' parameter for a climatological collapse")

            if isinstance(group, numpy_ndarray):
                classification = numpy_squeeze(group.copy())
                coord = self.dim(axis)

                if classification.dtype.kind != 'i':
                    raise ValueError(
"Can't collapse: Can't group by numpy array of type {0}".format(
    classification.dtype.name))
                elif classification.shape != (axis_size,):
                    raise ValueError(
"Can't collapse: group by numpy array of integers has incorrect shape: {0}".format(
    classification.shape))

                # Set group to None
                group = None
        #-- End: if

        if group is not None:
            if isinstance(group, Query):
                group = (group,)

            if isinstance(group, (int, long)):
                # ----------------------------------------------------
                # E.g. group=3
                # ----------------------------------------------------
                coord = None
                classification = numpy_empty((axis_size,), int)
                
                start = 0
                end   = group
                n = 0
                while start < axis_size:
                    classification[start:end] = n
                    start = end
                    end  += group
                    n += 1
                #--- End: while

                if group_span is True:
                    # Use the group definition as the group span
                    group_span = group
                    
            elif isinstance(group, TimeDuration):
                # ----------------------------------------------------
                # E.g. group=cf.M()
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None:
                    raise ValueError("dddddd siduhfsuildfhsuil dhfdui ") 
                 
#                # Get the bounds
#                if not coord.hasbounds:
#                    coord = coord.copy()
#
#                bounds = coord.get_bounds(create=True, insert=True)
    
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)

                lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)

                classification, n = _time_interval(classification, 0,
                                                   coord=coord,
                                                   interval=group,
                                                   lower=lower,
                                                   upper=upper,
                                                   lower_limit=lower_limit,
                                                   upper_limit=upper_limit,
                                                   group_by=group_by)

                if group_span is True:
                    # Use the group definition as the group span
                    group_span = group
                
            elif isinstance(group, Data):
                # ----------------------------------------------------
                # Chunks of 
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None:
                    raise ValueError("dddddd siduhfsuildfhsuil dhfdui ") 
                if group.size != 1:
                    raise ValueError(
                        "Can't group by SIZE > 1")                    
                if group.Units and not group.Units.equivalent(coord.Units):
                    raise ValueError(
"Can't group by {!r} when coordinates have units {!r}".format(
    interval, coord.Units))

                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)

                group = group.squeeze()
  
                lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, False)

                classification, n = _data_interval(classification, 0,
                                                   coord=coord,
                                                   interval=group,
                                                   lower=lower,
                                                   upper=upper,
                                                   lower_limit=lower_limit,
                                                   upper_limit=upper_limit,
                                                   group_by=group_by)

                if group_span is True:
                    # Use the group definition as the group span
                    group_span = group

            else:
                # ----------------------------------------------------
                # E.g. group=[cf.month(4), cf.month(cf.wi(9, 11))]
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None:
                    coord = self.aux(axes=axis, ndim=1)
                    if coord is None:
                        raise ValueError("asdad8777787 ")
                #---End: if

                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
                
                classification, n = _selection(classification, 0,
                                               coord=coord,
                                               selection=group,
                                               parameter='group')
                
                classification = _discern_runs(classification)
                
                if group_span is True:
                    raise ValueError(
"Can't collapse: Can't set group_span=True when group={!r}".format(group))
            #--- End: if
        #--- End: if
                  
        if classification is None:
            if over == 'days': 
                # ----------------------------------------------------
                # Over days
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over days\" collapse")
                if not coord.hasbounds:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinate bounds are required for an \"over days\" collapse")

#                cell_methods = getattr(self, 'cell_methods', None)
                cell_methods = self.cell_methods
                if not cell_methods or 'days' not in cell_methods.within:
                    raise ValueError(
"Can't collapse: An 'over days' collapse must come after a 'within days' collapse")

                # Parse the over_days parameter
                if isinstance(over_days, Query):
                    over_days = (over_days,)              
                elif isinstance(over_days, TimeDuration):
                    if over_days.Units.istime and over_days < Data(1, 'day'):
                        raise ValueError(
"Can't collapse: Bad parameter value: over_days={!r}".format(over_days))
                #--- End: if
                    
                coordinate = 'min'
                
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
                
                if isinstance(over_days, TimeDuration):
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)

                bounds = coord.bounds
                lower_bounds = bounds.lower_bounds.dtarray
                upper_bounds = bounds.upper_bounds.dtarray

                HMS0 = None

#            * An "over days" collapse must be preceded by a "within
#              days" collapse, as described by the CF conventions. If the
#              field already contains sub-daily data, but does not have
#              the "within days" cell methods flag then it may be added,
#              for example, as follows (this example assumes that the
#              appropriate cell method is the most recently applied,
#              which need not be the case; see `cf.CellMethods` for
#              details):
#            
#              >>> f.cell_methods[-1].within = 'days'

                n = 0
                for lower, upper in izip(lower_bounds, upper_bounds):
                    HMS_l = (eq(lower.hour  , attr='hour') & 
                             eq(lower.minute, attr='minute') & 
                             eq(lower.second, attr='second')).addattr('lower_bounds')
                    HMS_u = (eq(upper.hour  , attr='hour') & 
                             eq(upper.minute, attr='minute') & 
                             eq(upper.second, attr='second')).addattr('upper_bounds')
                    HMS = HMS_l & HMS_u

                    if not HMS0:
                        HMS0 = HMS
                    elif HMS.equals(HMS0):
                        break

                    if over_days is None:
                        # --------------------------------------------
                        # over_days=None
                        # --------------------------------------------
                        # Over all days
                        index = HMS.evaluate(coord).array
                        classification[index] = n
                        n += 1         
                    elif isinstance(over_days, TimeDuration):
                        # --------------------------------------------
                        # E.g. over_days=cf.M()
                        # --------------------------------------------
                        classification, n = _time_interval(classification, n,
                                                           coord=coord,
                                                           interval=over_days,
                                                           lower=lower,
                                                           upper=upper,
                                                           lower_limit=lower_limit,
                                                           upper_limit=upper_limit,
                                                           group_by=group_by,
                                                           extra_condition=HMS)
                    else:
                        # --------------------------------------------
                        # E.g. over_days=[cf.month(cf.wi(4, 9))]
                        # --------------------------------------------
                        classification, n = _selection(classification, n,
                                                       coord=coord,
                                                       selection=over_days,
                                                       parameter='over_days',
                                                       extra_condition=HMS)
                        
            elif over == 'years':
                # ----------------------------------------------------
                # Over years
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over years\" collapse")
                if not coord.hasbounds:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinate bounds are required for an \"over years\" collapse")

                cell_methods = self.CellMethods
                if (not cell_methods or ('years' not in cell_methods.within and
                                         'days'  not in cell_methods.over)):
                    raise ValueError(
"Can't collapse: An \"over years\" collapse must come after a \"within years\" cell method")

                # Parse the over_years parameter
                if isinstance(over_years, Query):
                    over_years = (over_years,)
                elif isinstance(over_years, TimeDuration):
                    if over_years.Units.iscalendartime:
                        over_years.Units = Units('calendar_years')
                        if not over_years.isint or over_years < 1:
                            raise ValueError(
"Can't collapse: over_years is not a whole number of calendar years: %r" % over_years)
                    else:
                        raise ValueError(
"Can't collapse: over_years is not a whole number of calendar years: %r" % over_years)
                #--- End: if
                
                coordinate = 'min'
                
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
                
                if isinstance(over_years, TimeDuration):
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)

#                if coord.increasing:
#                    bounds_max = upper_bounds[-1]
#                else:
#                    bounds_min = lower_bounds[-1]
                 
                bounds = coord.bounds
                lower_bounds = bounds.lower_bounds.dtarray
                upper_bounds = bounds.upper_bounds.dtarray
                mdHMS0 = None
                    
                n = 0
                for lower, upper in izip(lower_bounds, upper_bounds):
                    mdHMS_l = (eq(lower.month , attr='month') & 
                               eq(lower.day   , attr='day') & 
                               eq(lower.hour  , attr='hour') & 
                               eq(lower.minute, attr='minute') & 
                               eq(lower.second, attr='second')).addattr('lower_bounds')
                    mdHMS_u = (eq(upper.month , attr='month') & 
                               eq(upper.day   , attr='day') & 
                               eq(upper.hour  , attr='hour') & 
                               eq(upper.minute, attr='minute') & 
                               eq(upper.second, attr='second')).addattr('upper_bounds')
                    mdHMS = mdHMS_l & mdHMS_u

                    if not mdHMS0:
                        mdHMS0 = mdHMS
                        if _debug:
                            print '        mdHMS0 =', repr(mdHMS0)
                        
                    elif mdHMS.equals(mdHMS0):
                        break

                    if _debug:
                        print '        mdHMS  =', repr(mdHMS)

                    if over_years is None:
                        # --------------------------------------------
                        # E.g. over_years=None
                        # --------------------------------------------
                        # Over all years
                        index = mdHMS.evaluate(coord).array
                        classification[index] = n
                        n += 1
                    elif isinstance(over_years, TimeDuration):
                        # --------------------------------------------
                        # E.g. over_years=cf.Y(2)
                        # --------------------------------------------
#                        lower_bounds = bounds.lower_bounds
#                        upper_bounds = bounds.upper_bounds               
#                        
#                        lower = lower_bounds[0].dtarray[0]
#                        upper = upper_bounds[0].dtarray[0]
#                        bounds_min = lower_bounds[-1].dtarray[0]
#                        bounds_max = upper_bounds[-1].dtarray[0]

                        classification, n = _time_interval(classification, n,
                                                           coord=coord,
                                                           interval=over_years,
                                                           lower=lower,
                                                           upper=upper,
                                                           lower_limit=lower_limit,
                                                           upper_limit=upper_limit,
                                                           group_by=group_by,
                                                           extra_condition=mdHMS)
                    else:
                        # --------------------------------------------
                        # E.g. over_years=cf.year(cf.lt(2000))
                        # --------------------------------------------
                        classification, n = _selection(classification, n,
                                                       coord=coord,
                                                       selection=over_years,
                                                       parameter='over_years',
                                                       extra_condition=mdHMS)
                #--- End: for
    
            elif within == 'days':
                # ----------------------------------------------------
                # Within days
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over years\" collapse")

                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
    
                # Parse the within_days parameter
                if isinstance(within_days, Query):
                    within_days = (within_days,)
                elif isinstance(within_days, TimeDuration):
                    if within_days.Units.istime and Data(1, 'day') % within_days:
                        raise ValueError(
"Can't collapse: within_days={!r} is not an exact factor of 1 day".format(within_days))
                #--- End: if

                if isinstance(within_days, TimeDuration):
                    # ------------------------------------------------
                    # E.g. within_days=cf.h(6)
                    # ------------------------------------------------ 
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)
                        
                    classification, n = _time_interval(classification, 0,
                                                       coord=coord,
                                                       interval=within_days,
                                                       lower=lower,
                                                       upper=upper,
                                                       lower_limit=lower_limit,
                                                       upper_limit=upper_limit,
                                                       group_by=group_by)
                    
                    if group_span is True:
                        # Use the within_days definition as the group
                        # span
                        group_span = within_days
                    
                else:
                    # ------------------------------------------------
                    # E.g. within_days=cf.hour(cf.lt(12))
                    # ------------------------------------------------
                    classification, n = _selection(classification, 0,
                                                   coord=coord,
                                                   selection=within_days,
                                                   parameter='within_days') 
                    
                    classification = _discern_runs(classification)
                           
                    if group_span is True:
                        raise ValueError(
"Can't collapse: Can't set group_span=True when within_days={!r}".format(within_days))
                    
            elif within == 'years':
                # ----------------------------------------------------
                # Within years
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for a \"within years\" collapse")

                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)

                # Parse within_years
                if isinstance(within_years, Query):
                    within_years = (within_years,)               
                elif within_years is None:
                    raise ValueError(                        
'Must set the within_years parameter for a "within years" climatalogical time collapse')

                if isinstance(within_years, TimeDuration):
                    # ------------------------------------------------
                    # E.g. within_years=cf.M()
                    # ------------------------------------------------
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)
                        
                    classification, n = _time_interval(classification, 0,
                                                       coord=coord,
                                                       interval=within_years,
                                                       lower=lower,
                                                       upper=upper,
                                                       lower_limit=lower_limit,
                                                       upper_limit=upper_limit,
                                                       group_by=group_by)

                    if group_span is True:
                        # Use the within_years definition as the group
                        # span
                        group_span = within_years
                    
                else:
                    # ------------------------------------------------
                    # E.g. within_years=cf.season()
                    # ------------------------------------------------
                    classification, n = _selection(classification, 0,
                                                   coord=coord,
                                                   selection=within_years,
                                                   parameter='within_years')
                    
                    classification = _discern_runs(classification)

                    if group_span is True:
                        raise ValueError(
"Can't collapse: Can't set group_span=True when within_years={!r}".format(within_years))
                    
            elif over is not None:
                raise ValueError(
                    "Can't collapse: Bad 'over' syntax: {0!r}".format(over))
                
            elif within is not None: 
                raise ValueError(
                    "Can't collapse: Bad 'within' syntax: {0!r}".format(within))
            #--- End: if
        #--- End: if
                 
        if classification is not None:
            #---------------------------------------------------------
            # Collapse each group
            #---------------------------------------------------------
            unique = numpy_unique(classification)
            unique = unique[numpy_where(unique >= 0)[0]]
            unique.sort()

            ignore_n = -1

            for u in unique:
                index = numpy_where(classification==u)[0].tolist()

                pc = self.subspace(**{axis: index})

                # ----------------------------------------------------
                # Ignore groups that don't meet the specified criteria
                # ----------------------------------------------------
                if over is None:
                    if group_span is not None:
                        if isinstance(group_span, (int, long)):
                            if pc.axis_size(axis) != group_span:
                                classification[index] = ignore_n
                                ignore_n -= 1
                                continue
                        else:
                            coord = pc.coord(input_axis, ndim=1)
                            if coord is None:
                                raise ValueError(
"Can't collapse: Need unambiguous 1-d coordinates when group_span={!r}".format(group_span))
  
                            if not coord.hasbounds:
                                raise ValueError(
"Can't collapse: Need unambiguous 1-d coordinate bounds when group_span={!r}".format(group_span))

                            lb = coord.bounds[ 0, 0].data
                            ub = coord.bounds[-1, 1].data
                            if coord.T:
                                lb = lb.dtarray.item()
                                ub = ub.dtarray.item()
                            
                            if not coord.increasing:
                                lb, ub = ub, lb

                            if group_span + lb != ub:
                                # The span of this group is not the
                                # same as group_span, so don't
                                # collapse it.
                                classification[index] = ignore_n
                                ignore_n -= 1
                                continue
                        #--- End: if
                    #--- End: if
            
                    if group_contiguous:
                        overlap = (group_contiguous == 2)
                        if not coord.bounds.contiguous(overlap=overlap):
                            # This group is not contiguous, so
                            # don't collapse it.
                            classification[index] = ignore_n
                            ignore_n -= 1
                            continue                        
                #--- End: if

                if regroup:
                    continue

                # ----------------------------------------------------
                # Still here? Then collapse the group
                # ----------------------------------------------------
                w = _group_weights(weights, iaxis, index)
                if _debug:
                    print '        Collapsing group', u, ':', repr(pc)

                fl.append(pc.collapse(method, axis, weights=w,
                                      mtol=mtol, ddof=ddof,
                                      coordinate=coordinate,
                                      squeeze=False, i=True,
                                      _create_zero_size_cell_bounds=True,
                                      _update_cell_methods=False))
            #--- End: for
            
            if regroup:
                # return the numpy array
                return classification

        elif regroup:
            raise ValueError("Can't return classification 2453456 ")

        # Still here?
        if not fl:
            c = 'contiguous ' if group_contiguous else ''
            s = ' spanning {}'.format(group_span) if group_span is not None else ''
            raise ValueError(
                "Can't collapse: No {}groups{} were identified".format(c, s))
            
        if len(fl) == 1:
            f = fl[0]
        else:
            # Hack to fix missing bounds!            
            for g in fl:
                try:
                    g.dim(axis).get_bounds(create=True, insert=True, copy=False)
                except:
                    pass

            # --------------------------------------------------------
            # Sort the list of collapsed fields
            # --------------------------------------------------------
            if coord is not None and coord.isdimension:
                fl.sort(key=lambda g: g.dim(axis).datum(0),
                        reverse=coord.decreasing)
                
            # --------------------------------------------------------
            # Concatenate the partial collapses
            # --------------------------------------------------------
            try:
                f = self.concatenate(fl, axis=iaxis, _preserve=False)
            except ValueError as error:
                raise ValueError("Can't collapse: {0}".format(error))
        #--- End: if
                      
        if squeeze and f.axis_size(axis) == 1:
            # Remove a totally collapsed axis from the field's
            # data array
            f.squeeze(axis, i=True)

        # ------------------------------------------------------------
        # Return the collapsed field
        # ------------------------------------------------------------
        self.__dict__ = f.__dict__
        if _debug:
            print '    End of grouped collapse'
            
        return self
    #--- End: def

    def _collapse_update_cell_methods(self, method=None,
                                      collapse_axes=None, within=None,
                                      over=None, _debug=False):
        '''

        '''
        
        # --------------------------------------------------------
        # Update the cell methods
        # --------------------------------------------------------
        if _debug:
            print '    Cell methods =', repr(self.CellMethods)
            print '        method        =', repr(method)
            print '        collapse_axes =', repr(collapse_axes)
            print '        within        =', repr(within)
            print '        over          =', repr(over)
            print '        Initial cell methods  =', repr(self.CellMethods)

        axes   = tuple(collapse_axes)
        method = _collapse_cell_methods.get(method, method)
        names  = ': '.join(self.axis_name(axis, default=axis) for axis in axes)

        string = "{0}: {1}".format(names, method)
        if within:
            cell_method = CellMethods('{0} within {1}'.format(string, within))
        elif over:
            cell_method = CellMethods('{0} over {1}'.format(string, over))
        else:
            cell_method = CellMethods(string)

        cell_method.axes = axes

        original_cell_methods = self.CellMethods
            
        if original_cell_methods:
            # There are already some cell methods
            if len(collapse_axes) == 1:
                # Only one axis has been collapsed
                key, original_domain_axis = collapse_axes.items()[0]
    
                lastcm = original_cell_methods[-1]
                lastcm_method = _collapse_cell_methods.get(lastcm.method, lastcm.method)

                if original_domain_axis.size == self.axis_size(key):
                    if (lastcm.axes == axes and
                        lastcm_method == method and
                        lastcm_method in ('mean', 'maximum', 'minimum', 'point',
                                          'sum', 'median', 'mode', 
                                          'minumum_absolute_value',
                                          'maximum_absolute_value') and                        
                        not lastcm.within and 
                        not lastcm.over):
                        # It was a null collapse (i.e. the method is
                        # the same as the last one and the size of the
                        # collapsed axis hasn't changed).
                        cell_method = None
                        if within:
                            lastcm.within = within
                        elif over:
                            lastcm.over = over
        #--- End: if
    
        if cell_method:
            self.CellMethods += cell_method

        if _debug:
            print '        Modified cell methods =', repr(self.CellMethods)
    #--- End: def

    def data_axes(self):
        '''Return the domain axes for the data array dimensions.

.. seealso:: `axes`, `axis`, `item_axes`

:Examples 1:

>>> d = f.{+name}()

:Returns:

    out: list or None
        The ordered axes of the data array. If there is no data array
        then `None` is returned.

:Examples 2:

>>> f.ndim
3
>>> f.{+name}()
['dim2', 'dim0', 'dim1']
>>> f.remove_data()
>>> print f.{+name}()
None

>>> f.ndim
0
>>> f.{+name}()
[]

        '''    
        if not self._hasData:
            return None

        return self._data_axes[:]
    #--- End: def

    def direction(self, axes=None, size=None, **kwargs):
        '''

Return True if an axis is increasing, otherwise return False.

An axis is considered to be increasing if its dimension coordinate
values are increasing in index space or if it has no dimension
coordinate.

.. seealso:: `directions`

:Parameters:

    axis: `str`
        A domain axis identifier, such as ``'dim0'``.

:Returns:

    out: `bool`
        Whether or not the axis is increasing.
        
:Examples:

>>> d['dim0'].array
array([  0  30  60])
>>> d.direction('dim0')
True
>>> d['dim1'].array
array([15])
>>> d['dim1'].bounds.array
array([  30  0])
>>> d.direction('dim1')
False
>>> d['aux1'].array
array([0, -1])
>>> d.direction('dim2')
True
>>> d['aux2'].array
array(['z' 'a'])
>>> d.direction('dim3')
True
>>> d.direction('dim4')
True

'''
        axis = self.axis(axes, size=size, key=True, **kwargs)
        if axis is None:
            return True

        return self.Items.direction(axis)
    #--- End: def

    def directions(self):
        '''

Return a dictionary mapping axes to their directions.

.. seealso:: `direction`

:Returns:

    out: `dict`
        A dictionary whose key/value pairs are axis identifiers and
        their directions.

:Examples:

>>> d.directions()
{'dim1': True, 'dim0': False}

'''
        direction = self.Items.direction

        out = {}
        for axis in self.axes():
            out[axis] = direction(axis)

        return out
    #--- End: def

    def _dump_axes(self, display=True, _level=0):
        '''Return a string containing a description of the domain axes of the
field.
    
:Parameters:
    
    display: `bool`, optional

        If False then return the description as a string. By default
        the description is printed.
    
    _level: `int`, optional

:Returns:
    
    out: `str`
        A string containing the description.
    
:Examples:

        '''
        indent1 = '    ' * _level
        indent2 = '    ' * (_level+1)

#        string = ['%sAxes:' % indent1]
        
        data_axes = self.data_axes()
        if data_axes is None:
            data_axes = ()

        axis_name = self.axis_name
        axis_size = self.axis_size

        w = sorted(["{0}Domain Axis: {1}({2})".format(indent1, axis_name(axis), size)
                    for axis, size in self.axes().iteritems()
                    if axis not in data_axes])

        x = ["{0}Domain Axis: {1}({2})".format(indent1, axis_name(axis), axis_size(axis))
             for axis in data_axes]

        string = '\n'.join(w+x)

        if display:
            print string
        else:
            return string
    #--- End: def

    def _dump_cell_methods(self, display=True, _level=0):
        '''Return a string containing a description of the cell methods of the
field.
    
:Parameters:
    
    display: `bool`, optional

        If False then return the description as a string. By default
        the description is printed.
    
    _level: `int`, optional

:Returns:
    
    out: `str`
        A string containing the description.
    
:Examples:

        '''
        indent1 = '    ' * _level
        indent2 = '    ' * (_level+1)

        data_axes = self.data_axes()
        if data_axes is None:
            data_axes = ()

        axis_name = self.axis_name
        axis_size = self.axis_size

        w = sorted(["{0}Domain Axis: {1}({2})".format(indent1, axis_name(axis), size)
                    for axis, size in self.axes().iteritems()
                    if axis not in data_axes])

        x = ["{0}Domain Axis: {1}({2})".format(indent1, axis_name(axis), axis_size(axis))
             for axis in data_axes]

        string = '\n'.join(w+x)

        if display:
            print string
        else:
            return string
    #--- End: def

    def dump(self, display=True, _level=0, _title='Field', _q='-'):
        '''A full description of the field.

The field and its components are described without abbreviation with
the exception of data arrays, which are abbreviated to their first and
last values.

:Examples 1:
        
>>> f.{+name}()

:Parameters:

    display: `bool`, optional
        If False then return the description as a string. By default
        the description is printed.

          *Example:*
            ``f.dump()`` is equivalent to ``print
            f.dump(display=False)``.

:Returns:

    out: `None` or `str`
        If *display* is True then the description is printed and
        `None` is returned. Otherwise the description is returned as a
        string.

        '''
        indent = '    '      
        indent0 = indent * _level
        indent1 = indent0 + indent

        title = '{0}{1}: {2}'.format(indent0, _title, self.name(''))

        # Append the netCDF variable name
        ncvar = getattr(self, 'ncvar', None)
        if ncvar is not None:
            title += " (ncvar%{0})".format(ncvar)

        line  = '{0}{1}'.format(indent0, ''.ljust(len(title)-_level*4, '-'))

        # Title
        string = [line, title, line]

        # Simple properties
        if self._simple_properties():
            string.append(
                self._dump_simple_properties(_level=_level,
                                             omit=('Conventions',
                                                   '_FillValue',
                                                   'missing_value')))

        # Axes
        axes = self._dump_axes(display=False, _level=_level)
        if axes:
            string.extend(('', axes))
           
        # Data
        if self._hasData:
            axis_name = self.axis_name
            axis_size = self.axis_size
            x = ['{0}({1})'.format(axis_name(axis), axis_size(axis))
                 for axis in self.data_axes()]
            string.extend(('', '{0}Data({1}) = {2}'.format(indent0,
                                                           ', '.join(x),
                                                           str(self.Data))))
        # Cell methods        
        cell_methods = self.CellMethods
        if cell_methods:
            string.append('') 
            for value in cell_methods:
                string.append(
                    value.dump(display=False, field=self, _level=_level))

        # Flags
        flags = getattr(self, 'Flags', None)
        if flags is not None:            
            string.extend(('', flags.dump(display=False, _level=_level)))

        # Field ancillaries
        for key, value in sorted(self.Items.field_ancs().iteritems()):
            string.append('') 
            string.append(
                value.dump(display=False, field=self, key=key, _level=_level))

        # Dimension coordinates
        for key, value in sorted(self.Items.dims().iteritems()):
            string.append('')
            string.append(value.dump(display=False, 
                                     field=self, key=key, _level=_level))
             
        # Auxiliary coordinates
        for key, value in sorted(self.Items.auxs().iteritems()):
            string.append('')
            string.append(value.dump(display=False, field=self, 
                                     key=key, _level=_level))
        # Domain ancillaries
        for key, value in sorted(self.Items.domain_ancs().iteritems()):
            string.append('') 
            string.append(
                value.dump(display=False, field=self, key=key, _level=_level))
               
        # Coordinate references
        for key, value in sorted(self.Items.refs().iteritems()):
            string.append('')
            string.append(
                value.dump(display=False, field=self, key=key, _level=_level))

        # Cell measures
        for key, value in sorted(self.Items.msrs().iteritems()):
            string.append('')
            string.append(
                value.dump(display=False, field=self, key=key, _level=_level))

        string.append('')
        
        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False,
               ignore=('Conventions',)):
        # Note: map(None, f, g) only works at python 2.x
        '''True if two {+variable}s are equal, False otherwise.

Two fields are equal if ...

Note that a {+variable} may be equal to a single element field list,
for example ``f.equals(f[0:1])`` and ``f[0:1].equals(f)`` are always
True.

.. seealso:: `cf.FieldList.equals`, `cf.FieldList.set_equals`

:Examples 1:

>>> b = f.{+name}(g)

:Parameters:

    other: `object`
        The object to compare for equality.

    {+atol}

    {+rtol}

    ignore_fill_value: `bool`, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback: `bool`, optional
        If True then print a traceback highlighting where the two
        {+variable}s differ.

    ignore: `tuple`, optional
        The names of CF properties to omit from the comparison. By
        default, the CF Conventions property is omitted.

:Returns: 
  
    out: `bool`
        Whether or not the two {+variable}s are equal.

:Examples 2:

>>> f.Conventions
'CF-1.0'
>>> g = f.copy()
>>> g.Conventions = 'CF-1.6'
>>> f.equals(g)
True

In the following example, two fields differ only by the long name of
their time coordinates. The traceback shows that they differ in their
domains, that they differ in their time coordinates and that the long
name could not be matched.

>>> g = f.copy()
>>> g.coord('time').long_name += ' different'
>>> f.equals(g, traceback=True)
Domain: Different coordinate: <CF Coordinate: time(12)>
Field: Different domain properties: <CF Domain: (128, 1, 12, 64)>, <CF Domain: (128, 1, 12, 64)>
False

        '''

        kwargs2 = self._parameters(locals())
        return super(Field, self).equals(**kwargs2)
    #---End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''True if two fields are equivalent, False otherwise.

Two fields are equivalent if:

  * They have the same identity, as defined by their
    `~cf.Field.identity` methods.

  * The same rank, as given by their `~cf.Field.rank` attributes.

  * Their data arrays are the same after accounting for different but
    equivalent:

    * Units

    * Number of size one dimensions (if *squeeze* is True),
    
    * Dimension directions (if *use_directions* is True) 
    
    * Dimension orders (if *transpose* is set to a dictionary).

  * Both fields' domains must have the same rankdimensionality and where a
    dimension in one field has an identity inferred a 1-d coordinate,
    the other field has a matching dimension whose identity inferred
    is inferred from a 1-d coordinate with an equivalent data array.

    * The rank, as given by their `~cf.Field.rank`

.. seealso:: `~cf.Field.equals`

:Examples 1:

>>> b = f.{+name}(g)

:Parameters:

    other: `object`
        The object to compare for equivalence.

    {+atol}

    {+rtol}

    traceback: `bool`, optional
        If True then print a traceback highlighting where the two
        {+variable}s differ.

:Returns: 

    out: `bool`
        Whether or not the two {+variable}s are equivalent.
      
:Examples 2:

>>>

        '''
        if not self.equivalent_domain(other, rtol=rtol, atol=atol,
                                      traceback=traceback):
            if traceback:
                print("%s: Nonequivalent domains: %r, %r" % 
                      (self.__class__.__name__,
                       self.domain, other.domain))
            return False

        if not self.equivalent_data(other, rtol=rtol, atol=atol,
                                    traceback=False):
            if traceback:
                print("%s: Nonequivalent data arrays: %r, %r" % 
                      (self.__class__.__name__,
                       getattr(self, 'data', None),
                       getattr(other, 'data', None)))
            return False
                
        return True
    #--- End_def

    def _equivalent_refs(self, ref0, ref1, field1, atol=None,
                         rtol=None, s=None, t=None, traceback=False):
        '''

:Parameters:
 
    ref0: `cf.CoordinateReference`

    ref1: `cf.CoordinateReference`

    field1: `cf.Field`
        The field which contains *ref1*.

:Returns:

    out: `bool`

:Examples:

>>>

        '''
        if not ref0.equivalent(ref1, rtol=rtol, atol=atol,
                               traceback=traceback):
            if traceback:
                print(
"{}: Non-equivalent coordinate references ({!r} != {!r})".format(
    self.__class__.__name__, ref0, ref1))
            return False

        # Compare the domain ancillaries
        for term, identifier0 in ref0.ancillaries.iteritems():
            if identifier0 is None:
                continue

            key0 = self.key(identifier0, exact=True, role='c')
            key1 = field1.key(ref1[term], exact=True, role='c')

            if not self._equivalent_item_data(key0, key1, field1,
                                              rtol=rtol, atol=atol,
                                              s=s, t=t,
                                              traceback=traceback):
                # add traceback
                return False
        #--- End: for

        return True
    #--- End: def

    def _equivalent_cell_methods(self, cms0, cms1, field1, atol=None,
                                 rtol=None, s=None, t=None,
                                 traceback=False):
        '''

:Parameters:
 
    cms0: `cf.CellMethods`

    cms1: `cf.CellMethods`

    field1: `cf.Field`
        The field which contains *cms1*.

:Returns:

    out: `bool`

:Examples:

>>>

        '''
        m = self.map_axes(field1)

        for cm0, cm1 in zip(cms0, cms1):
            # Check that there are the same number of axes
            axes0 = list(cm1.axes)
            axes1 = list(cm1.axes)
            if len(axes0) != len(axes1):
                if traceback:
                    print("  987 98 7")
                return False                

            argsort = []
            for axis0 in axes0:
                for axis1 in axes1:
                    if axis0 in self._Axes and axis1 in field1._Axes:
                        if axis1 == m.get(axis0, None):
                            axes1.remove(axis1)
                            argsort.append(cm1.axes.index(axis1))
                            break
                    elif axis0 in self._Axes or axis1 in field1._Axes:
                        continue
                    elif axis0 == axis1:
                        axes1.remove(axis1)
                        argsort.append(cm1.axes.index(axis1))
                    else:
                        continue
            #--- End: for

            if len(cm1.axes) != len(argsort):
                if traceback:
                    print("  oihuytv8b7fing987 98 7=========")
                return False

            cm1 = cm1.copy()
            cm1.sort(argsort=argsort)
            cm1.axes = axes0

            if not cm0.equivalent(cm1, atol=atol, rtol=rtol, traceback=traceback):
                if traceback:
                    print("  asdadsf lygb a,kjsn xliu\hn p97qiuha nljm")
                return False                
        #--- End: for
    #--- End: def

    def equivalent_data(self, other, rtol=None, atol=None, traceback=False):
        '''

Return True if two fields have equivalent data arrays.

Equivalence is defined as both fields having the same data arrays
after accounting for different but equivalent units, size one
dimensions, different dimension directions and different dimension
orders.

:Parameters:

    other: `cf.Field`

    {+atol}

    {+rtol}

    traceback: `bool`, optional
        If True then print a traceback highlighting where the two
        data arrays differ.

:Returns:

    out: `bool`
        Whether or not the two fields' data arrays are equivalent.

:Examples:

>>> f.equivalent_data(g)

'''
        if self._hasData != other._hasData:
            if traceback:
                print("%s: Only one field has data: %s, %s" %
                      (self.__class__.__name__, self._hasData, other._hasData))
            return False
        
        if not self._hasData:
            # Neither field has a data array
            return True

        if self.size != other.size:
            if traceback:
                print("%s: Different data array sizes (%d, %d)" %
                      (self.__class__.__name__, self.size, other.size))
            return False

        s = self.analyse_items()
        t = other.analyse_items()

        data0 = self.data
        data1 = other.data
        if 1 in data0._shape:
            data0 = data0.squeeze()
            
        copy = True
        if 1 in data1._shape:
            data1 = data1.squeeze()
            copy = False

        data_axes0 = self.data_axes()
        data_axes1 = other.data_axes()

        transpose_axes = []
        for axis0 in data_axes0:
            axis1 = t['id_to_axis'].get(s['axis_to_id'][axis0], None)
            if axis1 is not None:
                transpose_axes.append(data_axes1.index(axis1))
            else:
                if traceback:
                    print("%s: woooooooooooooooo" % self.__class__.__name__)
                return False
        #--- End: for
       
        if transpose_axes != range(other.ndim):
            if copy:
                data1 = data1.copy()
                copy = False

            data1.transpose(transpose_axes, i=True)
        #--- End: if

        if self.size > 1:            
            self_directions  = self.directions()
            other_directions = other.directions()

            flip_axes = [i for i, (axis1, axis0) in enumerate(izip(data_axes1,
                                                                   data_axes0))
                         if other_directions[axis1] != self_directions[axis0]]
        
            if flip_axes:
                if copy:
                    data1 = data1.copy()                
                    copy = False

                data1.flip(flip_axes, i=True)
        #--- End: if

        return data0.equals(data1, rtol=rtol, atol=atol, ignore_fill_value=True)
    #--- End: def

    def expand_dims(self, position=0, axes=None, i=False, **kwargs):
        '''Insert a size 1 axis into the data array.

By default default a new size 1 axis is inserted which doesn't yet
exist, but a unique existing size 1 axis which is not already spanned
by the data array may be selected.

.. seealso:: `axes`, `flip`, `squeeze`, `transpose`, `unsqueeze`

:Examples 1:

>>> g = f.{+name}()
>>> g = f.{+name}(2, axes='T')

:Parameters:

    position: `int`, optional
        Specify the position that the new axis will have in the data
        array. By default the new axis has position 0, the slowest
        varying position.

    {+axes, kwargs}

    {+i}

:Returns:

    out: `cf.{+Variable}`
        The expanded field.

:Examples 2:

        '''
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('expand_dims', kwargs2)

        if axes is None and not kwargs:
            axis = None
        else:
            axis = self.axis(axes, key=True, **kwargs)
            if axis is None:
                raise ValueError("Can't identify a unique axis to insert")
            elif self.axis_size(axis) != 1:
                raise ValueError(
"Can't insert an axis of size {0}: {0!r}".format(self.axis_size(axis), axis))
            elif axis in self.data_axes():
                raise ValueError(
                    "Can't insert a duplicate axis: %r" % axis)
        #--- End: if
       
        # Expand the dims in the field's data array
        f = super(Field, self).expand_dims(position, i=i)

        if axis is None:
            axis = f.insert_axis(DomainAxis(1))

        f._data_axes.insert(position, axis)

        return f
    #--- End: def

    def indices(self, *args, **kwargs):
        '''Create indices based on domain metadata that define a subspace of
the field.

The subspace is defined in "domain space" via data array values of its
domain items: dimension coordinate, auxiliary coordinate, cell
measure, domain ancillary and field ancillary objects.

If metadata items are not specified for an axis then a full slice
(``slice(None)``) is assumed for that axis.

Values for size 1 axes which are not spanned by the field's data array
may be specified, but only indices for axes which span the field's
data array will be returned.

The conditions may be given in any order.

.. seealso:: `where`, `subspace`

:Parameters:

    args: *optional*

        ==============  ==============================================
        *arg*           Description
        ==============  ==============================================
        ``'exact'``     Keyword parameter names are not treated as
                        abbreviations of item identities. By default,
                        keyword parameter names are allowed to be
                        abbreviations of item identities.

        ``'compress'``

        ``'envelope'``

        ``'full'``
        ==============  ==============================================

    kwargs: *optional*
        Keyword parameters identify items of the domain (such as a
        particular coordinate type) and its value sets conditions on
        their data arrays (e.g. the actual coordinate values). Indices
        are created which, for each axis, select where the conditions
        are met.

        A keyword name is a string which selects a unique item of the
        field. The string may be any string value allowed by the
        *description* parameter of the field's `item` method, which is
        used to select a unique domain item. See `cf.Field.item` for
        details.
        
          *Example:*           
            The keyword ``lat`` will select the item returned by
            ``f.item('lat', role='dam')``. See the *exact* parameter.

        In general, a keyword value specifies a test on the selected
        item's data array which identifies axis elements. The returned
        indices for this axis are the positions of these elements.

          *Example:*
            To create indices for the northern hemisphere, assuming
            that there is a coordinate with identity "latitude":
            ``f.indices(latitude=cf.ge(0))``

          *Example:*
            To create indices for the northern hemisphere, identifying
            the latitude coordinate by its long name:
            ``f.indices(**{'long_name:latitude': cf.ge(0)})``. In this
            case it is necessary to use the ``**`` syntax because the
            ``:`` character is not allowed in keyword parameter names.

        If the value is a `slice` object then it is used as the axis
        indices, without testing the item's data array.

          *Example:*
            To create indices for every even numbered element along
            the "Z" axis: ``f.indices(Z=slice(0, None, 2))``.


        **Multidimensional items**
          Indices based on items which span two or more axes are
          possible if the result is a single element index for each of
          the axes spanned. In addition, two or more items must be
          provided, each one spanning the same axes  (in any order).

            *Example:*          
              To create indices for the unique location 45 degrees
              north, 30 degrees east when latitude and longitude are
              stored in 2-dimensional auxiliary coordiantes:
              ``f.indices(latitude=45, longitude=30)``. Note that this
              example would also work if latitude and longitude were
              stored in 1-dimensional dimensional or auxiliary
              coordinates, but in this case the location would not
              have to be unique.

    exact: `str`, *optional*

:Returns:

    out: `tuple`
        
:Examples:

These examples use the following field, which includes a dimension
coordinate object with no identity (``ncvar:model_level_number``) and
which has a data array which doesn't span all of the domain axes:


>>> print f
eastward_wind field summary
---------------------------
Data           : eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1
Cell methods   : time: mean
Axes           : time(3) = [1979-05-01 12:00:00, ..., 1979-05-03 12:00:00] gregorian
               : air_pressure(5) = [850.0, ..., 50.0] hPa
               : grid_longitude(106) = [-20.54, ..., 25.66] degrees
               : grid_latitude(110) = [23.32, ..., -24.64] degrees
Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_N
               : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_E
Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>


>>> f.indices(lat=23.32, lon=-20.54)
(slice(0, 3, 1), slice(0, 5, 1), slice(0, 1, 1), slice(0, 1, 1))

>>> f.indices(grid_lat=slice(50, 2, -2), grid_lon=[0, 1, 3, 90]) 
(slice(0, 3, 1), slice(0, 5, 1), slice(50, 2, -2), [0, 1, 3, 90])

>>> f.indices('exact', grid_latitude=slice(50, 2, -2), grid_longitude=[0, 1, 3, 90]) 
(slice(0, 3, 1), slice(0, 5, 1), slice(50, 2, -2), [0, 1, 3, 90])

>>> f.indices(grid_lon=cf.wi(0, 10, 'degrees'), air_pressure=850)
(slice(0, 3, 1), slice(0, 1, 1), slice(0, 110, 1), slice(47, 70, 1))

>>> f.indices(grid_lon=cf.wi(0, 10), air_pressure=cf.eq(85000, 'Pa')
(slice(0, 3, 1), slice(0, 1, 1), slice(0, 110, 1), slice(47, 70, 1))

>>> f.indices(grid_long=cf.gt(0, attr='lower_bounds'))
(slice(0, 3, 1), slice(0, 5, 1), slice(0, 110, 1), slice(48, 106, 1))

        '''
        exact    = 'exact' in args
        envelope = 'envelope' in args
        full     = 'full' in args
        compress = 'compress' in args or not (envelope or full)
        _debug   = '_debug' in args

        if _debug:
            print 'Field.indices:'
            print '    exact, envelope, full, compress =', exact, envelope, full, compress

        auxiliary_mask = []
        
        data_axes = self.data_axes()

        # Initialize indices
        indices = [slice(None)] * self.ndim
        
        parsed = {}
        unique_axes = set()
        n_axes = 0
        for identity, value in kwargs.iteritems():
            key, item = self.key_item(identity, role=('d', 'a', 'm', 'c'), exact=exact)
            if key is None:
                raise ValueError(
"Can't find indices: Ambiguous axis or axes: {}".format(identity))

            axes = self.item_axes(key)
            sorted_axes = tuple(sorted(axes))
            if sorted_axes not in parsed:
                n_axes += len(sorted_axes)

            parsed.setdefault(sorted_axes, []).append(
                (axes, key, item, value))

            unique_axes.update(sorted_axes)
        #--- End: for

        if len(unique_axes) < n_axes:
            raise ValueError(
                "Can't find indices: Ambiguous axis identification")

        for sorted_axes, axes_key_item_value in parsed.iteritems():
            axes, keys, items, points = zip(*axes_key_item_value)

            n_items = len(items)
            n_axes  = len(sorted_axes)

            if n_items > n_axes:
                if n_axes == 1:
                    a = 'axis'
                else:
                    a = 'axes'
                raise IndexError(
                    "Error: Can't specify {} conditions for {} {}: {}".format(
                        N_items, n_axes, a, points))

            create_mask = False

            if n_axes == 1:
                #-----------------------------------------------------
                # 1-d item
                #-----------------------------------------------------
                ind = None
                
                if _debug:
                    print '    {} 1-d items: {!r}'.format(n_items, items)

                item_axes = axes[0]
                axis  = item_axes[0]
                item  = items[0]
                value = points[0]

                if _debug:
                    print '    axis =', repr(axis)
                
                if isinstance(value, (list, slice, tuple, numpy_ndarray)):
                    # 1-d CASE 1: Value is already an index, e.g. [0],
                    #             (0, 3), slice(0, 4, 2),
                    #             numpy.array([2, 4, 7])
                    if _debug:
                        print '    1-d CASE 1: ',
                        
                    index = value
                    
                    if envelope or full:
                        raise ValueError(
"Can't make 'full' nor 'envelope' indices from {}".format(value))
                    
                elif (isinstance(value, Query) and 
                      value.operator in ('wi', 'wo') and
                      item.isdimension and
                      self.iscyclic(sorted_axes)):
                    # 1-d CASE 2: Axis is cyclic and subspace
                    #             criterion is a 'within' or 'without'
                    #             cf.Query instance
                    if _debug:
                        print '    1-d CASE 2: ',

                    if item.increasing:
                        anchor0 = value.value[0]
                        anchor1 = value.value[1]
                    else:
                        anchor0 = value.value[1]
                        anchor1 = value.value[0]
                        
                    a = self.anchor(axis, anchor0, dry_run=True)['roll']
                    b = self.flip(axis).anchor(axis, anchor1, dry_run=True)['roll']
                    
                    size = item.size 
                    if abs(anchor1 - anchor0) >= item.period():
                        if value.operator == 'wo':
                            start = 0
                            stop  = 0
                        else:
                            start = -a
                            stop  = -a
                    elif a + b == size:
                        b = self.anchor(axis, anchor1, dry_run=True)['roll']
                        if b == a:
                            if value.operator == 'wo':
                                start= -a
                                stop = -a
                            else:
                                start = 0
                                stop  = 0
                        else:
                            if value.operator == 'wo':
                                start= 0
                                stop = 0
                            else:
                                start = -a
                                stop  = -a
                    else:
                        if value.operator == 'wo':
                            start = b - size
                            stop  = -a + size
                        else:
                            start = -a
                            stop  = b - size
    
                    index = slice(start, stop, 1)

                    if full:
                        index = slice(start, start+size, 1)
                        ind = (numpy_arange((stop%size)-start, size),)
                else:        
                    # 1-d CASE 3: All other 1-d cases
                    if _debug:
                        print '    1-d CASE 3: ',

                    item_match = (value == item)
                    
                    if not item_match.any():                        
                        raise IndexError(
"No {!r} axis indices found from: {}".format(identity, value))
                
                    index = numpy_asanyarray(item_match)
                    
                    if envelope or full:
                        if numpy_ma_isMA:                    
                            ind = numpy_ma_where(index)
                        else:
                            ind = numpy_where(index)

                        index = slice(None)
                #--- End: if
                if _debug:
                    print 'index =', index
                   
                # Put the index into the correct place in the list of
                # indices.
                #
                # Note that we might overwrite it later if there's an
                # auxiliary mask for this axis.
                if axis in data_axes:
                    indices[data_axes.index(axis)] = index
                                    
            else:
                #-----------------------------------------------------
                # N-d items
                #-----------------------------------------------------
                if _debug:
                    print '    {} N-d items: {!r}'.format(n_items, items)
                    print '    {} points   : {!r}'.format(len(points), points)
                    print '    field.shape =', self.shape

                # Make sure that each N-d item has the same relative
                # axis order as the field's data array.
                #
                # For example, if the data array of the field is
                # ordered T Z Y X and the item is ordered Y T then the
                # item is transposed so that it is ordered T Y. For
                # example, if the field's data array is ordered Z Y X
                # and the item is ordered X Y T (T is size 1) then
                # tranpose the item so that it is ordered Y X T.
                g = self
                data_axes = self.data_axes()
                for item_axes in axes:
                    if item_axes != data_axes:
                        g = self.transpose(data_axes, items=True)
                        break

                items = [g.item(key) for key in keys]
                if _debug:
                    print '    tranposed N-d items = {!r}'.format(items)

                item_matches = [value == item for value, item in zip(points, items)]

                item_match = item_matches.pop()
                for m in item_matches:
                    item_match &= m
                item_match = item_match.array  # LAMA alert

                if numpy_ma_isMA:                    
                    ind = numpy_ma_where(item_match)
                else:
                    ind = numpy_where(item_match)
                    
                if _debug:
                    print '    item_match  =', item_match

                bounds = [item.bounds.array[ind] for item in items
                          if item.hasbounds]

                contain = False
                if bounds:
                    points2 = []
                    for v, item in zip(points, items):  
                        if isinstance(v, Query):
                            if v.operator == 'contain':                                
                                contain = True
                                v = v.value
                            elif v.operator == 'eq':
                                v = v.value
                            else:
                                contain = False
                                break
                        #--- End: if

                        v = Data.asdata(v)
                        if v.Units:
                            v.Units = item.Units
                        
                        points2.append(v.datum())
                    #--- End: for
                #--- End: if

                if contain:
                    # The coordinates have bounds and the condition is
                    # a 'contain' cf.Query object. Check each
                    # potentially matching cell for actually including
                    # the point.
                    if n_items != 2:
                        raise IndexError(
                            "333Can't index for cell from %d-d coordinate objects" %
                            n_axes)

                    if 0 < len(bounds) < n_items:
                        raise ValueError("bounds alskdaskds")

                    # Remove grid cells if, upon closer inspection,
                    # they do actually contain the point.
                    delete = [
                        n for n, vertices in enumerate(zip(*zip(*bounds)))
                        if not matplotlib_path_Path(zip(*vertices)).contains_point(points2)
                    ]
                    if delete:
                        ind = [numpy_delete(ind_1d, delete) for ind_1d in ind]
                #--- End: if                
            #--- End: if

##                if not len(ind[0]):
##                    raise IndexError(
##"{!r} does not identify any grid cells".format(points))
##
##                mask_shape = [None] * self.ndim
##                masked_subspace_size = 1
##                ind = numpy_array(ind)
##
##                for i, (axis, start, stop) in enumerate(
##                        zip(item_axes, ind.min(axis=1), ind.max(axis=1))):
##                    if axis not in data_axes:
##                        continue
##
##                    if compress:
##                        # Create a normal (compressed) index for this axis
##                        size = stop - start + 1
##                        index = sorted(set(ind[i]))
##                    elif envelope:
##                        # Create an envelope index for this axis
##                        stop += 1
##                        size = stop - start
##                        index = slice(start, stop)
##                    elif full:
##                        # Create a full index for this axis
##                        start = 0
##                        stop = self.axis_size(axis)
##                        size = stop - start                        
##                        index = slice(start, stop)
##                    else:
##                        raise ValueError("Must have full, envelope or compress")
## 
##                    position = data_axes.index(axis)
##                    indices[position] = index
##
##                    mask_shape[position] = size
##
##                    masked_subspace_size *= size
##                    ind[i] -= start
##                #--- End: for
##
##                create_mask = ind.shape[1] < masked_subspace_size
##            #--- End: if
##
##            # --------------------------------------------------------
##            # Create an auxiliary mask for these axes
##            # --------------------------------------------------------
##            if create_mask:
##                mask = self.Data._create_auxiliary_mask_component(mask_shape,
##                                                                  ind, compress)
##                auxiliary_mask.append(mask)
##                if _debug:
##                    print '\n    create_mask =', create_mask
##                    print '    mask_shape  =', mask_shape
##                    print '    mask.shape  =', mask.shape
##                    print '    mask        =', mask.array

            if ind is not None:
                mask_shape = [None] * self.ndim
                masked_subspace_size = 1
                ind = numpy_array(ind)
                if _debug:
                    print '    ind =', ind
    
                for i, (axis, start, stop) in enumerate(
                        zip(item_axes, ind.min(axis=1), ind.max(axis=1))):
                    if axis not in data_axes:
                        continue

                    position = data_axes.index(axis)

                    if indices[position] == slice(None):
                        if compress:
                            # Create a normal (compressed) index for this axis
                            size = stop - start + 1
                            index = sorted(set(ind[i]))
                        elif envelope:
                            # Create an envelope index for this axis
                            stop += 1
                            size = stop - start
                            index = slice(start, stop)
                        elif full:
                            # Create a full index for this axis
                            start = 0
                            stop = self.axis_size(axis)
                            size = stop - start                        
                            index = slice(start, stop)
                        else:
                            raise ValueError("Must have full, envelope or compress")
    
                        indices[position] = index
                    #--- End: if

                    mask_shape[position] = size    
                    masked_subspace_size *= size
                    ind[i] -= start
                #--- End: for

                create_mask = ind.shape[1] < masked_subspace_size
            else:
                create_mask = False

            # --------------------------------------------------------
            # Create an auxiliary mask for these axes
            # --------------------------------------------------------
            if _debug:
                print '\n    create_mask =', create_mask

            if create_mask:
                mask = self.Data._create_auxiliary_mask_component(mask_shape,
                                                                  ind, compress)
                auxiliary_mask.append(mask)
                if _debug:
                    print '    mask_shape  =', mask_shape
                    print '    mask.shape  =', mask.shape
        #--- End: for

        indices = tuple(parse_indices(self.shape, tuple(indices)))

        if auxiliary_mask:
            indices = ('mask', auxiliary_mask) + indices
        
        if _debug:
            print '\n    Final indices =', indices

        # Return the tuple of indices and the auxiliary mask (which
        # may be None)
        return indices
    #--- End: def



# OLD below
                
#            if n_coords != n_axes:
#                raise IndexError(
#"Must specify {0} {0}-d items to find {0}-d indices (got {1}".format(
#    n_axes, n_coords))
#
#
#
#
#
#            if n_coords == 1:
#                #-----------------------------------------------------
#                # 1-d coordinate
#                #-----------------------------------------------------
#                coord = coords[0]
#                value = point[0]
#                axis  = axes[0][0]    
#
#                if isinstance(value, (slice, list)):
#                    # CASE 1: Subspace criterion is already a valid index
#                    # (i.e. it is a slice object or a list (of ints, but
#                    # this isn't checked for)).
#                    index = value
#    
#                elif (isinstance(value, Query) and 
#                    value.operator in ('wi', 'wo') and
#                    coord.isdimension and
#                    self.iscyclic(key)):
#                    # CASE 2: Axis is cyclic and subspace criterion is
#                    # a 'within' or 'without' cf.Query instance
#                    if coord.increasing:
#                        anchor0 = value.value[0]
#                        anchor1 = value.value[1]
#                    else:
#                        anchor0 = value.value[1]
#                        anchor1 = value.value[0]
#                        
#                    a = self.anchor(axis, anchor0, dry_run=True)['roll']
#                    b = self.flip(axis).anchor(axis, anchor1, dry_run=True)['roll']
#                    
#                    size = coord.size 
#                    if abs(anchor1 - anchor0) >= coord.period():
#                        if value.operator == 'wo':
#                            start = 0
#                            stop  = 0
#                        else:
#                            start = -a
#                            stop  = -a
#                    elif a + b == size:
#                        b = self.anchor(axis, anchor1, dry_run=True)['roll']
#                        if b == a:
#                            if value.operator == 'wo':
#                                start= -a
#                                stop = -a
#                            else:
#                                start = 0
#                                stop  = 0
#                        else:
#                            if value.operator == 'wo':
#                                start= 0
#                                stop = 0
#                            else:
#                                start = -a
#                                stop  = -a
#                    else:
#                        if value.operator == 'wo':
#                            start = b - size
#                            stop  = -a + size
#                        else:
#                            start = -a
#                            stop  = b - size
#    
#                    index = slice(start, stop, 1)
#                else:        
#                    # CASE 3: All other cases
#                    item_match = (value == coord)
#                
#                    if not item_match.any():
#                        raise IndexError(
#                            "No %r axis indices found from: %r" %
#                            (identity, value))
#                
#                    index = item_match.array
#                #--- End: if
#    
#                # Put the index in to the correct place in the list of
#                # indices
#                if axis in data_axes:
#                    indices[data_axes.index(axis)] = index
#                                    
#            else:
#                #-----------------------------------------------------
#                # N-d coordinate
#                #-----------------------------------------------------
#                
#                # Make sure that each auxiliary coordinate has the
#                # same axis order
#                coords2 = [coords[0]]
#                axes0   = axes[0]
#                for a, coord in zip(axes[1:], coords[1:]):
#                    if a != axes0:
#                        coord = coord.transpose([axes0.index(axis) for axis in a])
#
#                    coords2.append(coord)
#                #--- End: for
#                coords = coords2
#
#                item_matches = [v == c for v, c in zip(point, coords)]
#                    
#                item_match = item_matches.pop()
#                for m in item_matches:
#                    item_match &= m
# 
#                ind = numpy_where(item_match)
#
#                bounds = [coord.bounds.array[ind] for coord in coords
#                          if coord.hasbounds]
#
#                contain = False
#                if bounds:
#                    point2 = []
#                    for v, coord in zip(point, coords):  
#                        if isinstance(v, Query):
#                            if v.operator == 'contain':                                
#                                contain = True
#                                v = v.value
#                            elif v.operator == 'eq':
#                                v = v.value
#                            else:
#                                contain = False
#                                break
#                        #--- End: if
#
#                        v = Data.asdata(v)
#                        if v.Units:
#                            v.Units = coord.Units
#                        
#                        point2.append(v.datum())
#                    #--- End: for
#                #--- End: if
#
#                if contain:
#                    # The coordinates have bounds and a 'contain'
#                    # cf.Query object has been given. Check each
#                    # possibly matching cell for actully including the
#                    # point.
#                    if n_coords > 2:
#                        raise IndexError(
#                            "333Can't geasasdast index for cell from %d-d coordinate objects" %
#                            n_axes)
#
#                    if 0 < len(bounds) < n_coords:
#                        raise ValueError("bounds alskdaskds")
#
#                    n_cells = 0
#                    for cell, vertices in enumerate(zip(*zip(*bounds))):
#                        n_cells += Path(zip(*vertices)).contains_point(point2)
#                        if n_cells > 1:
#                            # The point is apparently in more than one
#                            # cell
#                            break
#                else:
#                    n_cells = len(ind[0])
#                    cell = 0
#                #--- End: if
#
#                if not n_cells:
#                    raise IndexError(
#                        "No index found for the point %r" % (point,))
#                elif n_cells > 1:
#                    raise IndexError("Multiple indices found for %r" % (point,))
#                
#                # Put the indices in to the correct place in the list
#                # of indices
#                for axis, index in zip(axes0, numpy_array(ind)[:, cell]):
#                    if axis in data_axes:
#                        indices[data_axes.index(axis)] = index
#                #--- End: for
#            #--- End: if
#        #--- End: for
#                    
##        # Loop round slice criteria
##        for identity, value in kwargs.iteritems():
##            coords = self.items(identity, role=('d', 'a'),
##                                  exact=exact)
##
##            if len(coords) != 1:
##                raise ValueError(
##                    "Can't find indices: Ambiguous axis identity: %r" %
##                    identity)
##
##            key, coord = coords.popitem()
##
##            if coord.ndim == 1:
##                axis = self.item_axes(key)[0]
##    
##                if axis in seen_axes:
##                    raise ValueError(
##                        "Can't find indices: Duplicate %r axis" % axis)
##                else:
##                    seen_axes.append(axis)
##    
##                if isinstance(value, (slice, list)):
##                    # ----------------------------------------------------
##                    # Case 1: Subspace criterion is already a valid index
##                    # (i.e. it is a slice object or a list (of ints, but
##                    # this isn't checked for)).
##                    # ----------------------------------------------------
##                    index = value
##    
##                elif (isinstance(value, Query) and 
##                    value.operator in ('wi', 'wo') and
##                    coord.isdimension and
##                    self.iscyclic(key)):
##                    # ----------------------------------------------------
##                    # Case 2: Axis is cyclic and subspace criterion is a
##                    # 'within' or 'without' cf.Query instance
##                    # ----------------------------------------------------
##                    if coord.increasing:
##                        anchor0 = value.value[0]
##                        anchor1 = value.value[1]
##                    else:
##                        anchor0 = value.value[1]
##                        anchor1 = value.value[0]
##                        
##                    a = self.anchor(axis, anchor0, dry_run=True)['roll']
##                    b = self.flip(axis).anchor(axis, anchor1, dry_run=True)['roll']
##                    
##                    size = coord.size 
##                    if abs(anchor1 - anchor0) >= coord.period():
##                        if value.operator == 'wo':
##                            start = 0
##                            stop  = 0
##                        else:
##                            start = -a
##                            stop  = -a
##                    elif a + b == size:
##                        b = self.anchor(axis, anchor1, dry_run=True)['roll']
##                        if b == a:
##                            if value.operator == 'wo':
##                                start= -a
##                                stop = -a
##                            else:
##                                start = 0
##                                stop  = 0
##                        else:
##                            if value.operator == 'wo':
##                                start= 0
##                                stop = 0
##                            else:
##                                start = -a
##                                stop  = -a
##                    else:
##                        if value.operator == 'wo':
##                            start = b - size
##                            stop  = -a + size
##                        else:
##                            start = -a
##                            stop  = b - size
##    
##                    index = slice(start, stop, 1)
##                else:        
##                    # ----------------------------------------------------
##                    # Case 3: All other cases
##                    # ----------------------------------------------------
##                    item_match = (value == coord)
##                
##                    if not item_match.any():
##                        raise IndexError(
##                            "No %r axis indices found from: %r" %
##                            (identity, value))
##                
##                    index = item_match.array
##                #--- End: if
##    
##                # Put the index in to the correct place in the list of
##                # indices
##                if axis in data_axes:
##                    indices[data_axes.index(axis)] = index
##                    
##            else:
##                axes = self.item_axes(key)[0]
##                item_match = (value == coord)
##                if not item_match.any():
##                    raise IndexError(
##                        "No %r axis indices found from: %r" %
##                        (identity, value))                    
##        #--- End: for
#
#        # Return a tuple of the indices
#        return tuple(parse_indices(self, tuple(indices), False))
#    #--- End: def

    def insert_data(self, data, axes=None, copy=True, replace=True):
        '''Insert a data array into the field.

:Examples 1:

>>> f.insert_data(d)

:Parameters:

    data: `cf.Data`
        The data array to be inserted.

    axes: sequence of `str`, optional
        A list of axis identifiers (``'dimN'``), stating the axes, in
        order, of the data array.

        The ``N`` part of each identifier should be replaced by an
        integer greater then or equal to zero such that either a) each
        axis identifier is the same as one in the field's domain, or
        b) if the domain has no axes, arbitrary integers greater then
        or equal to zero may be used, the only restriction being that
        the resulting identifiers are unique.

        If an axis of the data array already exists in the domain then
        the it must have the same size as the domain axis. If it does
        not exist in the domain then a new axis will be created.

        By default the axes will either be those defined for the data
        array by the domain or, if these do not exist, the domain axis
        identifiers whose sizes unambiguously match the data array.

    copy: `bool`, optional
        If False then the new data array is not deep copied prior to
        insertion. By default the new data array is deep copied.

    replace: `bool`, optional
        If False then raise an exception if there is an existing data
        array. By default an existing data array is replaced with
        *data*.
   
:Returns:

    `None`

:Examples 2:

>>> f.axes()
{'dim0': 1, 'dim1': 3}
>>> f.insert_data(cf.Data([[0, 1, 2]]))

>>> f.axes()
{'dim0': 1, 'dim1': 3}
>>> f.insert_data(cf.Data([[0, 1, 2]]), axes=['dim0', 'dim1'])

>>> f.axes()
{}
>>> f.insert_data(cf.Data([[0, 1], [2, 3, 4]]))
>>> f.axes()
{'dim0': 2, 'dim1': 3}

>>> f.insert_data(cf.Data(4))

>>> f.insert_data(cf.Data(4), axes=[])

>>> f.axes()
{'dim0': 3, 'dim1': 2}
>>> data = cf.Data([[0, 1], [2, 3, 4]])
>>> f.insert_data(data, axes=['dim1', 'dim0'], copy=False)

>>> f.insert_data(cf.Data([0, 1, 2]))
>>> f.insert_data(cf.Data([3, 4, 5]), replace=False)
ValueError: Can't initialize data: Data already exists
>>> f.insert_data(cf.Data([3, 4, 5]))

        '''
        if data is None:
            return

        if self._hasData and not replace:
            raise ValueError(
"Can't insert data: Data already exists and replace={}".format(replace))

        if data.isscalar:
            # --------------------------------------------------------
            # The data array is scalar
            # --------------------------------------------------------
            if axes: 
                raise ValueError(
"Can't insert data: Wrong number of axes for scalar data array: axes={}".format(axes))

            axes = []

        elif axes is not None:
            # --------------------------------------------------------
            # Axes have been set
            # --------------------------------------------------------
            axes = list(self.axes(axes, ordered=True))

            if not axes:
                # The domain has no axes: Ignore the provided axes and
                # make some up for the data array
                axes = []
                for size in data.shape:
                    axes.append(self.insert_axis(DomainAxis(size)))

                axes = axes[:]
            else:
                # The domain axes exist: Check  Ignore the provided axes and
                # make some up for the data array
                len_axes = len(axes)
                if len_axes != len(set(axes)):
                    raise ValueError(
"Can't insert data: Ambiguous axes: {}".format(axes))

                    if len_axes != data.ndim:
                        raise ValueError(
"Can't insert data: Wrong number of axes for data array: {!r}".format(axes))
                        
                for axis, size in izip(axes, data.shape):
                    axis_size = self.axis_size(axis)
                    if size != axis_size:
                        raise ValueError(
"Can't insert data: Incompatible domain size for axis {!r} ({})".format(axis, size))
                #--- End: for

        elif self.data_axes() is None:
            # --------------------------------------------------------
            # The data is not scalar and axes have not been set and
            # the domain does not have data axes defined
            #
            # => infer the axes
            # --------------------------------------------------------
            if not self.axes():
                # The domain has no axes, so make some up for the data
                # array
                axes = []
                for size in data.shape:
                    axes.append(self.insert_axis(DomainAxis(size)))

                axes = axes[:]
            else:
                # The domain already has some axes
                data_shape = data.shape
                if len(data_shape) != len(set(data_shape)):
                    raise ValueError(
"Can't insert data: Ambiguous data shape: {}. Consider setting the axes parameter.".format(
    data_shape))

                axes = []
                axis_sizes = self.axes().values()
                for n in data_shape:
                    if axis_sizes.count(n) == 1:
                        axes.append(self.axis(size=n, key=True))
                    else:
                        raise ValueError(
"Can't insert data: Ambiguous data shape: {}. Consider setting the axes parameter.".format(
    data_shape))
                 #--- End: for
        else:
            # --------------------------------------------------------
            # The data is not scalar and axes have not been set, but
            # there are data axes defined on the field.
            # --------------------------------------------------------
            axes = self.data_axes()
            if len(axes) != data.ndim:
                raise ValueError(
                    "Wrong number of axes for data array: {!r}".format(axes))
            
            for axis, size in izip(axes, data.shape):
                try:
                    self.insert_axis(DomainAxis(size), axis, replace=False)
                except ValueError:
                    raise ValueError(
"Can't insert data: Incompatible size for axis {!r}: {}".format(axis, size))
            #--- End: for
        #--- End: if

        self._data_axes = axes

        if copy:
            data = data.copy()

        self.Data = data
    #--- End: def

    def domain_mask(self, *args, **kwargs):
        '''Return a boolean field that is True where criteria are met.

.. versionadded:: 1.1

.. seealso:: `indices`, `mask`, `subspace`

:Examples 1:

Create a domain mask which is masked at all between between -30 and 30
degrees of latitude:

>>> m = f.{+name}(latitude=cf.wi(-30, 30))

:Parameters:

    args: optional

        Zero or more of :
        
        ==============  ==============================================
        *arg*           Description
        ==============  ==============================================
        ``'exact'``     Keyword parameter names are not treated as
                        abbreviations of item identities. By default,
                        keyword parameter names are allowed to be
                        abbreviations of item identities.

        ``'compress'``  

        ``'envelope'``

        ==============  ==============================================

    kwargs: optional

:Returns:

    out: `cf.{+Variable}`
        The domain mask.

:Examples 2:

        '''
        mask = self.copy(_omit_Data=True,
                         _omit_properties=True,
                         _omit_attributes=True)

        false_everywhere = Data.zeros(self.shape, dtype=bool)

        mask.insert_data(false_everywhere, axes=self.data_axes(), copy=False)

        try:
            args.remove('full')
        except ValueError:
            pass

        mask.subspace[mask.indices(*args, **kwargs)] = True

        mask.long_name = 'domain mask'

        return mask
    #--- End: def

    def match(self, description=None, items=None, rank=None, ndim=None,
              exact=False, match_and=True, inverse=False):
        '''Test whether or not the field satisfies the given conditions.

Different types of conditions may be set with the parameters:
         
=============  =======================================================
Parameter      What gets tested
=============  =======================================================
*description*  Field properties and attributes
             
*items*        Field items
               
*rank*         The number of domain axes
               
*ndim*         The number of field data array axes
=============  =======================================================

By default, when multiple criteria are given the field matches if it
satisfies the conditions given by each one.

.. seealso:: `items`, `select`

**Quick start examples**

There is great flexibility in the types of test which can be
specified, and as a result the documentation is very detailed in
places. These preliminary, simple examples show that the usage need
not always be complicated and may help with understanding the keyword
descriptions.

1. Test if a field contains air temperature data, as given determined
   by its `identity` method:

   >>> f.match('air_temperature')

2. Test if a field contains air temperature data, as given determined
   by its `identity` method, or has a long name which contains the
   string "temp":

   >>> f.match(['air_temperature', {'long_name': cf.eq('.*temp.*', regex=true)}])

3. Test if a field has at least one longitude grid cell point on the
   Greenwich meridian:

   >>> f.match(items={'longitude': 0})

4. Test if a field has latitude grid cells which all have a resolution
   of less than 1 degree:

   >>> f.match(items={'latitude': cf.cellsize(cf.lt(1, 'degree'))})

5. Test if a field has exactly 4 domain axes:

   >>> f.match(rank=4)

6. Examples 1 to 4 may be combined to test if a field has exactly 4
   domain axes, contains air temperature data, has at least one
   longitude grid cell point on the Greenwich meridian and all
   latitude grid cells have a resolution of less than 1 degree:

   >>> f.match('air_temperature',
   ...         items={'longitude': 0,
   ...                'latitude': cf.cellsize(cf.lt(1, 'degree'))},
   ...         rank=4)

7. Test if a field contains Gregorian calendar monthly mean data array
   values:

   >>> f.match({'cell_methods': cf.CellMethods('time: mean')},
   ...         items={'time': cf.cellsize(cf.wi(28, 31, 'days'))})

Further examples are given within and after the description of the
arguments.


:Parameters:

    description: *optional*
        Set conditions on the field's CF property and attribute
        values. *description* may be one, or a sequence of:

          * `None` or an empty dictionary. Always matches the
            field. This is the default.

     ..

          * A string which identifies string-valued metadata of the
            field and a value to compare it against. The value may
            take one of the following forms:

              ==============  ======================================
              *description*   Interpretation
              ==============  ======================================
              Contains ``:``  Selects on the CF property specified
                              before the first ``:``
                                
              Contains ``%``  Selects on the attribute specified
                              before the first ``%``              
              
              Anything else   Selects on identity as returned by the
                              `identity` method
              ==============  ======================================

            By default the part of the string to be compared with the
            item is treated as a regular expression understood by the
            :py:obj:`re` module and the field matches if its
            appropriate value matches the regular expression using the
            :py:obj:`re.match` method (i.e. if zero or more characters
            at the beginning of field's value match the regular
            expression pattern). See the *exact* parameter for
            details.
            
              *Example:*
                To match a field with `identity` beginning with "lat":
                ``match='lat'``.

              *Example:*
                To match a field with long name beginning with "air":
                ``match='long_name:air'``.

              *Example:*
                To match a field with netCDF variable name of exactly
                "tas": ``match='ncvar%tas$'``.

              *Example:*
                To match a field with `identity` which ends with the
                letter "z": ``match='.*z$'``.

              *Example:*
                To match a field with long name which starts with the
                string ".*a": ``match='long_name%\.\*a'``. 

        ..

          * A `cf.Query` object to be compared with field's identity,
            as returned by its `identity` method.

              *Example:*
                To match a field with `identity` of exactly
                "air_temperature" you could set
                ``match=cf.eq('air_temperature')`` (see `cf.eq`).

              *Example:*
                To match a field with `identity` ending with
                "temperature" you could set
                ``match=cf.eq('.*temperature$', exact=False)`` (see
                `cf.eq`).

     ..

          * A dictionary which identifies properties of the field with
            corresponding tests on their values. The field matches if
            **all** of the tests in the dictionary are passed.

            In general, each dictionary key is a CF property name with
            a corresponding value to be compared against the field's
            CF property value. 

            If the dictionary value is a string then by default it is
            treated as a regular expression understood by the
            :py:obj:`re` module and the field matches if its
            appropriate value matches the regular expression using the
            :py:obj:`re.match` method (i.e. if zero or more characters
            at the beginning of field's value match the regular
            expression pattern). See the *exact* parameter for
            details.
            
              *Example:*
                To match a field with standard name of exactly
                "air_temperature" and long name beginning with the
                letter "a": ``match={'standard_name':
                cf.eq('air_temperature'), 'long_name': 'a'}`` (see
                `cf.eq`).

            Some key/value pairs have a special interpretation:

              ==================  ========================================
              Special key         Value
              ==================  ========================================
              ``'units'``         The value must be a string and by
                                  default is evaluated for
                                  equivalence, rather than equality,
                                  with the field's `units` property,
                                  for example a value of ``'Pa'``
                                  will match units of Pascals or
                                  hectopascals, etc. See the *exact*
                                  parameter.
                            
              ``'calendar'``      The value must be a string and by
                                  default is evaluated for
                                  equivalence, rather than equality,
                                  with the field's `calendar`
                                  property, for example a value of
                                  ``'noleap'`` will match a calendar
                                  of noleap or 365_day. See the
                                  *exact* parameter.
                              
              ``'cell_methods'``  The value must be a `cf.CellMethods`
                                  object containing *N* cell methods
                                  and by default is evaluated for
                                  equivalence with the last *N* cell
                                  methods contained within the field's
                                  `cell_methods` property. See the
                                  *exact* parameter.

              `None`              The value is interpreted as for a
                                  string value of the *description*
                                  parameter. For example,
                                  ``description={None: 'air'}`` is
                                  equivalent to ``match='air'`` and
                                  ``description={None: 'ncvar%pressure'}``
                                  is equivalent to
                                  ``description='ncvar%pressure'``.
              ==================  ========================================
            
              *Example:*
                To match a field with standard name starting with
                "air", units of temperature and a netCDF variable name
                beginning with "tas" you could set
                ``match={'standard_name': 'air', 'units': 'K', None:
                'ncvar%tas'}``.

              *Example:*
                To match a field whose last two cell methods are
                equivalent to "time: minimum area: mean":
                ``match={'cell_methods': cf.Cellmethods('time: minimum
                area: mean')``. This would match a field which has,
                for example, cell methods of "height: mean time:
                minimum area: mean".

        If *description* is a sequence of any combination of the above
        then the field matches if it matches **at least one** element
        of the sequence:

          *Example:* 

            >>> f.match('air_temperature')
            True
            >>> f.match('air_pressure')
            False
            >>> f.match({'units': 'hPa', 'long_name': 'foo'})
            False
            >>> f.match(['air_temperature',
            ...          'air_pressure',
            ...          {'units': 'hPa', 'long_name': 'foo'}])
            True
  
        If the sequence is empty then the field always matches.
 
    items: `dict`, optional
        A dictionary which identifies items of the field (dimension
        coordinate, auxiliary coordinate, cell measure or coordinate
        reference objects) with corresponding tests on their
        elements. The field matches if **all** of the specified items
        exist and their tests are passed.

        Each dictionary key specifies an item to test as the one that
        would be returned by this call of the field's `item` method:
        ``f.item(key, exact=exact)`` (see `cf.Field.item`).

        The corresponding value is, in general, any object for which
        the item may be compared with for equality (``==``). The test
        is passed if the result evaluates to True, or if the result is
        an array of values then the test is passed if at least one
        element evaluates to true.

        If the value is `None` then the test is always passed,
        i.e. this case tests for item existence.

          *Example:*
             To match a field which has a latitude coordinate value of
             exactly 30: ``items={'latitude': 30}``.

          *Example:*
             To match a field whose longitude axis spans the Greenwich
             meridien: ``items={'longitude': cf.contain(0)}`` (see
             `cf.contain`).

          *Example:*
             To match a field which has a time coordinate value of
             2004-06-01: ``items={'time': cf.dt('2004-06-01')}`` (see
             `cf.dt`).

          *Example:*
             To match a field which has a height axis: ``items={'Z':
             None}``.

          *Example:*
             To match a field which has a time axis and depth
             coordinates greater then 1000 metres: ``items={'T': None,
             'depth': cf.gt(1000, 'm')}`` (see `cf.gt`).

          *Example:*
            To match a field with time coordinates after than 1989 and
            cell sizes of between 28 and 31 days: ``items={'time':
            cf.dtge(1990) & cf.cellsize(cf.wi(28, 31, 'days'))}`` (see
            `cf.dtge`, `cf.cellsize` and `cf.wi`).

    rank: *optional*
        Specify a condition on the number of axes in the field.  The
        field matches if its number of domain axes equals *rank*. A
        range of values may be selected if *rank* is a `cf.Query`
        object. Not to be confused with the *ndim* parameter (the
        number of data array axes may be fewer than the number of
        domain axes).

          *Example:*
            ``rank=2`` matches a field with exactly two domain axes
            and ``rank=cf.wi(3, 4)`` matches a field with three or
            four domain axes (see `cf.wi`).

    ndim: *optional*
        Specify a condition on the number of axes in the field's data
        array. The field matches if its number of data array axes
        equals *ndim*. A range of values may be selected if *ndim* is
        a `cf.Query` object. Not to be confused with the *rank*
        parameter (the number of domain axes may be greater than the
        number of data array axes).

          *Example:*
            ``ndim=2`` matches a field with exactly two data array
            axes and ``ndim=cf.le(2)`` matches a field with fewer than
            three data array axes (see `cf.le`).

    exact: `bool`, optional
        The *exact* parameter applies to the interpretation of string
        values of the *description* parameter and of keys of the
        *items* parameter. By default *exact* is False, which means
        that:

          * A string value is treated as a regular expression
            understood by the :py:obj:`re` module. 

          * Units and calendar values in a *description* dictionary
            are evaluated for equivalence rather then equality
            (e.g. "metre" is equivalent to "m" and to "km").

          * A cell methods value containing *N* cell methods in a
            *description* dictionary is evaluated for equivalence with
            *the last *N* cell methods contained within the field's
            *`cell_methods` property.

        ..

          *Example:*
            To match a field with a standard name which begins with
            "air" and any units of pressure:
            ``f.match({'standard_name': 'air', 'units': 'hPa'})``.

          *Example:*          
            ``f.match({'cell_methods': cf.CellMethods('time: mean
            (interval 1 hour)')})`` would match a field with cell
            methods of "area: mean time: mean (interval 60 minutes)".

        If *exact* is True then:

          * A string value is not treated as a regular expression.

          * Units and calendar values in a *description* dictionary
            are evaluated for exact equality rather than equivalence
            (e.g. "metre" is equal to "m", but not to "km").

          * A cell methods value in a *description* dictionary is
            evaluated for exact equality to the field's cell methods.
          
        ..

          *Example:*          
            To match a field with a standard name of exactly
            "air_pressure" and units of exactly hectopascals:
            ``f.match({'standard_name': 'air_pressure', 'units':
            'hPa'}, exact=True)``.

          *Example:*          
            To match a field with a cell methods of exactly "time:
            mean (interval 1 hour)": ``f.match({'cell_methods':
            cf.CellMethods('time: mean (interval 1 hour)')``.

        Note that `cf.Query` objects provide a mechanism for
        overriding the *exact* parameter for individual values.

          *Example:*
            ``f.match({'standard_name': cf.eq('air', exact=False),
            'units': 'hPa'}, exact=True)`` will match a field with a
            standard name which begins "air" but has units of exactly
            hectopascals (see `cf.eq`).
    
          *Example:*
            ``f.match({'standard_name': cf.eq('air_pressure'),
            'units': 'hPa'})`` will match a field with a standard name
            of exactly "air_pressure" but with units which equivalent
            to hectopascals (see `cf.eq`).

    match_and: `bool`, optional
        By default *match_and* is True and the field matches if it
        satisfies the conditions specified by each test parameter
        (*description*, *items*, *rank* and *ndim*).

        If *match_and* is False then the field will match if it
        satisfies at least one test parameter's condition.

          *Example:*
            To match a field with a standard name of "air_temperature"
            **and** 3 data array axes: ``f.match('air_temperature',
            ndim=3)``. To match a field with a standard name of
            "air_temperature" **or** 3 data array axes:
            ``f.match('air_temperature", ndim=3, match_and=False)``.
    
    inverse: `bool`, optional
        If True then return the field matches if it does **not**
        satisfy the given conditions.

          *Example:*

            >>> f.match('air', ndim=4, inverse=True) == not f.match('air', ndim=4)
            True

:Returns:

    out: `bool`
        True if the field satisfies the given criteria, False
        otherwise.

:Examples:

Field identity starts with "air":

>>> f.match('air')

Field identity ends contains the string "temperature":

>>> f.match('.*temperature')

Field identity is exactly "air_temperature":

>>> f.match('^air_temperature$')
>>> f.match('air_temperature', exact=True)

Field has units of temperature:

>>> f.match({'units': 'K'}):

Field has units of exactly Kelvin:

>>> f.match({'units': 'K'}, exact=True)

Field identity which starts with "air" and has units of temperature:

>>> f.match({None: 'air', 'units': 'K'})

Field identity starts with "air" and/or has units of temperature:

>>> f.match(['air', {'units': 'K'}])

Field standard name starts with "air" and/or has units of exactly Kelvin:

>>> f.match([{'standard_name': cf.eq('air', exact=False), {'units': 'K'}],
...         exact=True)

Field has height coordinate values greater than 63km:

>>> f.match(items={'height': cf.gt(63, 'km')})

Field has a height coordinate object with some values greater than
63km and a north polar point on its horizontal grid:

>>> f.match(items={'height': cf.gt(63, 'km'),
...                'latitude': cf.eq(90, 'degrees')})

Field has some longitude cell sizes of 3.75:

>>> f.match(items={'longitude': cf.cellsize(3.75)})

Field latitude cell sizes within a tropical region are all no greater
than 1 degree:

>>> f.match(items={'latitude': (cf.wi(-30, 30, 'degrees') &
...                             cf.cellsize(cf.le(1, 'degrees')))})

Field contains monthly mean air pressure data and all vertical levels
within the bottom 100 metres of the atmosphere have a thickness of 20
metres or less:

>>> f.match({None: '^air_pressure$', 'cell_methods': cf.CellMethods('time: mean')},
...         items={'height': cf.le(100, 'm') & cf.cellsize(cf.le(20, 'm')),
...                'time': cf.cellsize(cf.wi(28, 31, 'days'))})

        '''
        conditions_have_been_set = False
        something_has_matched    = False

        if rank is not None:
            conditions_have_been_set = True
            found_match = len(self.axes()) == rank
            if match_and and not found_match:
                return bool(inverse)

            something_has_matched = True
        #--- End: if

        if description:
            conditions_have_been_set = True
             
        # --------------------------------------------------------
        # Try to match other properties and attributes
        # --------------------------------------------------------
        found_match = super(Field, self).match(
            description=description, ndim=ndim, exact=exact,
            match_and=match_and, inverse=False, _Flags=True,
            _CellMethods=True)

        if match_and and not found_match:
            return bool(inverse)

        something_has_matched = found_match
        #--- End: if

        # ------------------------------------------------------------
        # Try to match items
        # ------------------------------------------------------------
        if items:
            conditions_have_been_set = True

            found_match = False

            for identity, condition in items.iteritems():
                c = self.item(identity, exact=exact)

                if condition is None:
                    field_matches = c is not None
                else:
                    field_matches = condition == c
                    try:
                        field_matches = field_matches.any()
                    except AttributeError:
                        pass
                #--- End: if
                
                if match_and:                    
                    if field_matches:
                        found_match = True 
                    else:
                        found_match = False
                        break
                elif field_matches:
                    found_match = True
                    break
            #--- End: for 

            if match_and and not found_match:
                return bool(inverse)

            something_has_matched = found_match
        #--- End: if

        if conditions_have_been_set:
            if something_has_matched:            
                return not bool(inverse)
            else:
                return bool(inverse)
        else:
            return not bool(inverse)
    #--- End: def

#In [66]: w  
#Out[66]: array([ 0.125,  0.25 ,  0.375,  0.25 ])
#In [67]: convolve1d(a, w, mode='mirror')        
#Out[67]: array([ 1.75,  2.25,  3.25,  4.25,  5.25,  6.25,  7.  ,  7.25])
#
#In [68]: (w[::-1] * [5, 6, 7, 8]).sum()  
#Out[68]: 6.25
#
#In [69]: (w[::-1] * [6, 7, 8, 7]).sum() 
#Out[69]: 7.0
#
#In [70]: (w[::-1] * [7, 8, 7, 6]).sum()  
#Out[70]: 7.25





#In [60]: convolve1d(a, t, mode='mirror') 
#Out[60]: array([ 1.5,  2. ,  3. ,  4. ,  5. ,  6. ,  7. ,  7.5])
#
#In [61]: (t[::-1] * [5, 6, 7]).sum()   
#Out[61]: 6.0
#
#In [62]: (t[::-1] * [6, 7, 8]).sum()  
#Out[62]: 7.0
#
#In [63]: (t[::-1] * [7, 8, 7]).sum()  
#Out[63]: 7.5
#
#In [64]: t                           
#Out[64]: array([ 0.25,  0.5 ,  0.25])
#
#In [65]: a                            
#Out[65]: array([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.])


#In [75]: convolve1d(a, w, mode='reflect')   
#Out[75]: array([ 1.5  ,  2.25 ,  3.25 ,  4.25 ,  5.25 ,  6.25 ,  7.125,  7.625])
#
#In [76]: (w[::-1] * [5, 6, 7, 8]).sum()  
#Out[76]: 6.25
#
#In [77]: (w[::-1] * [6, 7, 8, 8]).sum()   
#Out[77]: 7.125
#
#In [78]: (w[::-1] * [7, 8, 8, 7]).sum()   
#Out[78]: 7.625
#In [81]: w     
#Out[81]: array([ 0.125,  0.25 ,  0.375,  0.25 ])
#
#In [82]: a     
#Out[82]: array([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.])

#In [94]: u                                                                                                        
#Out[94]: array([ 0.11111111,  0.22222222,  0.33333333,  0.22222222,  0.11111111])
#
#In [95]: convolve#convolve1d(a, w, mode='reflect')eflect')                                                        
#
#In [96]: convolve1d(a, u, mode='mirror')                                                                          
#Out[96]: 
#array([ 1.88888889,  2.22222222,  3.        ,  4.        ,  5.        ,
#        6.        ,  6.77777778,  7.11111111])
#
#In [97]: (u[::-1] * [4, 5, 6, 7, 8]).sum()                                                                        
#Out[97]: 6.0
#
#In [98]: (u[::-1] * [5, 6, 7, 8, 7]).sum()                                                                        
#Out[98]: 6.7777777777777768
#
#In [99]: (u[::-1] * [6, 7, 8, 7, 6]).sum()                                                                        
#Out[99]: 7.1111111111111107
#
#In [100]:                                        
#
#    def smooth(self, n, weights='boxcar', axis=None, mode='reflect', constant=0.0, mtol=0.0,
#               beta=None, std=None, power=None, width=None,
#               attenuation=None, return_weights=False):
## http://docs.scipy.org/doc/scipy-0.14.0/reference/signal.html      
##scipy.ndimage.filters.convolve1d
##ocs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve.html        
##http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve1d.html
#
#        '''Smooth the field along one of its axes.
#
# By default the field is smoothed with an unweighted moving average.
#
# The smoothing is the discrete convolution of values along the axis
# with a normalised weights function defined over an interval (window)
# of the axis.
#
#
#
#:Parameters:
#
#    window: `str`, optional
#
#          ====================  ==============================  ===============================
#          weights               Description                     Reference
#          ====================  ==============================  ===============================
#          ``barthann``          Modified Bartlett-Hann weights  `scipy.signal.barthann`        
#          ``bartlett``          Bartlett weights                `scipy.signal.bartlett`        
#          ``blackman``          Blackman weights                `scipy.signal.blackman`       
#          ``blackmanharris``    Minimum 4-term Blackman-Harris  `scipy.signal.blackmanharris`  
#                                weights                           
#          ``bohman``            Bohman weights                  `scipy.signal.bohman`          
#          ``boxcar``            Boxcar or rectangular weights   `scipy.signal.boxcar`
#          ``chebwin``           Dolph-Chebyshev weights         `scipy.signal.chebwin`         
#          ``cosine``            Weights with a simple cosine    `scipy.signal.cosine`          
#                                shape                                   
#          ``flattop``           Flat top weights                `scipy.signal.flattop`         
#          ``gaussian``          Gaussian weights                `scipy.signal.gaussian`        
#          ``general_gaussian``  Weights with a generalized      `scipy.signal.general_gaussian`
#                                Gaussian shape                   
#          ``hamming``           Hamming weights                 `scipy.signal.hamming`         
#          ``hann``              Hann weights                    `scipy.signal.hann`           
#          ``kaiser``            Kaiser weights                  `scipy.signal.kaiser`          
#          ``nuttall``           Minimum 4-term Blackman-Harris  `scipy.signal.nuttall`         
#                                weights according to Nuttall      
#          ``parzen``            Parzen weights                  `scipy.signal.parzen`         
#          ``slepian``           Digital Slepian (DPSS) weights  `scipy.signal.slepian`         
#          ``triang``            Triangular weights              `scipy.signal.triang`          
#          ???/                  User-defined weights
#          ====================  ==============================  ===============================
#
#        The default weights are ``'boxcar'``, which are create an
#        unweighted moving average

#        Some weights require extra parameters to be set for their calculation:
#        
#          ======================  ================  ===============================
#          *weights*               Extra parameters  Reference                      
#          ======================  ================  ===============================
#          ``'chebwin'``           *attenuation*     `scipy.signal.chebwin`
#          ``'gaussian'``          *std*             `scipy.signal.gaussian`    
#          ``'general_gaussian'``  *power*, *std*    `scipy.signal.general_gaussian`
#          ``'kaiser'``            *beta*            `scipy.signal.kaiser`   
#          ``'slepian'``           *width*           `scipy.signal.slepian`   
#          ======================  ================  ===============================
#
#    attenuation: number, optional
#        Required for a Dolph-Chebyshev weights, otherwise
#        ignored. *attenuation* is in decibels.
#    
#          Example: ``n=51, weights='chebwin', attenuation=100``
#
#    beta: number, optional
#        Required for Kaiser weights, otherwise ignored. *beta* is a
#        shape parameter which determines the trade-off between
#        main-lobe width and side lobe level.
#    
#          Example: ``n=51, weights='Kaiser', beta=14``
#
#    power: number, optional
#        Required for a generalized Gaussian weights, otherwise
#        ignored. *power* is a shape parameter: 1 is identical to
#        Gaussian weights, 0.5 is the same shape as the Laplace
#        distribution.
#
#          Example: ``n=52, weights='general_gaussian', power=1.5, std=7``
#
#    std: number, optional
#        Required for Gaussian and generalized Gaussian weights,
#        otherwise ignored. *std* is the standard deviation, sigma.
#
#          Example: ``n=52, weights='gaussian', std=7``
#
#    width: `float`, optional
#        Required for digital Slepian (DPSS) weights, otherwise
#        ignored. *wodth* is the bandwidth.
#
#          Example: ``n=51, weights='slepian', width=0.3``
#
#    rolling_window: *optional*
#        Group the axis elements for a "rolling window" collapse. The
#        axis is grouped into **consecutive** runs of **overlapping**
#        elements. The first group starts at the first element of the
#        axis and each following group is offset by one element from
#        the previous group, so that an element may appear in multiple
#        groups. The collapse operation is applied to each group
#        independently and the collapsed axis in the returned field
#        will have a size equal to the number of groups. If weights
#        have been given by the *weights* parameter then they are
#        applied to each group, unless alternative weights have been
#        provided with the *window_weights* parameter. The
#        *rolling_window* parameter may be one of:
#
#          * An `int` defining the number of elements in each
#            group. Each group will have exactly this number of
#            elements. Note that if the group size does does not divide
#            exactly into the axis size then some elements at the end
#            of the axis will not be included in any group.
#            
#              Example: To define groups of 5 elements:
#              ``rolling_window=5``.
#
#        .. 
#
#          * A `cf.Data` defining the group size. Each group contains a
#            consecutive run of elements whose range of coordinate
#            bounds does not exceed the group size. Note that 1) if the
#            group size is sufficiently small then some groups may be
#            empty and some elements may not be inside any group may
#            not be inside any group; 2) different groups may contain
#            different numbers of elements.
#
#              Example: To create 10 kilometre windows:
#              ``rolling_window=cf.Data(10, 'km')``.
#
#    window_weights: ordered sequence of numbers, optional
#        Specify the weights for a rolling window collapse. Each
#        non-empty group uses these weights in its collapse, and all
#        non-empty groups must have the same number elements as the
#        window weights. If *window_weights* is not set then the groups
#        take their weights from the *weights* parameter, and in this
#        case the groups may have different sizes.
#
#          Example: To define a 1-2-1 filter: ``rolling_window=3,
#          window_weights=[1, 2, 1]``.
#
#'''
#        if weights == 'user':
#            weights = numpy_array(weights, float)
#            if weights.size != n:
#                raise ValueError("jb ")
#            if weights.ndim > 1:
#                raise ValueError("bad shape")
#        else:
#            weights = getattr(signal, window)(n, **window_args)

#        if return_weights:
#            return weights

#        http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve1d.html

#        http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve.html

#        smoothed_array = convolve1d(array, weights/weights.sum(), axis=iaxis,
        #                            mode=mode, cval=constant)
#        
#        f.Data = Data(smoothed_array, f.Units)
#http://mail.scipy.org/pipermail/scipy-user/2008-November/018601.html
#Sorry for the long overdue reply.
#
#Reflect means:
#
#1 | 2 | 3 | 2 | 1
#
#While mirror means:
#
#1 | 2 | 3 | 3| 2 | 1
#
#(or the other way around, can't remember). IT IS THE OTHER WAY ROUND!!!!
#
#http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter

#The problem with the last approach is the interpolation between 3 and
#3, which is currently broken, so I'd advise against using it.
#
#
#        # Coordinate bounds
#        dim = f.dim(axis)
#
#
#        n_by_2 = 0.5 * n
#        i = int(n_by_2)
#        j = axis_size - i
#        d1 = i
#        if not i < n_by_2:
#            # Window has even number of points
#            i -= 1
#
#        d0 = i
# 
#        new_bounds[:i, 0] = bounds[0, 0]
#
#        new_bounds[i:j, 0] = bounds[i-d0:j-d0, 0]
#        new_bounds[i:j, 1] = bounds[i+d1:j+d1, 1]
#
#        new_bounds[j:, 1] = bounds[-1, 1]
#
#        if mode == 'mirror':
#            new_bounds[:i, 1] = bounds[i+d1, 1]
#            new_bounds[j:, 0] = bounds[j-d0, 0]
#        elif mode in ('nearest', 'reflect', 'constant'):
#            new_bounds[:i, 1] = bounds[d1:i+d1, 1]
#            new_bounds[j:, 0] = bounds[j-d0:axis_size-d0, 0]
#                
#            wrap?
##        if dim:
#            if dim.hasbounds:            
#                data       = dim.array
#                bounds     = dim.bounds.array
#                new_bounds = numpy_empty(bounds.shape, dtype=float)
#                
#                half_window = 0.5 * n * float(cell_sizes[0])
#                
#                if dim.increasing:
#                    a_min, a_max = bounds[[0, -1], [0, 1]]
#                else:
#                    half_window = -half_window 
#                    a_min, a_max = bounds[[-1, 0], [0, 1]]
#                    
#                new_bounds[0] = data - half_window
#                new_bounds[1] = data + half_window
#                numpy_clip(new_bounds, a_min, a_max, new_bounds)
#                
#                dim.insert_bounds(Data(new_bounds, dim.Units), copy=False)
#            #--- End: if   
#
#            f.remove_items(role='c', axes=axis)
#            
#            for b in f.auxs(axes=axis):
#                if b.hasbounds:
#                    del b.bounds
#       #--- End: if   

#        cell_methods = getattr(f, 'cell_methods', None)
#        if cell_methods is None:
#            cell_methods = CellMethods()
#
#        f.cell_methods += CellMethods(
#            'name: mean (+'+weights+' weights '+', '.join([str(x) for x in weights])+')')
#
##    #--- End: def

    def convolution_filter(self, weights, width=None, axis=-1,
                           mode='constant', cval=None, origin=0,
                           update_bounds=True, i=False):
        '''Return the field convolved along the given axis with the specified
filter.

:Parameters:

    weights: `str` or `tuple`, optional
        A string specifying the type of weights to use for the filter:

        ====================  ==============================  ===============================
        weights               Description                     Reference
        ====================  ==============================  ===============================
        ``barthann``          Modified Bartlett-Hann weights  `scipy.signal.barthann`
        ``bartlett``          Bartlett weights                `scipy.signal.bartlett`
        ``blackman``          Blackman weights                `scipy.signal.blackman`
        ``blackmanharris``    Minimum 4-term Blackman-Harris  `scipy.signal.blackmanharris`
                              weights
        ``bohman``            Bohman weights                  `scipy.signal.bohman`
        ``boxcar``            Boxcar or rectangular weights   `scipy.signal.boxcar`
        ``chebwin``           Dolph-Chebyshev weights         `scipy.signal.chebwin`
        ``cosine``            Weights with a simple cosine    `scipy.signal.cosine`
                              shape                                   
        ``exponential``       Exponential (or Poison) weights `scipy.signal.exponential`
        ``flattop``           Flat top weights                `scipy.signal.flattop`
        ``gaussian``          Gaussian weights                `scipy.signal.gaussian`
        ``general_gaussian``  Weights with a generalized      `scipy.signal.general_gaussian`
                              Gaussian shape
        ``hamming``           Hamming weights                 `scipy.signal.hamming`
        ``hann``              Hann weights                    `scipy.signal.hann`
        ``kaiser``            Kaiser weights                  `scipy.signal.kaiser`
        ``nuttall``           Minimum 4-term Blackman-Harris  `scipy.signal.nuttall`
                              weights according to Nuttall
        ``parzen``            Parzen weights                  `scipy.signal.parzen`
        ``slepian``           Digital Slepian (DPSS) weights  `scipy.signal.slepian`
        ``triang``            Triangular weights              `scipy.signal.triang`
        ``tukey``             Tukey or tapered cosine weights `scipy.signal.tukey`
        ``user``              User-defined weights
        ====================  ==============================  ===============================

       Some weights require extra parameters to be set for their
       calculation, in which case a tuple must be passed in with the
       type of weights specified by the first argument and the
       necessary parameters in order as the next arguments:
       
        ======================  ================  ===============================
        *weights*               Extra parameters  Reference                      
        ======================  ================  ===============================
        ``'chebwin'``           *attenuation*     `scipy.signal.chebwin`
        ``'exponential'``       *tau*             `scipy.signal.exponential`
        ``'gaussian'``          *std*             `scipy.signal.gaussian`
        ``'general_gaussian'``  *power*, *std*    `scipy.signal.general_gaussian`
        ``'kaiser'``            *beta*            `scipy.signal.kaiser`
        ``'slepian'``           *width*           `scipy.signal.slepian`
        ``'tukey'``             *alpha*           `scipy.signal.tukey`
        ``'user'``              *weights*
        ======================  ================  ===============================

        If ``'user'`` is specified then the second argument in the
        tuple must be a sequence of numbers specifying the weights.
        Note that for the ``'exponential'`` filter it is not necessary
        to specify the center as the weights must be symmetric when
        used in filter design.

    width: `int`, optional
        The width of the filter. Not necessary for user defined
        weights.

    {+axes}

    mode: {'reflect', 'constant', 'nearest', 'mirror', 'wrap'}, optional
        Determines how the edges of the array are handled.

        A table of the different behaviours is given here:
        https://stackoverflow.com/questions/22669252/how-exactly-does-the-reflect-mode-for-scipys-ndimage-filters-work

        "Suppose the data in one axis is 1 2 3 4 5 6 7 8. The
        following table shows how the data is extended for each mode
        (assuming cval=0):

        mode       |   Ext   |         Input          |   Ext
        -----------+---------+------------------------+---------
        'mirror'   | 4  3  2 | 1  2  3  4  5  6  7  8 | 7  6  5
        'reflect'  | 3  2  1 | 1  2  3  4  5  6  7  8 | 8  7  6
        'nearest'  | 1  1  1 | 1  2  3  4  5  6  7  8 | 8  8  8
        'constant' | 0  0  0 | 1  2  3  4  5  6  7  8 | 0  0  0
        'wrap'     | 6  7  8 | 1  2  3  4  5  6  7  8 | 1  2  3

        For an even window size n, consider the window of size n+1,
        and then don't include the lower and right edges. (The
        position of the window can be changed by using the origin
        argument.)"

        Defaults to constant.

    cval: scalar, optional
        Value to fill past the edges of the array if *mode* is
        constant. Defaults to None, in which case the edges of the
        array will be filled with missing data.

    origin: `int`, optional
        Controls the placement of the filter. Defaults to 0, which is
        the centre of the array.

    update_bounds: `bool`, optional
        Update the bounds of the axis to reflect the size of the
        filter.

    {+i}

        '''

        # Retrieve the axis
        axis_key = self.axis(axis, key=True)
        if axis_key is None:
            raise ValueError('Invalid axis specifier')

        # If the mode is to wrap at the edges then check that the axis is
        # cyclic
        if mode=='wrap' and not self.iscyclic(axis_key):
            raise ValueError('Cannot wrap a noncyclic axis.')
        #--- End: if

        # Get the axis index
        axis_index = self.data_axes().index(axis_key)

        # Section the data into sections up to a chunk in size
        sections = self.Data.section([axis_index], chunks=True)

        # Set cval to NaN if it is currently None, so that the edges
        # will be filled with missing data if the mode is 'constant'
        if cval is None:
            cval = numpy_nan
        #--- End: if

        # Calculate the weights
        if type(weights) is str:
            if weights == 'user':
                raise ValueError("The 'user' window needs one or more " +
                                 'parameters -- pass a tuple.')
            else:
                weights = get_window(weights, width, False)
            #--- End: if
        elif type(weights) is tuple:
            if not weights:
                raise ValueError("'weights' cannot be an empty tuple.")
            elif len(weights) == 1:
                if weights[0] == 'user':
                    raise ValueError("The 'user' window needs one or more " +
                                     'parameters -- pass a tuple.')
                else:
                    if weights[0] == 'exponential':
                        weights = (weights[0], None)
                    #--- End: if
                    weights = get_window(weights, width, False)
                #--- End: if
            elif weights[0] == 'user':
                if len(weights) > 2:
                    raise ValueError("The 'user' window needs at most one " +
                                     'parameter.')
                else:
                    weights = weights[1]
                #--- End: if
            else:
                if weights[0] == 'exponential':
                    if len(weights) != 2:
                        raise ValueError('Only the decay scale need be ' +
                                         "specified for the 'exponential' " +
                                         'window.')
                    else:
                        weights = (weights[0], None, weights[1])
                    #--- End: if
                weights = get_window(weights, width, False)
            #--- End: if
        else:
            raise ValueError("'weights' must be either a string or a tuple.")
        #--- End: if

        # Filter each section replacing masked points with numpy
        # NaNs and then remasking after filtering.
        for k in sections:
            input_array = sections[k].array
            masked = numpy_ma_is_masked(input_array)
            if masked:
                input_array = input_array.filled(numpy_nan)
            #--- End: if
            output_array = convolve1d(input_array, weights, axis=axis_index,
                                      mode=mode, cval=cval, origin=origin)
            if masked or (mode == 'constant' and numpy_isnan(cval)):
                with numpy_errstate(invalid='ignore'):
                    output_array = numpy_ma_masked_invalid(output_array)
                #--- End: with
            #--- End: if
            sections[k] = Data(output_array, units=self.Units)
        #--- End: for

        # Glue the sections back together again
        new_data = Regrid.reconstruct_sectioned_data(sections)

        # Construct new field
        if i:
            f = self
        else:
            f = self.copy(_omit_Data=True)
        #--- End: if

        # Insert filtered data into new field
        f.insert_data(new_data, axes=self.data_axes())

        # Update the bounds of the convolution axis if necessary
        if update_bounds:
            coord = f.dim(axis_key)
            if coord.hasbounds:
                old_bounds = coord.bounds.array
                length = old_bounds.shape[0]
                new_bounds = numpy_empty((length, 2))
                len_weights = len(weights)
                lower_offset = len_weights//2 + origin
                upper_offset = len_weights - 1 - lower_offset
                if mode == 'wrap':
                    new_bounds[:, 0] = \
                                coord.roll(0, upper_offset).bounds.array[:, 0]
                    new_bounds[:, 1] = \
                        coord.roll(0, -lower_offset).bounds.array[:, 1] - \
                        coord.period()
                else:
                    new_bounds[upper_offset:length, 0] = \
                                        old_bounds[0:length - upper_offset, 0]
                    new_bounds[0:upper_offset, 0] = old_bounds[0, 0]
                    new_bounds[0:length - lower_offset, 1] = \
                                        old_bounds[lower_offset:length, 1]
                    new_bounds[length - lower_offset:length, 1] = \
                                        old_bounds[length - 1, 1]
                    #--- End: for
                #--- End: if
                coord.insert_bounds(Data(new_bounds, units=coord.units))
            #--- End: if
        #--- End: if

        # Return the new field
        return f
    #--- End: def

    def HDF_chunks(self, *chunksizes):
        '''{+HDF_chunks}

**Chunking the metadata**

The coordinate, cell measure, and ancillary contructs are not
automatically chunked, but they may be chunked manually. For example,
a two dimensional latitude coordinate could chunked as follows (see
`cf.AuxiliaryCoordinate.HDF_chunks` for details):

>>> f.coord('latitude').HDF_chunks({0: 10, 1: 15})

In version 2.0, the metadata will be automatically chunked.

**Chunking via cf.write**

Chunking may also be defined via a parameter to the `cf.write`
function, in which case any axis chunk sizes set on the field take
precedence.

.. versionadded:: 1.1.13

.. seealso:: `cf.write`

:Examples 1:
        
To define chunks which are the full size for each axis except for the
time axis which is to have a chunk size of 12:

>>> old_chunks = f.{+name}({'T': 12})

:Parameters:


    chunksizes: `dict` or None, optional
        Specify the chunk sizes for axes of the field. Axes are given
        by dictionary keys, with a chunk size for those axes as the
        dictionary values. A dictionary key of ``axes`` defines the
        axes that would be returned by the field's `~cf.Field.axes`
        method, i.e. by ``f.axes(axes)``. See `cf.Field.axes` for
        details. In the special case of *chunksizes* being `None`,
        then chunking is set to the netCDF default.

          *Example:*
            To set the chunk size for time axes to 365: ``{'T':
            365}``.

          *Example:*
            To set the chunk size for the first and third data array
            axes to 100: ``{0: 100, 2: 100}``, or equivalently ``{(0,
            2): 100}``.

          *Example:*
            To set the chunk size for the longitude axis to 100 and
            for the air temperature axis to 5: ``{'X': 100,
            'air_temperature': 5}``.

          *Example:*
            To set the chunk size for all axes to 10: ``{None:
            10}``. This works because ``f.axes(None)`` returns all
            field axes.

          *Example:*
            To set the chunking to the netCDF default: ``None``.

:Returns:

    out: `dict`
        The chunk sizes prior to the new setting, or the current
        current sizes if no new values are specified.

:Examples 2:

>>> f
<CF Field: air_temperature(time(3650), latitude(64), longitude(128)) K>
>>> f.HDF_chunks()
{0: None, 1: None, 2: None}
>>> f.HDF_chunks({'T': 365, 2: 1000})
{0: None, 1: None, 2: None}
>>> f.HDF_chunks({'X': None})
{0: 365, 1: None, 2: 1000}
>>> f.HDF_chunks(None)
{0: 365, 1: None, 2: None}
>>> f.HDF_chunks()
{0: None, 1: None, 2: None}

        '''
        if not chunksizes:
            return super(Field, self).HDF_chunks()

        if len(chunksizes) > 1:
            raise ValueError("asfdds ")
            
        chunks = chunksizes[0]

        if chunks is None:
            return super(Field, self).HDF_chunks(None)

        _HDF_chunks = {}
#        seen_axes = []
        data_axes = self.data_axes()
        for axes, size in chunks.iteritems():
            for axis in self.axes(axes):
#                if axis in seen_axes:
#                    raise ValueError(
#"Can't set multiple chunk sizes for axis {0}".format(data_axes.index(axis)))
                try:
                    _HDF_chunks[data_axes.index(axis)] = size
                except ValueError:
                    pass                
#                seen_axes.append(axis)
        #--- End: for

        return super(Field, self).HDF_chunks(_HDF_chunks)
    #--- End: def

    def field(self, description=None, role=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, exact=False,
              inverse=False, match_and=True, ndim=None, bounds=False):
        '''Create an independent field from a domain item.

An item is either a dimension coordinate, an auxiliary coordinate or a
cell measure object of the domain.

{+item_selection}

If a unique item can not be found then no field is created and `None`
is returned.

A field may also be created from coordinate bounds (see the *bounds*
parameter).

.. versionadded:: 1.1

.. seealso:: `cf.read`, `item`

:Examples 1:

Create a field whose data are the latitude coordinates

>>> y = f.field('latitude')

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    bounds: `bool`, optional
        If true then create a field from a coordinate object's bounds.

:Returns:

    out: `cf.{+Variable}`
        The field based on the selected domain item.
        
:Examples 2:

::

   >>> print f 
   eastward_wind field summary
   ---------------------------
   Data           : eastward_wind(time(3), grid_latitude(110), grid_longitude(106)) m s-1
   Cell methods   : time: mean
   Axes           : time(3) = [1979-05-01 12:00:00, ..., 1979-05-03 12:00:00] gregorian
                  : grid_longitude(106) = [-20.54, ..., 25.66] degrees
                  : grid_latitude(110) = [23.32, ..., -24.64] degrees
   Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_north
                  : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_east
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
   
   >>> print f.field('X')
   grid_longitude field summary
   ----------------------------
   Data           : grid_longitude(grid_longitude(106)) degrees
   Axes           : grid_longitude(106) = [-20.54, ..., 25.66] degrees
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
   
   >>> print f.field('X', bounds=True)
   grid_longitude field summary
   ----------------------------
   Data           : grid_longitude(grid_longitude(106), domain%dim1(2)) degrees
   Axes           : domain%dim1(2)
                  : grid_longitude(106) = [-20.54, ..., 25.66] degrees
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
   
   >>> print f.field('lat')
   latitude field summary
   ----------------------
   Data           : latitude(grid_latitude(110), grid_longitude(106)) degrees_north
   Axes           : grid_longitude(106) = [-20.54, ..., 25.66] degrees
                  : grid_latitude(110) = [23.32, ..., -24.64] degrees
   Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_north
                  : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_east
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>

To multiply the field by the cosine of its latitudes:

>>> latitude = f.field({'units': 'radian', None: 'Y'})
>>> latitude
<CF Field: grid_latitude(grid_latitude(110)) degrees>
>>> g = f * latitude.cos()

        '''
        kwargs2 = self._parameters(locals())
        del kwargs2['bounds']
 
        (key, item) = self.Items.key_item(**kwargs2)
        if key is None:
            raise ValueError("No unique item could be found from {}".format(
                self._no_None_dict(kwargs2)))

        item_axes = self.item_axes(key)
        data_axes = item_axes
        
        f = type(self)(properties=item.properties())
        
        if bounds and item.hasbounds:
            if not item.bounds.hasdata:
                raise ValueError("No bounds data")

            data_axes.append(self.new_identifier('axis'))
            data = item.bounds.data
        else:
            data = item.data
        
        f.insert_data(data, axes=data_axes)
        
        for key, item in self.items(axes_superset=item_axes).iteritems():
            role = self.Items.role(key)
            if role in ('d', 'a', 'm'):
                f.insert_item(role, item, key=key, axes=self.item_axes(key))

        # Add coordinate references which span a subset of the item's
        # axes
        for rkey, ref in self.items(role='r').iteritems():
            if not set(f.axes(ref.coordinates)).issuperset(item_axes):
                continue

            ref = ref.copy()

            coordinates = []
            new_field_coordinates = f.items(role='da')
            for x in ref.coordinates:
                if x in new_field_coordinates:
                    coordinates.append(x)
            ref._coordinates = set(coordinates)

            ancillaries = []
            for term in ref.ancillaries:
                key = ref[term]
                domain_anc = f.item(key, role='c', axes_superset=item_axes)
                if domain_anc is not None:
                    ancillaries.append(term)
                    f.insert_item('c', domain_anc, key=key, axes=self.item_axes(key))
                else:
                    ref[term] = None
                    
                ref._ancillaries = set(ancillaries)
            #--- End: for
                
            f.insert_ref(ref, key=rkey, copy=False)
        #--- End: for

        return f
    #--- End: def

#
#
#
#
#
#
#
#
#
#
#        kwargs2 = self._parameters(locals())
#        del kwargs2['bounds']
# 
#        (key, item) = self.key_item(**kwargs2)
#        if key is None:
#            raise ValueError("No unique item could be found from {}".format(self._no_None_dict(kwargs2)))
#
#        f = type(self)(properties=item.properties(), data=item.data)
#
#        role = self.Items.role(key)
#        if role in ('d', 'a', 'm'):
#            f.insert_item(role, item, axes=f.data_axes())
#
#
#        print f
##        f = self.copy()
#
##        f.properties(clear=True, copy=False)
##        f.properties(item.properties(), copy=True)
#
#        axes = f.item_axes(key)
#
#        # Remove items which span any axis not spanned by the item
#        unused_axes = set(f.axes()).difference(axes)
#        for key in self.items(axes=unused_axes):
#            f.remove_item(key)
#
#        # Remove coordinate references which do not span any of the
#        # item's axes
#        for key, ref in self.refs().iteritems():
#            if not set(f.axes(ref.coordinates)).intersection(axes):
#                f.remove_item(key)
#
#        # Remove the unused axes
#        print f #dch
#        f.remove_axes(unused_axes)
#
#        if bounds and item.hasbounds:
#            item = item.bounds
#            axes.append(f.insert_axis(DomainAxis(item.shape[-1])))
#
#        f.attributes(clear=True, copy=False)
#        ncvar = getattr(item, 'ncvar', None)
#        if ncvar is not None:
#            f.ncvar = ncvar
#
#        f.remove_data()
#        data = getattr(item, 'Data', None)
#        if data is not None:
#            f.insert_data(data, axes=axes, copy=True)
#
#        return f
#    #--- End: def

    def flip(self, axes=None, i=False, **kwargs):
        '''Flip (reverse the direction of) axes of the field.

.. seealso:: `axes`, `expand_dims`, `squeeze`, `transpose`,
             `unsqueeze`
        
:Examples:

>>> f.flip()
>>> f.flip('time')
>>> f.flip(1)
>>> f.flip('dim2')
>>> f.flip(['time', 1, 'dim2'])

:Parameters:

    {+axes, kwargs}

    {+i}
 
:Returns:

    out: `cf.{+Variable}`
        The flipped field.

        '''
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('flip', kwargs2)

        if axes is None and not kwargs:
            # Flip all the axes
            axes = set(self.axes())
            iaxes = range(self.ndim)
        else:
            axes = set(self.axes(axes, **kwargs))

            data_axes = self.data_axes()
            iaxes = [data_axes.index(axis) for axis in
                     axes.intersection(data_axes)]
        #--- End: if

        # Flip the requested axes in the field's data array
        f = super(Field, self).flip(iaxes, i=i)

        # Flip any items which span the flipped axes
        for key, item in f.items(role=('d', 'a', 'm', 'f', 'c')).iteritems():
            item_axes = f.item_axes(key)
            item_flip_axes = axes.intersection(item_axes)
            if item_flip_axes:
                iaxes = [item_axes.index(axis) for axis in item_flip_axes]
                item.flip(iaxes, i=True)
        #--- End: for

        return f
    #--- End: def

    def remove_data(self):
        '''

Remove and return the data array.

:Returns: 

    out: `cf.Data` or `None`
        The removed data array, or `None` if there isn't one.

:Examples:

>>> f._hasData
True
>>> f.data
<CF Data: [0, ..., 9] m>
>>> f.remove_data()
<CF Data: [0, ..., 9] m>
>>> f._hasData
False
>>> print f.remove_data()
None

'''        
        self._data_axes = None
        return super(Field, self).remove_data()
    #--- End: def

    def anchor(self, axes, value, i=False, dry_run=False, **kwargs):
        '''Roll a cyclic axis so that the given value lies in the first
coordinate cell.

A unique axis is selected with the *axes* and *kwargs* parameters.

.. versionadded:: 1.0

.. seealso:: `axis`, `cyclic`, `iscyclic`, `period`, `roll`

:Examples 1:

Anchor the cyclic X axis to a value of 180:

>>> g = f.{+name}('X', 180)

:Parameters:

    {+axes, kwargs}

    value: data-like object
        Anchor the dimension coordinate values for the selected cyclic
        axis to the *value*. If *value* has units then they must be
        compatible with those of the dimension coordinates, otherwise
        it is assumed to have the same units as the dimension
        coordinates. The coordinate values are transformed so that
        *value* is "equal to or just before" the new first coordinate
        value. More specifically:
        
          * Increasing dimension coordinates with positive period, P,
            are transformed so that *value* lies in the half-open
            range (L-P, F], where F and L are the transformed first
            and last coordinate values, respectively.

          * Decreasing dimension coordinates with positive period, P,
            are transformed so that *value* lies in the half-open
            range (L+P, F], where F and L are the transformed first
            AND last coordinate values, respectively.

        ..

            *Example:*
              If the original dimension coordinates are ``0, 5, ...,
              355`` (evenly spaced) and the period is ``360`` then
              ``value=0`` implies transformed coordinates of ``0, 5,
              ..., 355``; ``value=-12`` implies transformed coordinates
              of ``-10, -5, ..., 345``; ``value=380`` implies
              transformed coordinates of ``380, 385, ..., 715``.

            *Example:*
              If the original dimension coordinates are ``355, 350,
              ..., 0`` (evenly spaced) and the period is ``360`` then
              ``value=355`` implies transformed coordinates of ``355,
              350, ..., 0``; ``value=0`` implies transformed
              coordinates of ``0, -5, ..., -355``; ``value=392``
              implies transformed coordinates of ``390, 385, ...,
              30``.

        {+data-like}

    {+i}

    dry_run: `bool`, optional
        Return a dictionary of parameters which describe the anchoring
        process. The field is not changed, even if *i* is True.

:Returns:

[+1]    out: `cf.{+Variable}` or `dict`
[+N]    out: `cf.{+Variable}`

:Examples 2:

>>> f[+0].iscyclic('X')
True
>>> f[+0].dim('X').data
<CF Data: [0, ..., 315] degrees_east>
>>> print f[+0].dim('X').array
[  0  45  90 135 180 225 270 315]
>>> g = f.anchor('X', 230)
>>> print g[+0].dim('X').array
[270 315   0  45  90 135 180 225]
>>> g = f.anchor('X', cf.Data(590, 'degreesE'))
>>> print g[+0].dim('X').array
[630 675 360 405 450 495 540 585]
>>> g = f.anchor('X', cf.Data(-490, 'degreesE'))
>>> print g[+0].dim('X').array
[-450 -405 -720 -675 -630 -585 -540 -495]

>>> f[+0].iscyclic('X')
True
>>> f[+0].dim('X').data
<CF Data: [0.0, ..., 357.1875] degrees_east>
>>> f.anchor('X', 10000)[+0].dim('X').data
<CF Data: [10001.25, ..., 10358.4375] degrees_east>
>>> d = f[+0].anchor('X', 10000, dry_run=True)
>>> d
{'axis': 'dim2',
 'nperiod': <CF Data: [10080.0] 0.0174532925199433 rad>,
 'roll': 28}
>>> (f.roll(d['axis'], d['roll'])[+0].dim(d['axis']) + d['nperiod']).data
<CF Data: [10001.25, ..., 10358.4375] degrees_east>

        '''
#        # List functionality
#        if self._list:
#            kwarsg2 = self._parameters(locals())
#            if kwargs2['dry_run']:
#                raise ValueError(
#"Can't do a dry run on a {0}".format(self.__class__.__name__))
#            return self._list_method('anchor', kwargs2)

        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:  
            raise ValueError(
"Can't anchor: Bad axis specification")

        if i or dry_run:
            f = self
        else:
            f = self.copy()
        
        dim = f.item(axis)
        if dim is None:
          raise ValueError(
"Can't shift non-cyclic {!r} axis".format(f.axis_name(axis)))
        
        period = dim.period()
        if period is None:
            raise ValueError("Cyclic %r axis has no period" % dim.name())

        value = Data.asdata(value)
        if not value.Units:
            value = value.override_units(dim.Units)
        elif not value.Units.equivalent(dim.Units):
            raise ValueError(
"Anchor value has incompatible units: {0!r}".format(value.Units))

        axis_size = f.axis_size(axis)
        if axis_size <= 1:
            # Don't need to roll a size one axis
            if dry_run:
                return {'axis': axis, 'roll': 0, 'nperiod': 0}
            else:
                return f
        
        c = dim.data

        if dim.increasing:
            # Adjust value so it's in the range [c[0], c[0]+period) 
            n = ((c[0] - value) / period).ceil(i=True)
            value1 = value + n * period

            shift = axis_size - numpy_argmax(c - value1 >= 0)
            if not dry_run:
                f.roll(axis, shift, i=True)     

            dim = f.item(axis)
            n = ((value - dim.data[0]) / period).ceil(i=True)
        else:
            # Adjust value so it's in the range (c[0]-period, c[0]]
            n = ((c[0] - value) / period).floor(i=True)
            value1 = value + n * period

            shift = axis_size - numpy_argmax(value1 - c >= 0)
            if not dry_run:
                f.roll(axis, shift, i=True)     

            dim = f.item(axis)
            n = ((value - dim.data[0]) / period).floor(i=True)
        #--- End: if

        if dry_run:
            return  {'axis': axis, 'roll': shift, 'nperiod': n*period}

        if n:
            np = n * period
            dim += np
            if dim.hasbounds:
                bounds = dim.bounds
                bounds += np
        #--- End: if
                
        return f
    #--- End: def

    def field_anc(self, description=None, axes=None, axes_all=None,
                  axes_subset=None, axes_superset=None, ndim=None,
                  match_and=True, exact=False, inverse=False, copy=False):
        '''Return a field ancillary object.

In this documentation, an ancillary variable object is referred to as
an item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.item(role='f', inverse=False, **kwargs)``.
 
.. seealso:: `aux`, `coord`, `dim`, `domain_anc`, `field_ancs`,
             `item`, `measure`, `ref`, `remove_item`

:Examples 1:

>>> v = f.{+name}()

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the domain. The dictionary
        may be empty.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        role = ('f',)
        kwargs2['role'] = role
#        kwargs2['_restrict_inverse'] = role
        return self.item(**kwargs2)
    #--- End: def

    def field_ancs(self, description=None, axes=None, axes_all=None,
                   axes_subset=None, axes_superset=None, ndim=None,
                   match_and=True, exact=False, inverse=False, copy=False):
        '''Return ancillary variable objects.

In this documentation, an ancillary variable object is referred to as
an item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='f', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `coords`, `dims`, `domain_ancs`, `field_anc`,
             `items`, `measures`, `refs`, `remove_items`

:Examples 1:

To select all ancillary variable objects:

>>> v = f.{+name}()

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the domain. The dictionary
        may be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        role = ('f',)
        kwargs2['role'] = role
#        kwargs2['_restrict_inverse'] = role
        return self.items(**kwargs2)
    #--- End: def

    def autocyclic(self):
        '''

Set axes to be cyclic if they meet conditions.

An axis is set to be cyclic if and only if the following is true:

* It has a unique, 1-d, longitude dimension coordinate object with
  bounds and the first and last bounds values differ by 360 degrees
  (or an equivalent amount in other units).
   
.. versionadded:: 1.0

.. seealso:: `cyclic`, `iscyclic`, `period`

:Examples 1:

>>> f.{+name}()

:Returns:

   `None`

'''
#        # List functionality
#        if self._list:
#            for f in self:
#                f.autocyclic()
#            return

        dims = self.dims('X')

        if len(dims) != 1:
            return

        key, dim = dims.popitem()

        if not dim.Units.islongitude:
            if dim.getprop('standard_name', None) not in ('longitude', 'grid_longitude'):
                self.cyclic(key, iscyclic=False)
                return

        if not dim.hasbounds:
            self.cyclic(key, iscyclic=False)
            return
        
        bounds = dim.bounds
        if not bounds._hasData:
            self.cyclic(key, iscyclic=False)
            return 
        
        period = Data(360, 'degrees')
        if abs(bounds.datum(-1) - bounds.datum(0)) != period:
            self.cyclic(key, iscyclic=False)
            return

        self.cyclic(key, iscyclic=True, period=period)
    #--- End: def

    def squeeze(self, axes=None, i=False, **kwargs):
        '''Remove size-1 axes from the data array.

By default all size 1 axes are removed, but particular size 1 axes may
be selected for removal.

The axes are selected with the *axes* parameter.

Squeezed axes are not removed from the coordinate and cell measure
objects, nor are they removed from the domain. To completely remove
axes, use the `remove_axes` method.

.. seealso:: `expand_dims`, `flip`, `remove_axes`, `transpose`,
             `unsqueeze`

:Examples 1:

>>> g = f.{+name}()
>>> g = f.{+name}('T')

:Parameters:

    {+axes, kwargs}

    {+i}

:Returns:

    out: `cf.{+Variable}`
        The squeezed field.

:Examples 2:

        '''     
        data_axes = self.data_axes()

        if axes is None and not kwargs:
            all_axes = self.axes()
            axes = [axis for axis in data_axes if all_axes[axis] == 1]
        else:
            axes = set(self.axes(axes, **kwargs)).intersection(data_axes)

        iaxes = [data_axes.index(axis) for axis in axes]      

        # Squeeze the field's data array
        f = super(Field, self).squeeze(iaxes, i=i)

        f._data_axes = [axis for axis in data_axes if axis not in axes]

        return f
    #--- End: def

#    def subspace(self, *args, **kwargs):
#        '''
#        '''
#        if not kwargs:
#            return self.copy()    
#
##        # List functionality
##        if self._list:
##            return type(self)([f[f.indices(*args, **kwargs)] for f in self])
#
#        return self[self.indices(*args, **kwargs)]
#    #--- End: def

    def transpose(self, axes=None, i=False, items=True, **kwargs):
        '''Permute the axes of the data array.

By default the order of the axes is reversed, but any ordering may be
specified by selecting the axes of the output in the required order.

The axes are selected with the *axes* parameter.

.. seealso:: `expand_dims`, `flip`, `squeeze`, `transpose`, `unsqueeze`

:Examples 1:

>>> g = f.{+name}()
>>> g = f.{+name}(['T', 'X', 'Y'])

.. seealso:: `axes`, `expand_dims`, `flip`, `squeeze`, `unsqueeze`

:Parameters:

    {+axes, kwargs}

    items: `bool`
        If False then metadata items (corodinates, cell measures,
        etc.) are not tranposed. By default, metadata items are
        tranposed so that their axes are in the same relative order as
        in the tranposed data array of the field.

    {+i}

:Returns:

    out: `cf.{+Variable}`
        The transposed field.

:Examples 2:

>>> f.items()
{'dim0': <CF DimensionCoordinate: time(12) noleap>,
 'dim1': <CF DimensionCoordinate: latitude(64) degrees_north>,
 'dim2': <CF DimensionCoordinate: longitude(128) degrees_east>,
 'dim3': <CF DimensionCoordinate: height(1) m>}
>>> f.data_axes()
['dim0', 'dim1', 'dim2']
>>> f.transpose()
>>> f.transpose(['Y', 'T', 'X'])
>>> f.transpose([1, 0, 2])
>>> f.transpose((1, 'time', 'dim2'))

        '''     
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('transpose', kwargs2)
 
        data_axes = self.data_axes()

        if _debug:
            print '{}.tranpose:'.format(self.__class__.__name__)
            print '    axes, kwargs:', axes, kwargs
            print '    shape =', self.shape

        if axes is None and not kwargs:
            axes2 = data_axes[::-1]
            iaxes = range(self.ndim-1, -1, -1)
        else:
            kwargs['ordered'] = True
            axes2 = list(self.axes(axes, **kwargs))
            if set(axes2) != set(data_axes):
                raise ValueError(
"Can't transpose {}: Bad axis specification: {!r}".format(
    self.__class__.__name__, axes))

            iaxes = [data_axes.index(axis) for axis in axes2]
        #---- End: if

        # Transpose the field's data array
        f = super(Field, self).transpose(iaxes, i=i)
                       
        # Reorder the list of data axes
        f._data_axes = axes2
        
        if _debug:
            print '    iaxes =', iaxes
            print '    axes2 =', f.data_axes()
            print '    shape =', f.shape

        if items:
            ndim = f.ndim
            for key, item in f.items(role=('d', 'a', 'm', 'f', 'c')).iteritems():
                item_ndim = item.ndim
                if item.ndim < 2:
                    # No need to transpose 1-d items
                    continue
                item_axes = f.item_axes(key)

                faxes = [axis for axis in axes2 if axis in item_axes]        
                for i, axis in enumerate(item_axes):
                    if axis not in faxes:
                        faxes.insert(i, axis)

                iaxes = [item_axes.index(axis) for axis in faxes]                
                if _debug:
                    print '    item, item_axes, iaxes:', repr(item), item_axes, iaxes

                f.transpose_item(key, iaxes)
                if _debug:
                    print '                      item:', repr(item)
        #--- End: if
        
        return f
    #--- End: def

    def transpose_item(self, description=None, iaxes=None, **kwargs):
        '''Permute the axes of a field item data array.

By default the order of the axes is reversed, but any ordering may be
specified by selecting the axes of the output in the required order.

The axes are selected with the *axes* parameter.

.. seealso:: `expand_dims`, `flip`, `squeeze`, `transpose`, `unsqueeze`

:Examples 1:

>>> g = f.{+name}()

.. seealso:: `axes`, `expand_dims`, `flip`, `squeeze`, `unsqueeze`

:Parameters:

    {+axes, kwargs}

:Returns:

    out: `cf.{+Variable}`
        The transposed field.

:Examples 2:

>>> f.items()
{'dim0': <CF DimensionCoordinate: time(12) noleap>,
 'dim1': <CF DimensionCoordinate: latitude(64) degrees_north>,
 'dim2': <CF DimensionCoordinate: longitude(128) degrees_east>,
 'dim3': <CF DimensionCoordinate: height(1) m>}
>>> f.data_axes()
['dim0', 'dim1', 'dim2']
>>> f.transpose()
>>> f.transpose(['Y', 'T', 'X'])
>>> f.transpose([1, 0, 2])
>>> f.transpose((1, 'time', 'dim2'))

        '''     
        key, item = self.key_item(description, **kwargs)
        item_axes = self.item_axes(key)            
        
        if iaxes is None and not kwargs:
            axes2 = item_axes[::-1]
            iaxes = range(item.ndim-1, -1, -1)
        else:
            if len(iaxes) != item.ndim:
                raise ValueError(
"Can't transpose {}: Bad axis specification: {!r}".format(
    item.__class__.__name__, axes))
            
            axes2 = [item_axes[i] for i in iaxes]
        #---- End: if

        # Transpose the item's data array
        item.transpose(iaxes, i=True)

        # Reorder the field's list of axes
        self.Items.axes(key=key, axes=axes2)
        
        return item
    #--- End: def

    def unlimited(self, *xxx):
        '''Todo ...


.. versionadded:: 1.3.1
        
.. seealso:: `cf.write`

:Examples 1:

Set the time axis to be unlimited when written to a netCDF file:

>>> f.{+name}({'T': True})

:Parameters:

    xxx: `dict` or `None`, optional

        Specify the chunk sizes for axes of the field. Axes are given
        by dictionary keys, with a chunk size for those axes as the
        dictionary values. A dictionary key of ``axes`` defines the
        axes that would be returned by the field's axes method,
        i.e. by ``f.axes(axes)``. See `cf.Field.axes` for details. In
        the special case of *xxx* being `None`, then chunking is
        set to the netCDF default.

          *Example:*
            To set time axes to be unlimited: ``{'T': True}``.

        Example:

            To set the chunk size for the first and third data array
        axes to 100: {0: 100, 2: 100}, or equivalently {(0, 2): 100}.
        Example:

            To set the chunk size for the longitude axis to 100 and
        for the air temperature axis to 5: {'X': 100,
        'air_temperature': 5}.  Example:

            To set the chunk size for all axes to 10: {None: 10}. This
        works because f.axes(None) returns all field axes.  Example:
        To set the chunking to the netCDF default: None.

:Returns:

    out: `dict`

:Examples 2:

        '''
        if len(xxx) > 1:
            raise ValueError("asfdds asdasdas4444444")

        org = {}
        for axis in self.axes():
            org[axis] = None            
            
        if self._unlimited:
            org.update(self._unlimited)

        if not xxx:
            return org
    
        xxx = xxx[0]

        if xxx is None:
            # Clear all settings
            self._unlimited = None
            return org

        _unlimited = {}
        for axes, value in xxx.iteritems():
            for axis in self.axes(axes):
                _unlimited[axis] = value

        if not _unlimited:        
            _unlimited = None

        self_unlimited = self._unlimited
        if self_unlimited is None:
            self._unlimited = _unlimited
        else:
            self._unlimited = self_unlimited.copy()
            self._unlimited.update(_unlimited)

        return org
    #--- End: def

    def unsqueeze(self, axes=None, i=False, **kwargs):
        '''Insert size 1 axes into the data array.

By default all size 1 domain axes which are not spanned by the field's
data array are inserted, but existing size 1 axes may be selected for
insertion.

The axes are selected with the *axes* parameter.

The axes are inserted into the slowest varying data array positions.

.. seealso:: `expand_dims`, `flip`, `squeeze`, `transpose`

:Examples 1:

>>> g = f.{+name}()
>>> g = f.{+name}('T', size=1)

:Parameters:

    {+axes, kwargs}

    {+i}

:Returns:

    out: `cf.{+Variable}`
        The unsqueezed field.

:Examples 2:

>>> print f
Data            : air_temperature(time, latitude, longitude)
Cell methods    : time: mean
Dimensions      : time(1) = [15] days since 1860-1-1
                : latitude(73) = [-90, ..., 90] degrees_north
                : longitude(96) = [0, ..., 356.25] degrees_east
                : height(1) = [2] m
Auxiliary coords:
>>> f.unsqueeze()
>>> print f
Data            : air_temperature(height, time, latitude, longitude)
Cell methods    : time: mean
Dimensions      : time(1) = [15] days since 1860-1-1
                : latitude(73) = [-90, ..., 90] degrees_north
                : longitude(96) = [0, ..., 356.25] degrees_east
                : height(1) = [2] m
Auxiliary coords:

        '''     
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('unsqueeze', kwargs2)
 
        data_axes = self.data_axes()
        axes = set(self.axes(axes, size=1, **kwargs)).difference(data_axes)

        if i:
            f = self
        else:
            f = self.copy()

        for axis in axes:
            f.expand_dims(0, axis, i=True)

        return f
    #--- End: def

    def aux(self, description=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, exact=False,
            inverse=False, match_and=True, ndim=None, key=False,
            copy=False):
        '''Return an auxiliary coordinate object.

In this documentation, an auxiliary coordinate object is referred to
as an "item".

{+item_selection}

{+item_criteria}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.item(role='a', inverse=False, **kwargs)``.
 

.. seealso:: `auxs`, `measure`, `coord`, `ref`, `dim`, `item`,
             `remove_item`

:Examples 1:

>>> a = f.{+name}('Y')
>>> a = f.{+name}('latitude')
>>> a = f.{+name}('long_name:latitude')
>>> a = f.{+name}('aux1')
>>> a = f.{+name}(axes_all='Y')

:Parameters:

    {+description}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}
        
    {+copy}

:Returns:

    out: `cf.AuxiliaryCoordinate` or `str` or `None`
       The unique auxiliary coordinate object or its domain identifier
       or, if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        role = ('a',)
#        return self.item(role=role, _restrict_inverse=role, **kwargs2)#
        return self.item(role=('a',), **kwargs2)
    #--- End: def

    def measure(self, description=None, axes=None, axes_all=None,
                axes_subset=None, axes_superset=None, exact=False,
                inverse=False, match_and=True, ndim=None,
                key=False, copy=False):
        '''Return a cell measure object, or its identifier.

In this documentation, a cell measure object is referred to as an
item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.measure(inverse=False, **kwargs)`` is equivalent to
``f.item(role='m', inverse=False, **kwargs)``.

.. seealso:: `aux`, `measures`, `coord`, `ref`, `dims`, `item`,
             `remove_item`

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}
        
    {+copy}

:Returns:

    out: `cf.CellMeasure` or `str` or `None`
        The unique cell measure object or its identifier or, if there
        is not one, `None`.
        
:Examples 2:

>>> f.measure('area')
<CF CellMeasure: area(73, 96) m 2>

        '''
        kwargs2 = self._parameters(locals())
        role = ('m',)
#        return self.item(role=role, _restrict_inverse=role, **kwargs2)
        return self.item(role=('m',), **kwargs2)
    #--- End: def

    def coord(self, description=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, ndim=None,
              match_and=True, exact=False, inverse=False, key=False,
              copy=False):
        '''Return a dimension or auxiliary coordinate object.

In this documentation, a dimension or auxiliary coordinate object is
referred to as an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.item(role='da', inverse=False, **kwargs)``.

.. seealso:: `aux`, `coords`, `dim`, `item`, `measure`, `ref`,
             `remove_item`,

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

    out: `cf.DimensionCoordinate` or `cf.AuxiliaryCoordinate` or `str` or `None`
        The unique dimension or auxiliary coordinate object or its
        identifier or, if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        role=('d', 'a')
#        return self.item(role=role, _restrict_inverse=role, **kwargs2)
        return self.item(role=('d', 'a'), **kwargs2)
    #--- End: def

    def dim(self, description=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, ndim=None,
            match_and=True, exact=False, inverse=False,
            key=False, copy=False):
        '''Return a dimension coordinate object, or its identifier.

In this documentation, a dimension coordinate object is referred to as
an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.item(role='d', inverse=False, **kwargs)``.

.. seealso:: `aux`, `measure`, `coord`, `ref`, `dims`, `item`,
             `remove_item`

:Examples 1:

>>> d = f.{+name}('Y')
>>> d = f.{+name}('latitude')
>>> d = f.{+name}('long_name:latitude')
>>> d = f.{+name}('dim1')
>>> d = f.{+name}(axes_all='Y')

:Parameters:

    {+description}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}
        
:Returns:

    out: `cf.DimensionCoordinate` or `str` or `None`
        The unique dimension coordinate object or its domain
        identifier or, if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
#        role=('d',)
#        return self.item(role=role, _restrict_inverse=role, **kwargs2)
        return self.item(role=('d',), **kwargs2)
    #--- End: def

    def domain_anc(self, description=None, axes=None, axes_all=None,
                   axes_subset=None, axes_superset=None, ndim=None,
                   match_and=True, exact=False, inverse=False,
                   key=False, copy=False):
        '''Return a domain ancillary object, or its identifier.

In this documentation, a dimension coordinate object is referred to as
an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.item(role='d', inverse=False, **kwargs)``.

.. seealso:: `aux`, `measure`, `coord`, `ref`, `dims`, `item`,
             `remove_item`

:Examples 1:

A latitude item could potentially be selected with any of:

>>> d = f.{+name}('Y')
>>> d = f.{+name}('latitude')
>>> d = f.{+name}('long_name:latitude')
>>> d = f.{+name}('dim1')
>>> d = f.{+name}(axes_all='Y')

:Parameters:

    {+description}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}
        
:Returns:

    out: `cf.DomainAncillary` or `str` or `None`
        The unique domain ancillary object or its domain identifier
        or, if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        role = ('c',)
#        return self.item(role=role, _restrict_inverse=role, **kwargs2)
        return self.item(role=('c',), **kwargs2)
    #--- End: def


    def ref(self, description=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, ndim=None,
            match_and=True, exact=False, inverse=False, key=False,
            copy=False):
        '''Return a coordinate reference object.

In this documentation, a coordinate reference object is referred to as
an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

.. seealso:: `item`, `refs`, `remove_item`

:Examples 1:

>>> c = f.{+name}('rotated_latitude_longitude')
>>> c = f.{+name}('ref1')

:Parameters:

    {+description}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}
        
:Returns:

    out:  `cf.CoordinateReference` or `str` or `None`
        The unique coordinate reference object or its identifier or,
        if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
#        role = ('r',)
#        return self.item(role=role, _restrict_inverse=role, **kwargs2)
        return self.item(role=('r',), **kwargs2)
    #--- End: def

    def auxs(self, description=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, ndim=None, match_and=True, 
             exact=False, inverse=False, copy=False):
        '''Return auxiliary coordinate objects.

In this documentation, an auxiliary coordinate object is referred to
as an item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='a', inverse=False, **kwargs)``.
 
.. seealso:: `aux`, `coords`, `dims`, `domain_ancs`, `field_ancs`,
             `items`, `measures` , `refs`, `remove_items`

:Examples 1:

>>> d = f.{+name}()

:Parameters:

    {+description}

          *Example:* 

            >>> x = f.items(['aux1',
            ...             'time',
            ...             {'units': 'degreeN', 'long_name': 'foo'}])
            >>> y = {}
            >>> for items in ['aux1', 'time', {'units': 'degreeN', 'long_name': 'foo'}]:
            ...     y.update(f.items(items))
            ...
            >>> set(x) == set(y)
            True

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of auxiliary coordinates. The dictionary
        will be empty if no items were selected.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
#        role = ('a',)
#        return self.items(role=role, _restrict_inverse=role, **kwargs2)
        return self.items(role=('a',), **kwargs2)
    #--- End: def

    def measures(self, description=None, axes=None, axes_all=None,
                 axes_subset=None, axes_superset=None, ndim=None, 
                 match_and=True, exact=False, inverse=False, copy=False):
        '''Return cell measure objects.

In this documentation, a cell measure object is referred to as an
item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='m', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `coords`, `dims`, `items`, `measure`, `refs`, 
             `remove_items`

:Examples 1:

>>> d = f.{+name}()

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of cell measure objects. The dictionary
        will be empty if no items were selected.


:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        role = ('m',)
#        return self.items(role=role, _restrict_inverse=role, **kwargs2)
        return self.items(role=role, **kwargs2)
    #--- End: def

    def coords(self, description=None, axes=None, axes_all=None,
               axes_subset=None, axes_superset=None, ndim=None,
               match_and=True, exact=False, inverse=False, copy=False):
        '''Return dimension and auxiliary coordinate objects of the field.

.. seealso:: `auxs`, `axes`, `measures`, `coord`, `refs`, `dims`,
             `items`, `remove_items`

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of coordinates objects. The dictionary
        may be empty.

:Examples:

        '''      
        kwargs2 = self._parameters(locals())
        role=('d', 'a')
#        return self.items(role=role, _restrict_inverse=role, **kwargs2)
        return self.items(role=role, **kwargs2)
    #--- End: def

    def dims(self, description=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, ndim=None,
             match_and=True, exact=False, inverse=False, copy=False):
        '''Return dimension coordinate objects.

In this documentation, a dimension coordinate object is referred to as
an item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='d', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `axes`, `measures`, `refs`, `coords`, `dim`,
             `items`, `remove_items`

:Examples 1:

>>> d = f.{+name}()

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict` 
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the field. The dictionary may
        be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        role = ('d',)
#        return self.items(role=role, _restrict_inverse=role, **kwargs2)
        return self.items(role=role, **kwargs2)
    #--- End: def

    def domain_ancs(self, description=None, axes=None, axes_all=None,
                    axes_subset=None, axes_superset=None, ndim=None,
                    match_and=True, exact=False, inverse=False,
                    copy=False):
        '''Return domain ancillary objects.

In this documentation, a domain ancillary object is referred to as an
item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='d', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `axes`, `measures`, `refs`, `coords`, `dim`,
             `items`, `remove_items`

:Examples 1:

>>> d = f.{+name}()

:Parameters:

    {+description}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out: `dict` 
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the field. The dictionary may
        be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        role = ('c',)
#        return self.items(role=role, _restrict_inverse=role, **kwargs2)
        return self.items(role=role, **kwargs2)
    #--- End: def

    def refs(self, description=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, ndim=None,
             match_and=True, exact=False, inverse=False, copy=False):
        '''Return coordinate reference objects.

In this documentation, a coordinate reference object is referred to as
an item.

{+item_selection}

.. seealso:: `items`, `ref`, `remove_items`

:Examples 1:

>>> d = f.{+name}()

:Parameters:
         
    {+description}

          *Example:* 

            >>> x = f.items(['ref1', 'latitude_longitude'])
            >>> y = {}
            >>> for items in ['ref1', 'latitude_longitude']:
            ...     y.update(f.items(items))
            ...
            >>> set(x) == set(y)
            True

    {+match_and}

    {+exact}
       
    {+inverse}

    {+copy}

:Returns:
 
    out: `dict` 
        A dictionary whose keys are domain item identifiers with
        corresponding values of coordinate references objects. The
        dictionary may be empty.

:Examples:

        '''  
        kwargs2 = self._parameters(locals())
        return self.items(role=('r',), **kwargs2)
    #--- End: def
    
    def item(self, description=None, role=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, exact=False,
             inverse=False, match_and=True, ndim=None, key=False,
             default=None, copy=False): #, _restrict_inverse=True):
        '''Return a field item.

{+item_definition}
 
{+item_selection}
 
The output is a the unique item found from the selection criteria (see
the *key* parameter).

If no unique item can be found which meets the given selection
critiera then the value of the *default* parameter is returned.

{+items_criteria}

To find multiple items, use the `~cf.Field.{+name}s` method.

.. seealso:: `aux`, `measure`, `coord`, `ref`, `dim`, `item_axes`,
             `items`, `remove_item`

:Examples 1:

>>> item = f.{+name}('X')

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+default}

    {+copy}

:Returns:

    out: 
        The unique item or its identifier or, if there is no
        unique item, the value of the *default* parameter.

:Examples 2:

>>>

        '''
        kwargs2 = self._parameters(locals())

#        kwargs2['items'] = kwargs.pop('item')

        if key:
            del kwargs2['key']
            del kwargs2['copy']
            return self.key(**kwargs2)

        del kwargs2['key']
        del kwargs2['default']
        d = self.items(**kwargs2)
        if not d:
            return default

        items = d.popitem()

        return default if d else items[1]
    #--- End: def

    def key(self, description=None, role=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, exact=False,
            inverse=False, match_and=True, ndim=None, default=None):
#            _restrict_inverse=False):
        '''Return the identifier of a field item.

{+item_definition}
 
If no unique item can be found then the value of the *default*
parameter is returned.

{+item_selection}
 
.. versionadded:: 2.0

.. seealso:: `item`, `items`

:Examples 1:

>>> key = f.{+name}('X')

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+default}

:Returns:

    out: 
        The unique item identifier or, if there is no unique item, the
        value of the *default* parameter.

:Examples 2:

>>>
        '''
        kwargs2 = self._parameters(locals())

#        kwargs2['items'] = kwargs.pop('item')

        del kwargs2['default']

        d = self.items(**kwargs2)
        if not d:
            return default

        items = d.popitem()

        return default if d else items[0]
    #--- End: def

    def key_item(self, description=None, role=None, axes=None,
                 axes_all=None, axes_subset=None, axes_superset=None,
                 exact=False, inverse=False, match_and=True,
                 ndim=None, default=(None, None)):
        '''Return an item, or its identifier, from the field.

{+item_definition}
 
If no unique item can be found then the value of the *default*
parameter is returned.

{+item_selection}

.. versionadded:: 2.0 

.. seealso:: `item`, `items`

:Examples 1:

>>> key, item = f.{+name}('X')

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+default}

:Returns:

    out: 
        The unique item identifier or, if there is no unique item, the
        value of the *default* parameter.

:Examples 2:

>>>

        '''
        kwargs2 = self._parameters(locals())

#        kwargs2['items'] = kwargs.pop('item')

        del kwargs2['default']

        d = self.items(**kwargs2)
        if not d:
            return default

        items = d.popitem()

        return default if d else items
    #--- End: def

    def axis_name(self, axes=None, default=None, **kwargs):
        '''Return the canonical name for an axis.

{+axis_selection}

.. seealso:: `axis`, `axis_size`, `item`

:Parameters:

    {+axes, kwargs}

:Returns:

    out: `str`
        The canonical name for the axis.

:Examples:

>>> f.axis_name('dim0')
'time'
>>> f.axis_name('X')
'domain%dim1'
>>> f.axis_name('long_name%latitude')
'ncdim%lat'

        '''      
        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:
            return default
#            raise ValueError("No unique axis could be identified")

        return self.Items.axis_name(axis, default=default)
    #--- End: def

    def axes_names(self, axes=None, **kwargs):
        '''Return the canonical names for domain axes.

{+axis_selection}

.. seealso:: `axis`, `axis_name`, `axis_size`, `item`

:Parameters:

    {+axes, kwargs}

:Returns:

    out: `dict`
        The canonical name for the axis. DCH

:Examples:

>>> f.axis_names()
'time' DCH
>>> f.axis_name('X')
'domain%dim1' DCH
>>> f.axis_name('long_name%latitude')
'ncdim%lat' DCH

        '''          
        out = {}
        for axis in self._Axes:
            out[axis] = self.Items.axis_name(axis)

        return out
    #--- End: def

    def axis_size(self, axes=None, **kwargs):
        '''Return the size of a domain axis.

{+axis_selection}

.. seealso:: `axis`, `axis_name`, `axis_identity`

:Parameters:

    {+axes, kwargs}

:Returns:
    
    out: `int`
        The size of the axis.

:Examples:

>>> f
<CF Field: eastward_wind(time(3), air_pressure(5), latitude(110), longitude(106)) m s-1>
>>> f.axis_size('longitude')
106
>>> f.axis_size('Z')
5
        '''
        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:
            return None

        return self._Axes[axis].size
    #--- End: def

    def axes(self, axes=None, size=None, ordered=False, **kwargs):
        '''Return domain axis identifiers from the field.

The output is a set of domain axis identifiers, which may be empty.

{+axis_selection}

.. seealso:: `axis`, `data_axes`, `item_axes`, `items`, `remove_axes`

:Parameters:

    {+axes, kwargs}

          *Example:*

            >>> x = f.axes(['dim2', 'time', {'units': 'degree_north'}])
            >>> y = set()
            >>> for axes in ['dim2', 'time', {'units': 'degree_north'}]:
            ...     y.update(f.axes(axes))
            ...
            >>> x == y
            True
 
    {+size}

    ordered: `bool`, optional
        Return an ordered list of axes instead of an unordered
        set. The order of the list will reflect any ordering specified
        by the *axes* and *kwargs* parameters.

          *Example:*
            If the data array axes, as returned by the field's
            `data_axes` method, are ``['dim0', 'dim1', 'dim2']``, then
            ``f.axes([2, 0, 1, 2])`` will return ``set(['dim0',
            'dim1', 'dim2'])``, but ``f.axes([2, 0, 1, 2],
            ordered=True)`` will return ``['dim2', 'dim0', 'dim1',
            'dim2']``.

:Returns:

    out: `dict` or `OrderedDict`
        A dictionary of domain axis identifiers and their sizes, or an
        `OrderedDict` if *ordered* is True.

:Examples:

All axes and their identities:

>>> f.axes()
set(['dim0', 'dim1', 'dim2', 'dim3'])
>>> dict([(axis, f.domain.axis_name(axis)) for axis in f.axes()])
{'dim0': time(12)
 'dim1': height(19)
 'dim2': latitude(73)
 'dim3': longitude(96)}

Axes which are not spanned by the data array:

>>> f.axes().difference(f.data_axes())

        '''
        def _axes(self, axes, size, items_axes, data_axes, domain_axes,
                  kwargs):
            ''':Parameters:

        items_axes: `dict`
            Dictionary of item axes keyed by the item identifiers.

        data_axes: sequence of `str`
            The domain axis identifiers for the data array.
            
        domain_axes: `dict`
            Dictionary of `cf.DomainAxis` objects keyed by their
            identifiers.

            '''
            a = None

            if axes is not None:
                if axes.__hash__:
                    if isinstance(axes, slice):
                        # --------------------------------------------
                        # axes is a slice object
                        # -------------------------------------------
                        if data_axes is not None:
                            try:                            
                                a = tuple(data_axes[axes])
                            except IndexError:
                                a = []
                        else:
                            a = []
                    elif axes in domain_axes:
                        # --------------------------------------------
                        # axes is a domain axis identifier
                        # --------------------------------------------
                        a = [axes]
                    elif axes in items_axes and not kwargs:
                        # --------------------------------------------
                        # axes is a domain item identifier
                        # --------------------------------------------
                        a = items_axes[axes][:]
                    else:
                        try:
                            axes_is_ncdim_name = axes.startswith('ncdim%')
                        except AttributeError:
                            axes_is_ncdim_name = False

                        if axes_is_ncdim_name:
                            # ----------------------------------------
                            # axes is a netCDF dimension name
                            # ----------------------------------------
                            ncdimensions = self.ncdimensions
                            if ncdimensions:
                                ncdim = axes[6:]  # Note: There are 6 characters in 'ncdim%'
                                tmp = []
                                for axis, value in ncdimensions.iteritems():
                                    if value == ncdim:
                                        tmp.append(axis)
                                if tmp:
                                    a = tmp
                        else:
                            try:
                                # --------------------------------
                                # If this works then axes is a
                                # valid integer
                                # --------------------------------
                                a = [data_axes[axes]]
                            except IndexError:
                                # axes is an out-of bounds integer
                                a = []
                            except TypeError:
                                # ------------------------------------
                                # Axes is something else, or data_axes
                                # is None
                                # ------------------------------------
                                a = None    
                #--- End: if
 
            elif not kwargs:
#                a = list(domain_axes)
                if not data_axes:
                    data_axes = ()
                a = []
                for x in domain_axes:
                    if x not in data_axes:
                        a.append(x)

                a.extend(data_axes)
            #--- End: if

            if a is None:
                # ----------------------------------------------------
                # Assume that axes is a value accepted by the items
                # method
                # ----------------------------------------------------
                a = [] 
                kwargs2 = kwargs.copy()
                kwargs2['axes'] = None
                for key in self.items(axes, **kwargs2):
                    a += items_axes.get(key, ())
            #--- End: if

            if size:
                a = [axis for axis in a if size == domain_axes[axis]]

            return a
        #--- End: def

#        role = kwargs.get('role', None)
#        if role is None:
#            # By default, omit coordinate reference items from the
#            # axis selection.
#            kwargs['role'] = ('d', 'a', 'm', 'f', 'c')

        domain_axes = self._Axes

        data_axes  = self.data_axes()
        items_axes = self.items_axes()

        if axes is None or isinstance(axes, (basestring, dict, slice,
                                             int, long)):
            # --------------------------------------------------------
            # axes is not a sequence or a set
            # --------------------------------------------------------
            a = _axes(self, axes, size, items_axes, data_axes,
                      domain_axes, kwargs)
        else:   
            # --------------------------------------------------------
            # axes is a sequence or a set
            # --------------------------------------------------------
            a = []
            for x in axes:
                a += _axes(self, x, size, items_axes, data_axes,
                           domain_axes, kwargs)
        #--- End: if

        if ordered:
            out = OrderedDict()
        else:
            out = {}    

        for x in a:
            out[x] = domain_axes[x]
            
#            out = a

        return out
    #--- End: def
        
    def axis(self, axes=None, size=None, default=None, key=False,
             **kwargs):
        '''Return a domain axis.

{+axis_selection}

.. seealso:: `axes`, `data_axes`, `item_axes`, `item`, `remove_axis`

:Examples 1:

>>> a = f.{+name}('time')

:Parameters:

    {+axes, kwargs}
 
    {+size}

:Returns:

    out: `str` or `None`
        The unique domain axis, or its identifier or, if there is no
        unique item, `None`.

:Examples 2:

>>> f
<CF Field: air_temperature(time(12), latitude(64), longitude(128)) K>
>>> f.data_axes()
['dim0', 'dim1', 'dim2']
>>> f.axis('time')
'dim0'
>>> f.axis('Y')
'dim1'
>>> f.axis(size=64)
'dim1'
>>> f.axis('X', size=128)
'dim2'
>>> print f.axis('foo')
None
>>> print f.axis('T', size=64)
None

        '''
        kwargs2 = self._parameters(locals())

        key = kwargs2.pop('key')

        del kwargs2['default'] 
        kwargs2['ordered'] = False  
        d = self.axes(**kwargs2)
        if not d:
            return default

        axes = d.popitem()

        if d:
            return default 

        if key:
            return axes[0]
        else:
            return axes[1]

#        return default if d else axes[0]
    #--- End: def

    def insert_cell_methods(self, item):
        '''Insert one or more cell method objects into the field.

.. seealso:: `insert_aux`, `insert_measure`, `insert_ref`,
             `insert_data`, `insert_dim`

:Parameters:

    item: `str` or `cf.CellMethods`

:Returns:

    out: `cf.CellMethods`
        The identifier of the new axis.


:Examples:

        '''
        cm = CellMethods(item)
        self.Items.cell_methods.extend(cm)
        self._conform_cell_methods(self.CellMethods)
    #--- End: def

    def insert_axis(self, axis, key=None, replace=True):
        '''Insert a domain axis into the field.

.. seealso:: `insert_aux`, `insert_measure`, `insert_ref`,
             `insert_data`, `insert_dim`

:Parameters:

    axis: `cf.DomainAxis`
        The new domain axis.

    key: `str`, optional
        The identifier for the new axis. By default a new,
        unique identifier is generated.
  
    replace: `bool`, optional
        If False then do not replace an existing axis with the same
        identifier but a different size. By default an existing axis
        with the same identifier is changed to have the new size.

:Returns:

    out: `str`
        The identifier of the new domain axis.


:Examples:

>>> f.insert_axis(cf.DomainAxis(1))
>>> f.insert_axis(cf.DomainAxis(90), key='dim4')
>>> f.insert_axis(cf.DomainAxis(23), key='dim0', replace=False)

        '''
        if key is None:
            key = self.new_identifier('axis')

#        if key is None:
#            if axes is None:
#                key = self.new_identifier('axis')
#            else:
#                # key is not set but axes is
#                key = axes[0]
#        elif axes is not None:
#            # key and axes are set
#            if axes[0] != key:
#                raise ValueError(
#"Incompatible key and axes parameters: {}, {}".format(key, axes))

        if not replace and key in self._Axes and self._Axes[key].size != axis.size:
            raise ValueError(
"Can't insert axis: Existing axis {!r} has different size (got {}, expected {})".format(
    key, axis.size, self._Axes[key].size))

        self._Axes[key] = axis

        return key
    #--- End: def

    def new_identifier(self, item_type):
        '''

Return a new, unique auxiliary coordinate identifier for the domain.

.. seealso:: `new_measure_identifier`, `new_dimemsion_identifier`,
             `new_ref_identifier`

The domain is not updated.

:Parameters:

    item_type: `str`

:Returns:

    out: `str`
        The new identifier.

:Examples:

>>> d.items().keys()
['aux2', 'aux0', 'dim1', 'ref2']
>>> d.new_identifier('aux')
'aux3'
>>> d.new_identifier('ref')
'ref1'

>>> d.items().keys()
[]
>>> d.new_identifier('dim')
'dim0'


>>> d.axes()
{'dim0', 'dim4'}
>>> d.new_identifier('axis')
'dim2'

>>> d.axes()
{}
>>> d.new_identifier('axis')
'dim0'

'''
        if item_type in ('axis', 'dim'):
            keys = self._Axes
            item_type = 'dim'
        else:
            keys = getattr(self.Items, item_type[0])
        
        n = len(keys)
        key = '{0}{1}'.format(item_type, n)

        while key in keys:
            n += 1
            key = '{0}{1}'.format(item_type, n)
        #--- End: while

        return key
    #--- End: def

    def _insert_item(self, variable, key, role, axes=None, copy=True,
                     replace=True, scalar=False):
        '''

Insert a new auxiliary coordinate into the domain in place, preserving
internal consistency.

:Parameters:

    item: `cf.Variable`

    key: `str`
        The identifier for the auxiliary coordinate or cell
        measure.

    role: `str`

    axes: sequence, optional
        The ordered axes of the new coordinate. Ignored if the
        coordinate is a dimension coordinate. Required if the
        coordinate is an auxiliary coordinate.

    copy: `bool`, optional
        If False then the auxiliary coordinate is not copied before
        insertion. By default it is copied.

    replace: `bool`, optional
        If False then do not replace an existing dimension coordinate
        with the same identifier. By default an existing dimension
        coordinate with the same identifier is replaced with *coord*.

:Returns:

    out: `cf.Variable`

:Examples:

>>>

'''
        if key in self._item_axes and not replace:
            raise ValueError(
"Can't insert {0}: Identifier {1!r} already exists".format(role, key))

        ndim = variable.ndim
        if not ndim:
            ndim = 1
            
        if axes is None:
            # --------------------------------------------------------
            # The axes have not been set => infer the axes.
            # --------------------------------------------------------
            variable_shape = variable.shape
            if scalar and not variable_shape:
                axes = []
            else:
                if (not variable_shape or 
                    len(variable_shape) != len(set(variable_shape))):
                    raise ValueError(
"Ambiguous %s shape: %s. Consider setting the axes parameter." %
(variable.__class__.__name__, variable_shape))

                axes = []
                axes_sizes = self.axes().values()
                for n in variable_shape:
                    if axes_sizes.count(n) == 1:
                        axes.append(self.axis(size=n, key=True))
                    else:
                        raise ValueError(
"Ambiguous %s shape: %s. Consider setting the axes parameter." %
(variable.__class__.__name__, variable_shape))
            #--- End: if

        else:
            # --------------------------------------------------------
            # Axes have been provided
            # --------------------------------------------------------
#            axes = self._asd(variable, role, axes, scalar=scalar)
            ndim = variable.ndim
            if not ndim and not scalar:
                ndim = 1
            
            axes = list(self.axes(axes, ordered=True))
            
            if len(set(axes)) != ndim:
                raise ValueError(
                    "Can't insert %s: Mismatched number of axes (%d != %d)" % 
                    (role, len(set(axes)), ndim))

            axes2 = []                
            for axis, size in izip_longest(axes, variable.shape, fillvalue=1):
                axis_size = self.axis_size(axis)
                if size != axis_size:
                    raise ValueError(
                        "Can't insert %s: Mismatched axis size (%d != %d)" % 
                        (role, size, axis_size))

                axes2.append(axis)
            #--- End: for
            axes = axes2

            n_axes = len(set(axes))
            if not (ndim == n_axes or (ndim == 0 and n_axes == 1)):
                raise ValueError(
"Can't insert {0}: Mismatched number of axes ({1} != {2})".format(
role, n_axes, ndim))
        #-- End: if

        if not scalar and not variable.ndim:
            # Turn a scalar item into size 1, 1-d item, copying it if
            # required.
            variable.expand_dims(0, i=(not copy))
        elif copy:
            # Copy the variable
            variable = variable.copy()

        return variable, axes
    #--- End: def

    def insert_field_anc(self, item, key=None, axes=None, copy=True,
                         replace=True):
        '''Insert a field ancillary object into the field.
        
        '''
        if key is None:
            key = self.new_identifier('fav')
        elif key in self.Items.f and not replace:
            raise ValueError(
"Can't insert field ancillary object: Identifier {0!r} already exists".format(key))

        if not isinstance(item, FieldAncillary):
            if isinstance(item, Field):
                if not axes:
                    axis_map = item.map_axes(self)
                    axes = [axis_map[axis] for axis in item.data_axes()]
            #--- End: if
            item = FieldAncillary(source=item, copy=copy)
        #--- End: if

        axes = self._insert_item_parse_axes(item, 'field ancillary', 
                                            axes, allow_scalar=True)

        self.Items.insert_field_anc(item, key=key, axes=axes, copy=False)

        return key
    #--- End: def

    def insert_domain_anc(self, item, key=None, axes=None, copy=True,
                          replace=True):
        '''Insert a domain ancillary object into the field.
        '''
        if key is None:
            key = self.new_identifier('cct')
        elif key in self.Items.c and not replace:
            raise ValueError(
"Can't insert domain ancillary object: Identifier {0!r} already exists".format(key))

        if not isinstance(item, DomainAncillary):
            if isinstance(item, Field):
                if not axes:
                    axis_map = item.map_axes(self)
                    axes = [axis_map[axis] for axis in item.data_axes()]
            #--- End: if
            item = DomainAncillary(source=item, copy=copy)
        #--- End: if

        axes = self._insert_item_parse_axes(item, 'domain ancillary', 
                                            axes, allow_scalar=True)

        self.Items.insert_domain_anc(item, key=key, axes=axes, copy=False)

        refs = self.refs()
        if refs:
            for ref in refs.itervalues():
                self._conform_ref(ref, i=True)

        return key
    #--- End: def

    def _conform_ref(self, ref, i=False):
        '''Where possible, replace the content of ref.coordinates with
coordinate identifiers and the values of domain ancillary terms with
domain ancillary identifiers.

:Parameters:

    ref: `cf.CoordinateReference`

:Returns:

    `None`

:Examples:

>>> s = f._conform_ref(r)
>>> s = f._conform_ref(r, i=True)

        '''
        if not i:
            ref = ref.copy()

        identity_map = {}
        role = ('d', 'a')        
        for identifier in ref.coordinates:
            key = self.Items.key(identifier, role=role, exact=True)
            if key is not None:
                identity_map[identifier] = key
        #--- End: for
        ref.change_identifiers(identity_map, ancillary=False, i=True)
 
        identity_map = {}
        role = ('c',)
        for identifier in ref.ancillaries.values():
            key = self.key(identifier, role=role, exact=True)
            if key is not None:
                identity_map[identifier] = key
        #--- End: for
# DCH inplace??
        ref.change_identifiers(identity_map, coordinate=False, i=True)
    #--- End: def

    def _conform_cell_methods(self, cms):
        '''

:Parameters:

:Returns:

    `None`

:Examples:

>>> f._conform_cell_methods()

        '''
        axis_map = {}
        for cm in cms:
            for axis in cm.axes:
                if axis in axis_map:
                    continue
                if axis == 'area':
                    axis_map[axis] = axis
                    continue
                axis_map[axis] = self.axis(axis, role=('d', 'a'), ndim=1, 
                                           default=axis, key=True)
        #--- End: for

        self.CellMethods.change_axes(axis_map, i=True)
    #--- End: def

    def _unconform_cell_methods(self, cms):
        '''

:Parameters:

:Returns:

    `None`

:Examples:

>>> f._conform_cell_methods()

        '''
        axes_names = self.axes_names()

        axis_map = {}
        for cm in cms:
            for axis in cm.axes:
                if axis in axes_names:
                    axis_map[axis] = axes_names.pop(axis)

        return cms.change_axes(axis_map, i=False)
    #--- End: def

    def _unconform_ref(self, ref, i=False):
        '''Replace the content of ref.coordinates with coordinate identifiers
and domain ancillaries where possible.

:Parameters:

    ref: `cf.CoordinateReference`

:Returns:

    `None`

:Examples:

>>> s = f._unconform_ref(r)
>>> s = f._unconform_ref(r, i=True)
        
        '''
        if not i:
            ref = ref.copy()
            
        identity_map = {}
        role = ('d', 'a')        
        for identifier in ref.coordinates:
            item = self.item(identifier, role=role, exact=True)
            if item is not None:
                identity_map[identifier] = item.identity()
        #--- End: for
        ref.change_identifiers(identity_map, ancillary=False, strict=True, i=True)
 
        identity_map = {}
        role = ('c',)
        for identifier in ref.ancillaries.values():
            anc = self.item(identifier, role=role, exact=True)
            if anc is not None:
                identity_map[identifier] = anc.identity()
        #--- End: for
        ref.change_identifiers(identity_map, coordinate=False, strict=True, i=True)
# DCH inplace??
        return ref
    #--- End: def

    def insert_item(self, role, item, key=None, axes=None,
                    copy=True, replace=True):
        '''Insert an item into the field.

.. seealso:: `insert_axis`, `insert_measure`, `insert_data`,
             `insert_dim`, `insert_ref`

:Parameters:

    role: `str`

    item: `cf.AuxiliaryCoordinate` or `cf.Coordinate` or `cf.DimensionCoordinate`
        The new auxiliary coordinate object. If it is not already a
        auxiliary coordinate object then it will be converted to one.

    key: `str`, optional
        The identifier for the *item*. By default a new, unique
        identifier will be generated.

    axes: sequence of `str`, optional
        The ordered list of axes for the *item*. Each axis is given by
        its identifier. By default the axes are assumed to be
        ``'dim0'`` up to ``'dimM-1'``, where ``M-1`` is the number of
        axes spanned by the *item*.

    copy: `bool`, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace: `bool`, optional
        If False then do not replace an existing auxiliary coordinate
        object of domain which has the same identifier. By default an
        existing auxiliary coordinate object with the same identifier
        is replaced with *item*.
    
:Returns:

    out: `str`
        The identifier for the inserted *item*.

:Examples:

>>>
        '''
        kwargs2 = self._parameters(locals())
        del kwargs2['role']

        if role == 'd':
            return self.insert_dim(**kwargs2)
        if role == 'a':
            return self.insert_aux(**kwargs2)
        if role == 'm':
            return self.insert_measure(**kwargs2)
        if role == 'c':
            return self.insert_domain_anc(**kwargs2)
        if role == 'f':
            return self.insert_field_anc(**kwargs2)
        if role == 'r':
            return self.insert_ref(**kwargs2)
    #--- End: def

    def insert_aux(self, item, key=None, axes=None, copy=True, replace=True):
        '''Insert an auxiliary coordinate object into the field.

.. seealso:: `insert_axis`, `insert_measure`, `insert_data`,
             `insert_dim`, `insert_ref`

:Parameters:

    item: `cf.AuxiliaryCoordinate` or `cf.DimensionCoordinate`
        The new auxiliary coordinate object. If it is not already a
        auxiliary coordinate object then it will be converted to one.

    key: `str`, optional
        The identifier for the *item*. By default a new, unique
        identifier will be generated.

    axes: sequence of `str`, optional
        The ordered list of axes for the *item*. Each axis is given by
        its identifier. By default the axes are assumed to be
        ``'dim0'`` up to ``'dimM-1'``, where ``M-1`` is the number of
        axes spanned by the *item*.

    copy: `bool`, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace: `bool`, optional
        If False then do not replace an existing auxiliary coordinate
        object of domain which has the same identifier. By default an
        existing auxiliary coordinate object with the same identifier
        is replaced with *item*.
    
:Returns:

    out: `str`
        The identifier for the inserted *item*.

:Examples:

>>>

        '''

        item = item.asauxiliary(copy=copy)            

        if key is None:
            key = self.new_identifier('aux')

        if key in self.axes() and not replace:
            raise ValueError(
"Can't insert auxiliary coordinate object: Identifier {0!r} already exists".format(key))

        axes = self._insert_item_parse_axes(item, 'auxiliary coordinate', axes,
                                            allow_scalar=False)

        if item.isscalar:
            # Turn a scalar auxiliary coordinate into 1-d
            item.expand_dims(0, i=True)

        self.Items.insert_aux(item, key=key, axes=axes, copy=False)

        # Update coordindate references
        refs = self.refs()
        if refs:
            for ref in refs.itervalues():
                self._conform_ref(ref, i=True)

        # Update cell methods
        cms = self.CellMethods
        if cms:
            self._conform_cell_methods(cms)

        return key
    #--- End: def

    def _insert_item_parse_axes(self, item, role, axes=None, allow_scalar=True):
        '''
        '''
        all_axes = self.axes()

        if axes is None:
            # --------------------------------------------------------
            # The axes have not been set => infer the axes.
            # --------------------------------------------------------
            shape = item.shape
            if allow_scalar and not shape:
                axes = []
            else:
                if not allow_scalar and not shape:
                    shape = (1,)

                if not shape or len(shape) != len(set(shape)):
                    raise ValueError(
"Can't insert {0}: Ambiguous shape: {1}. Consider setting the 'axes' parameter.".format(
    item.__class__.__name__, shape))

                axes = []
                axes_sizes = all_axes.values()
                for n in shape:
                    if axes_sizes.count(n) == 1:
                        axes.append(self.axis(size=n, key=True))
                    else:
                        raise ValueError(
"Can't insert {} {}: Ambiguous shape: {}. Consider setting the 'axes' parameter.".format(
    item.name(default=''), item.__class__.__name__, shape))
            #--- End: if

        else:
            # --------------------------------------------------------
            # Axes have been provided
            # --------------------------------------------------------
            ndim = item.ndim
            if not ndim and not allow_scalar:
                ndim = 1

            axes = list(self.axes(axes, ordered=True))

            if len(set(axes)) != ndim:
                raise ValueError(
"Can't insert {} {}: Mismatched number of axes ({} != {})".format(
    item.name(default=''), item.__class__.__name__, len(set(axes)), ndim))

            axes2 = []                
            for axis, size in izip_longest(axes, item.shape, fillvalue=1):
                if size != self.axis_size(axis):
                    raise ValueError(
"Can't insert {} {}: Mismatched axis size ({} != {})".format(
    item.name(default=''), item.__class__.__name__, size, self.axis_size(axis)))

                axes2.append(axis)
            #--- End: for
            axes = axes2

            if ndim != len(set(axes)):
                raise ValueError(
"Can't insert {} {}: Mismatched number of axes ({} != {})".format(
    item.name(default=''), item.__class__.__name__, len(set(axes)), ndim))
        #--- End: if
    
        return axes
    #--- End: def

    def insert_measure(self, item, key=None, axes=None, copy=True, replace=True):
        '''Insert a cell measure object into the field.

.. seealso:: `insert_axis`, `insert_aux`, `insert_data`, `insert_dim`,
             `insert_ref`

:Parameters:

    item: `cf.CellMeasure`
        The new cell measure object.

    key: `str`, optional
        The identifier for the *item*. By default a new, unique
        identifier will be generated.

    axes: sequence of `str`, optional
        The ordered list of axes for the *item*. Each axis is given by
        its identifier. By default the axes are assumed to be
        ``'dim0'`` up to ``'dimM-1'``, where ``M-1`` is the number of
        axes spanned by the *item*.

    copy: `bool`, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace: `bool`, optional
        If False then do not replace an existing cell measure object
        of domain which has the same identifier. By default an
        existing cell measure object with the same identifier is
        replaced with *item*.
    
:Returns:

    out: 
        The identifier for the *item*.

:Examples:

>>>

        '''
        if key is None:
            key = self.new_identifier('msr')

        if key in self.axes() and not replace:
            raise ValueError(
"Can't insert cell measure object: Identifier {0!r} already exists".format(key))

        axes = self._insert_item_parse_axes(item, 'cell measure', axes,
                                            allow_scalar=False)

        if copy:
            item = item.copy()

        if item.isscalar:
            # Turn a scalar auxiliary coordinate into 1-d
            item.expand_dims(0, i=True)

        self.Items.insert_measure(item, key=key, axes=axes, copy=False)

        return key
    #--- End: def

    def insert_dim(self, item, key=None, axes=None, copy=True, replace=True):
        '''Insert a dimension coordinate object into the field.

.. seealso:: `insert_aux`, `insert_axis`, `insert_item`,
             `insert_measure`, `insert_data`, `insert_ref`,
             `remove_item`

:Parameters:

    item: `cf.DimensionCoordinate` or `cf.Coordinate` or `cf.AuxiliaryCoordinate`
        The new dimension coordinate object. If it is not already a
        dimension coordinate object then it will be converted to one.

    axes: sequence of `str`, optional
        The axis for the *item*. The axis is given by its domain
        identifier. By default the axis will be the same as the given
        by the *key* parameter.

    key: `str`, optional
        The identifier for the *item*. By default a new, unique
        identifier will be generated.

    copy: `bool`, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace: `bool`, optional
        If False then do not replace an existing dimension coordinate
        object of domain which has the same identifier. By default an
        existing dimension coordinate object with the same identifier
        is replaced with *item*.
    
:Returns:

    out: 
        The identifier for the inserted *item*.

:Examples:

>>>

        '''
        item = item.asdimension(copy=copy)            

#        if key is None and axes is None:
#            # Key is not set, axes is not set
#            key = self.insert_axis(DomainAxis(item.size))
#            axes = [key]
            
        if key is None and axes is None:
            # Key is not set and axes is not set
            item_size = item.size
            c = [axis for axis, domain_axis in self._Axes.iteritems() 
                 if domain_axis == item_size]
            if len(c) == 1:
                key = c[0]
                if self.dims(axes_all=key):
                    key = self.insert_axis(DomainAxis(item_size))
                axes = [key]
            elif not c:
                key = self.insert_axis(DomainAxis(item_size))
                axes = [key]
            else:
                raise ValueError(
"Ambiguous dimension coordinate object size. Condsider setting the key or axes parameter")

##        if key is None and axes is None:
#            # Key is not set, axes is not set
#            item_size = item.size
#            c = [axis for axis, size in self._Axes.iteritems() 
#                 if size == item_size]
#            if len(c) == 1:                
#                key = c[0]
#                axes = [key]
#            elif not c:
#                key = self.insert_axis(DomainAxis(item_size))
#                axes = [key]
#            else:
#                raise ValueError("asdasdas 08qywh liauh ,")
        elif key is not None:
            if axes is None:
                # Key is set, axes is not set
                axes = [key]
                if key not in self._Axes:
                    key = self.insert_axis(DomainAxis(item.size), key=key)
            elif axes != [key]:
                # Key is set, axes is set
                raise ValueError(
                    "Incompatible key and axes parameters: {0!r}, {1!r}".format(
                        key, axes))

            axes = self._insert_item_parse_axes(item, 'dimension coordinate',
                                                axes, allow_scalar=False)
        else:
            # Key is not set, axes is set
            key = axes[0]
            axes = self._insert_item_parse_axes(item, 'dimension coordinate',
                                                axes, allow_scalar=False)    

        if key in self.Items.d and not replace:
            raise ValueError(
"Can't insert dimension coordinate object: Identifier {0!r} already exists".format(key))

        if item.isscalar:
            # Turn a scalar object into 1-d
            item.expand_dims(0, i=True)

        self.Items.insert_dim(item, key=key, axes=axes, copy=False)

        self.autocyclic()

        refs = self.Items.refs()
        if refs:
            for ref in refs.itervalues():
                self._conform_ref(ref, i=True)
        refs = self.Items.refs()

        cms = self.CellMethods
        if cms:
            self._conform_cell_methods(cms)

        return key
    #--- End: def

    def insert_ref(self, item, key=None, axes=None, copy=True, replace=True):
        '''Insert a coordinate reference object into the field.

.. seealso:: `insert_axis`, `insert_aux`, `insert_measure`,
             `insert_data`, `insert_dim`
             
:Parameters:

    item: `cf.CoordinateReference`
        The new coordinate reference object.

    key: `str`, optional
        The identifier for the *item*. By default a new, unique
        identifier will be generated.

    axes: *optional*
        *Ignored*

    copy: `bool`, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace: `bool`, optional
        If False then do not replace an existing coordinate reference object of
        domain which has the same identifier. By default an existing
        coordinate reference object with the same identifier is replaced with
        *item*.
    
:Returns:

    out: 
        The identifier for the *item*.


:Examples:

>>>

        '''
        if key is None:
            key = self.new_identifier('ref')

        if copy:
            item = item.copy()

        self._conform_ref(item, i=True)

        self.Items.insert_ref(item, key=key, copy=False)

        return key
    #--- End: def

    def item_axes(self, description=None, role=None, axes=None,
                  axes_all=None, axes_subset=None, axes_superset=None,
                  exact=False, inverse=False, match_and=True,
                  ndim=None, default=None):
        '''Return the axes of a domain item of the field.

An item is a dimension coordinate, an auxiliary coordinate, a cell
measure or a coordinate reference object.

.. seealso:: `axes`, `data_axes`, `item`

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

:Returns:

    out: `list` or `None`
        The ordered list of axes for the item or, if there is no
        unique item or the item is a coordinate reference then `None`
        is returned.

:Examples:

'''    
        kwargs2 = self._parameters(locals())

        del kwargs2['default']

        key = self.key(**kwargs2)
        if key is None:
            return default

        return list(self.Items.axes(key=key))
    #--- End: def

    def items_axes(self, description=None, role=None, axes=None,
                   axes_all=None, axes_subset=None, axes_superset=None,
                   exact=False, inverse=False, match_and=True,
                   ndim=None):
        '''Return the axes of items of the field.

An item is a dimension coordinate, an auxiliary coordinate, a cell
measure or a coordinate reference object.   .......................................

.. seealso:: `axes`, `data_axes`, `item`

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

:Returns:

    out: `dict`
        
:Examples:

'''    
        kwargs2 = self._parameters(locals())
        
        out = {}
        for key in self.items(**kwargs2):
            out[key] = self.Items.axes(key=key)

        return out
    #--- End: def

    def items(self, description=None, role=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, ndim=None,
              match_and=True, exact=False, inverse=False, copy=False):
#              _restrict_inverse=False):
        '''Return items of the field.

{+item_definition}

{+item_selection}

The output is a dictionary whose key/value pairs are item identifiers
with corresponding values of items of the field. If no items are found
then the dictionary will be empty.

{+items_criteria}

To find a unique item, use the `item` method.

.. seealso:: `auxs`, `axes`, `measures`, `coords`, `dims`, `item`, `match`
             `remove_items`, `refs`

:Examples 1:

Select all items whose identities (as returned by their `!identity`
methods) start "height":

>>> f.{+name}('height')

Select all items which span only one axis:

>>> f.items(ndim=1)

Select all cell measure objects:

>>> f.items(role='m')

Select all items which span the "time" axis:

>>> f.items(axes='time')

Select all CF latitude coordinate objects:

>>> f.items('Y')

Select all multidimensional dimension and auxiliary coordinate objects
which span at least the "time" and/or "height" axes and whose long
names contain the string "qwerty":

>>> f.items('long_name:.*qwerty', 
...         role='da',
...         axes=['time', 'height'],
...         ndim=cf.ge(2))

:Parameters:

    {+description}

          *Example:* 

            >>> x = f.items(['aux1',
            ...             'time',
            ...             {'units': 'degreeN', 'long_name': 'foo'}])
            >>> y = {}
            >>> for items in ['aux1', 'time', {'units': 'degreeN', 'long_name': 'foo'}]:
            ...     y.update(f.items(items))
            ...
            >>> set(x) == set(y)
            True

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

          *Example:*
            ``f.items(role='da', inverse=True)`` selects the same
            items as ``f.items(role='mr')``.

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of items. The dictionary may be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())

        # Parse the various axes options
        if axes is not None:
            if not isinstance(axes, dict):
                axes = {'axes': axes}

            kwargs2['axes'] = set(self.axes(**axes))

        if axes_subset is not None:
            if not isinstance(axes_subset, dict):
                axes_subset = {'axes': axes_subset}

            kwargs2['axes_subset'] = set(self.axes(**axes_subset))

        if axes_superset is not None:
            if not isinstance(axes_superset, dict):
                axes_superset = {'axes': axes_superset}

            kwargs2['axes_superset'] = set(self.axes(**axes_superset))

        if axes_all is not None:
            if not isinstance(axes_all, dict):
                axes_all = {'axes': axes_all}

            kwargs2['axes_all'] = set(self.axes(**axes_all))

        # By default, omit coordinate reference items.
        if role is None:
            kwargs2['role'] = ('d', 'a', 'm', 'c', 'f')

        return self.Items(**kwargs2)
    #--- End: def
 
    def period(self, axes=None, **kwargs):
        '''Return the period of an axis.

Note that a non-cyclic axis may have a defined period.

.. versionadded:: 1.0

.. seealso:: `axis`, `cyclic`, `iscyclic`,
             `cf.DimensionCoordinate.period`

:Parameters:

    {+axes, kwargs}

:Returns:

    out: `cf.Data` or `None`
        The period of the cyclic axis's dimension coordinates, or
        `None` no period has been set.

:Examples 2:

>>> f.cyclic()
{}
>>> print f.period('X')
None
>>> f.dim('X').Units
<CF Units: degrees_east>
>>> f.cyclic('X', period=360)
{}
>>> print f.period('X')
<CF Data: 360.0 'degrees_east'>
>>> f.cyclic('X', False)
{'dim3'}
>>> print f.period('X')
<CF Data: 360.0 'degrees_east'>
>>> f.dim('X').period(None)
<CF Data: 360.0 'degrees_east'>
>>> print f.period('X')
None

        '''
        axis = self.axis(axes=axes, key=True, **kwargs)
        if axis is None:
            raise ValueError("Can't identify axis")

        dim = self.dim(axis)
        if dim is None:
            return
            
        return dim.period()       
    #--- End: def

    def remove_item(self, description=None, role=None, axes=None,
                    axes_all=None, axes_subset=None,
                    axes_superset=None, ndim=None, exact=False,
                    inverse=False, match_and=True, key=False):
        '''Remove and return an item from the field.

{+item_definition}

By default all items of the domain are removed, but particular items
may be selected with the keyword arguments.

{+item_selection}

.. seealso:: `items`, `remove_axes`, `remove_axis`, `remove_item`

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

:Returns:

    out: 
        A dictionary whose keys are domain item identifiers with
        corresponding values of the removed items. The dictionary may
        be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())

#        kwargs2['items'] = kwargs2.pop('item')

        del kwargs2['key']

        # Include coordinate references by default
        if kwargs2['role'] is None:
            kwargs2['role'] = ('d', 'a', 'm', 'c', 'f', 'r')

        items = self.items(**kwargs2)
        if len(items) == 1:
            out = self.remove_items(**kwargs2)
            if key:
                return out.popitem()[0]
            return out.popitem()[1]
            
        if not len(items):
            raise ValueError(
"Can't remove non-existent item defined by parameters {0}".format(kwargs2))
        else:
            raise ValueError(
"Can't remove non-unique item defined by parameters {0}".format(kwargs2))
    #--- End: def

    def remove_items(self, description=None, role=None, axes=None,
                     axes_all=None, axes_subset=None,
                     axes_superset=None, ndim=None, exact=False,
                     inverse=False, match_and=True):
        '''Remove and return items from the field.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object.

By default all items of the domain are removed, but particular items
may be selected with the keyword arguments.

.. seealso:: `items`, `remove_axes`, `remove_axis`, `remove_item`

:Parameters:

    {+description}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of the removed items. The dictionary may
        be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())

        # Include coordinate references by default
        if kwargs2['role'] is None:
            kwargs2['role'] = ('d', 'a', 'm', 'c', 'f', 'r')

        Items = self.Items
        role  = Items.role

        items = self.items(**kwargs2)

        out = {}
 
        for key, item in items.items():
            if role(key) == 'r':
                ref = Items.remove_item(key)
                out[key ] = self._unconform_ref(ref)
                del items[key]
                
        for key, item in items.iteritems():
            item_role = role(key)

            if item_role in 'dac':
                # The removed item is a dimension coordinate,
                # auxiliary coordinate or domain ancillary, so replace
                # its identifier in any coordinate references with its
                # identity.
                identity_map = {key: item.identity()}
                for ref in self.Items.refs().itervalues():
                    ref.change_identifiers(identity_map,
                                           coordinate=(item_role!='c'),
                                           ancillary=(item_role=='c'),
                                           i=True)
            #--- End: if
                
            out[key] = Items.remove_item(key)        
        #--- End: if        
                                                      
        return out
    #--- End: def

    def remove_axes(self, axes=None, size=None, **kwargs):
        '''

Remove and return axes from the field.

By default all axes of the domain are removed, but particular axes may
be selected with the keyword arguments.

The axis may be selected with the keyword arguments. If no unique axis
can be found then no axis is removed and `None` is returned.

If an axis has size greater than 1 then it is not possible to remove
it if it is spanned by the field's data array or any multidimensional
coordinate or cell measure object of the field.

.. seealso:: `axes`, `remove_axis`, `remove_item`, `remove_items`

:Parameters:

    {+axes, kwargs}

    {+size}

:Returns:

    out: `dict`
        The removed axes. The dictionary may be empty.

:Examples:

'''
        axes = self.axes(axes, size=size, **kwargs)
        if not axes:
            return axes

        axes = set(axes)

        size1_data_axes = []
        domain_axes = self.axes()
        if self.data_axes() is not None:
            for axis in axes.intersection(domain_axes).intersection(self.data_axes()):
                if domain_axes[axis] == 1:
                    size1_data_axes.append(axis)
                else:
                    raise ValueError(
"Can't remove an axis with size > 1 which is spanned by the data array")
        #---End: if

        for axis in axes:
            if (domain_axes[axis] > 1 and
                self.items(ndim=gt(1), axes=axis)):
                raise ValueError(
"Can't remove an axis with size > 1 which is spanned by a multidimensional item")
        #--- End: for

        # Replace the axis in cell methods with a standard name, if
        # possible.
        cms = self.CellMethods
        if cms:            
            axis_map = {}
            del_axes = []
            for axis in axes:
                coord = self.item(role=('d',), axes=axis)
                standard_name = getattr(coord, 'standard_name', None)
                if standard_name is None:
                    coord = self.item(role=('a',), ndim=1, axes_all=axis)
                    standard_name = getattr(coord, 'standard_name', None)
                if standard_name is not None:
                    axis_map[axis] = standard_name
                else:
                    del_axes.append(axis)
        #--- End: if

        # Remove coordinate references which span any of the removed axes
        for key in self.items(role='r'):
            if axes.intersection(self.Items.axes(key)):
                self.Items.remove_item(key)

        for key, item in self.items(axes=axes).iteritems():
            item_axes = self.item_axes(key)

            # Remove the item if it spans only removed axes
            if axes.issuperset(item_axes):
                self.Items.remove_item(key)
                continue            

            # Still here? Then squeeze removed axes from the item,
            # which must be multidimensional and have size 1 along the
            # axes to be removed.
            iaxes = [item_axes.index(axis) for axis in axes
                     if axis in item_axes]
            item.squeeze(iaxes, i=True)

            # Remove the removed axes from the multidimensional item's
            # list of axes
            for axis in axes.intersection(item_axes):
                item_axes.remove(axis)

            self.Items.axes(key, axes=item_axes)
        #--- End: for

        if size1_data_axes:
            self.squeeze(size1_data_axes, i=True)
            
        # Replace the axis in cell methods with a standard name, if
        # possible.
        if cms:
            self.CellMethods.change_axes(axis_map, i=True)
            self.CellMethods.remove_axes(del_axes)

        # Remove the axes
        for axis in axes:
            del self._Axes[axis]

        # Remove axes from unlimited dictionary
        unlimited = self._unlimited
        if unlimited:
            for axis in axes:
                unlimited.pop(axis, None)
            if not unlimited:
                self._unlimited = None

        return axes
    #--- End: def

    def remove_axis(self, axes=None, size=None, **kwargs):
        '''

Remove and return a unique axis from the field.

The axis may be selected with the keyword arguments. If no unique axis
can be found then no axis is removed and `None` is returned.

If the axis has size greater than 1 then it is not possible to remove
it if it is spanned by the field's data array or any multidimensional
coordinate or cell measure object of the field.

.. seealso:: `axis`, `remove_axes`, `remove_item`, `remove_items`

:Parameters:

    {+axes, kwargs}

    {+size}

:Returns:

    out: `str`
        The identifier of the removed axis, or `None` if there
        isn't one.

:Examples:

'''      
        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:
            return

        return self.remove_axes(axis).pop()
    #--- End: def

    def roll(self, axes, shift, i=False, **kwargs):
        '''Roll the field along a cyclic axis.

A unique axis is selected with the axes and kwargs parameters.

.. versionadded:: 1.0

.. seealso:: `anchor`, `axis`, `cyclic`, `iscyclic`, `period`

:Parameters:

    {+axes, kwargs}

    shift: `int`
        The number of places by which the selected cyclic axis is to
        be rolled.

    {+i}

:Returns:

    out: `cf.{+Variable}`
        The rolled field.

:Examples:

        '''          
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('roll', kwargs2)
#
        axis = self.axis(axes, key=True, **kwargs)
        if axis is None:
            raise ValueError("Can't roll: Bad axis specification")

        if i:
            f = self
        else:
            f = self.copy()
        
        if self.axis_size(axis) <= 1:
            return f
        
        dim = self.item(axis)
        if dim is not None and dim.period() is None:
            raise ValueError(
"Can't roll: {!r} axis has non-periodic dimension coordinates".format(
    dim.name()))

        try:
            iaxis = self.data_axes().index(axis)
        except ValueError:
            return f

        f = super(Field, f).roll(iaxis, shift, i=True)

        for key, item in f.items(role=('d', 'a', 'm', 'c', 'f')).iteritems():
            axes = f.item_axes(key)
            if axis in axes:
                item.roll(axes.index(axis), shift, i=True)
        #--- End: for

        return f
    #--- End: def

    def where(self, condition, x=None, y=None, i=False, item=None, **item_options):
        '''Set data array elements depending on a condition.

Elements are set differently depending on where the condition is True
or False. Two assignment values are given. From one of them, the
field's data array is set where the condition is True and where the
condition is False, the data array is set from the other.

Each assignment value may either contain a single datum, or is an
array-like object which is broadcastable shape of the field's data
array.

**Missing data**

The treatment of missing data elements depends on the value of field's
`hardmask` attribute. If it is True then masked elements will not
unmasked, otherwise masked elements may be set to any value.

In either case, unmasked elements may be set to any value (including
missing data).

Unmasked elements may be set to missing data by assignment to the
`cf.masked` constant or by assignment to a value which contains masked
elements.

.. seealso:: `cf.masked`, `hardmask`, `indices`, `mask`, `subspace`

:Examples 1:

>>> 

:Parameters:

    condition: 
        The condition which determines how to set the data array. The
        *condition* parameter may be one of:

          * Any object which is broadcastable to the field's shape
            using the metadata-aware `cf` broadcasting rules (i.e. a
            suitable `cf.Field` object or any object, ``a``, for which
            ``numpy.size(a)`` is 1). The condition is True where the
            object broadcast to the field's data array evaluates to
            True.

              *Example:*                
                To set all data array values of 10 to -999:
                ``f.where(10, -999)``.

              *Example:*
                To set all data array values of 100 metres to -999
                metres: ``f.where(cf.Data(100, 'm'), -999)``.

              *Example:*
                To set all data array values to -999 where another
                field, ``g`` (which is broadcastable to ``f``),
                evaluates to true: ``f.where(g, -999)``.

        ..

          * A `cf.Query` object which is evaluated against the field
            and the resulting field of booleans (which will always
            have the same shape as the original field) defines the
            condition.
   
              *Example:*
                ``f.where(cf.lt(0), -999)`` will set all data array
                values less than zero to -999. This will often be
                equivalent to ``f.where(f==cf.lt(0), -999)``, but the
                latter will fail if the field ``f`` has insufficient
                domain metadata whilst the former will always work.

        If *item* or *item_options* are set then the condition must be
        a `cf.Query` object and is evaluated against the selected
        item's data array (such as one containing coordinates). The
        field's data array is set to *x* or *y* according to where in
        the domain the item's data satisfies the condition.

          *Example:*
            ``f.where(cf.wi(-30, 30), cf.masked, -99,
            item='latitude')`` will set all data array values within
            the tropics to missing data and at all other locations
            will be set to -99.

    x, y: *optional*
        Specify the assignment values. Where the condition evaluates
        to True, set the field's data array from *x* and where the
        condition evaluates to False, set the field's data array from
        *y*. The *x* and *y* parameters are each one of:

          * `None`. The appropriate elements of the field's data
            array are unchanged. This the default.
        ..

          * Any object which is broadcastable to the field's data
            array using the metadata-aware `cf` broadcasting rules
            (i.e. a suitable `cf.Field` object or any object, ``a``,
            for which ``numpy.size(a)`` is 1). The appropriate
            elements of the field's data array are set to the
            corresponding values from the object broadcast to the
            field's data array shape.

    item, **item_options: optional
        If *item* and/or *item_options* are set then the *condition*
        is evaluated against a particular item of the field (such as
        one containing coordinates) and field's data array is set to
        *x* or *y* according to where in the domain the item's data
        satisfies the condition. The condition must be a `cf.Query`
        object.

        *item* may be any value accepted by the *description*
        parameter of the field's `item` method. The selected item is
        the one that would be returned by this call of the field's
        `item` method: ``f.item(item, **item_options)``. See
        `cf.Field.item` for details.

          *Example:*
            ``f.where(cf.wi(-30, 30), cf.masked, -99,
            item='latitude')`` will set all data array values within
            the tropics to missing data and at all other locations
            will be set to -99.

          *Example:*
            ``f.where(cf.dt('2000-1-1'), 0, item'T', ndim=1)`` will
            set all data array values to zero where the uniques 1-d
            time coordinates are 2000-1-1.

          *Example:*
            ``f.where(cf.lt(2500, 'km2'), cf.masked, role='m')`` will
            mask all data values for grid cells with a cell area of
            less than 2500 km2 (assuming that there is a unique cell
            measure object in the field).

    {+i}

:Returns:

    out: `cf.{+Variable}`
        The field with updated data array.

:Examples 2:

Set data array values to 15 everywhere:

>>> f.where(True, 15)

This example could also be done with subspace assignment:

>>> f[...] = 15

Set all negative data array values to zero and leave all other
elements unchanged:

>>> g = f.where(f<0, 0)

Multiply all positive data array elements by -1 and set other data
array elements to 3.14:

>>> g = f.where(f>0, -f, 3.14)

Set all values less than 280 and greater than 290 to missing data:

>>> g = f.where((f < 280) | (f > 290), cf.masked)

This example could also be done with a `cf.Query` object:

>>> g = f.where(cf.wo(280, 290), cf.masked)

or equivalently:

>>> g = f.where(f==cf.wo(280, 290), cf.masked)

Set data array elements in the northern hemisphere to missing data
in-place:

>>> condition = f.domain_mask(latitude=cf.ge(0))
>>> f.where(condition, cf.masked, i=True)

This in-place example could also be done with subspace assignment by
indices:

>>> northern_hemisphere = f.indices(latitude=cf.ge(0))
>>> f.subspace[northern_hemisphere] = cf.masked

Set a polar rows to their zonal-mean values:

>>> condition = f.domain_mask(latitude=cf.set([-90, 90]))
>>> g = f.where(condition, f.collapse('longitude: mean'))

        '''
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())            
#            return self._list_method('where', kwargs2)
 
        if i:
            f = self
        else:
            f = self.copy()

        if x is None and y is None:
            return f

        self_class = f.__class__

        if isinstance(condition, self_class):
            # --------------------------------------------------------
            # Condition is another cf.Field object
            # --------------------------------------------------------
            condition = f._conform_for_assignment(condition)

        elif item is not None or item_options:
            if not isinstance(condition, Query):
                raise ValueError(
"Can only only apply a Query condition to an item of the field")
            
            # Apply the Query to an item of the field, making sure
            # that the item's data is broadcastable to the field's
            # data.
            g = f.transpose(f.data_axes(), items=True)
                
            kwargs2 = item_options.copy()
            kwargs2['description'] = item
            
            key, item = g.key_item(**kwargs2)
            if key is None:
                raise ValueError(
"No unique item could be found from {}".format(kwargs2))

            item_axes = g.item_axes(key)
            data_axes = g.data_axes()
            
            if item_axes != data_axes:
                s = [i for i, axis in enumerate(item_axes) if axis not in data_axes]
                if s:
                    item = item.squeeze(s)
                    item_axes = [axis for axis in item_axes if axis not in data_axes]

                for i, axis in enumerate(data_axes):
                    if axis not in item_axes:
                        item = item.expand_dims(i)
            #--- End: if
                
#            if isinstance(condition, Query):
            condition = condition.evaluate(item).Data
 #           else:
 #               print 'ARSE', condition
 #               condition = (condition == item)
 #               print condition
#
#
#            
#        else: #if isinstance(condition, Query):
#            # --------------------------------------------------------
#            # Condition is another cf.Query object
#            # --------------------------------------------------------            
#            if item is None and not item_options:
#                # Apply the Query to the field's data
#                condition = condition.evaluate(f).Data
##                item = f.Data
#            else:
#                # Apply the Query to an item of the field, making sure
#                # that the item's data is broadcastable to the field's
#                # data.
#                g = f.transpose(f.data_axes(), items=True)
#                
#                kwargs2 = item_options.copy()
#                kwargs2['description'] = item
#
#                key, item = g.key_item(**kwargs2)
#                if key is None:
#                    raise ValueError(
#"No unique item could be found from {}".format(kwargs2))
#
#                item_axes = g.item_axes(key)
#                data_axes = g.data_axes()
#
#                if item_axes != data_axes:
#                    s = [i for i, axis in enumerate(item_axes) if axis not in data_axes]
#                    if s:
#                        item = item.squeeze(s)
#                        item_axes = [axis for axis in item_axes if axis not in data_axes]
#
#                    for i, axis in enumerate(data_axes):
#                        if axis not in item_axes:
#                            item = item.expand_dims(i)
#            #--- End: if
#                
#            if isinstance(condition, Query):
#                condition = condition.evaluate(item).Data
#            else:
#                print 'ARSE', condition
#                condition = (condition == item)
#                print condition
        elif isinstance(condition, Query):
            condition = condition.evaluate(f).Data
        #--- End: if

        if x is not None and isinstance(x, self_class):
            x = f._conform_for_assignment(x)
               
        if y is not None and isinstance(y, self_class):
            y = f._conform_for_assignment(y)

        return super(Field, f).where(condition, x, y, i=True)
    #--- End: def

    @property
    def subspace(self):
        '''Create a subspace of the field.

A subspace may be defined in "metadata-space" via data array values of
its domain items: dimension coordinate, auxiliary coordinate, cell
measure, domain ancillary and field ancillary objects.

Alternatively, a subspace my be defined be in "index-space" via
explicit indices for the data array using an extended Python slicing
syntax.

**Defining a subspace in metadata-space**

Defining a subspace in metadata-space has the following features

* Axes to be subspaced may identified by metadata, rather than their
  position in the data array.


* The position in the data array of each axis need not be known and
  the axes to be subspaced may be given in any order.

* Axes for which no subspacing is required need not be specified.

* Size one axes of the domain which are not spanned by the data
  array may be specified.

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>
>>> f.subspace(latitude=0)
<CF Field: air_temperature(time(12), latitude(1), longitude(96)) K>
>>> f.subspace(longitude=cf.ge(180), latitude=0)
<CF Field: air_temperature(time(12), latitude(1), longitude(48)) K>
>>> f.subspace(longitude=cf.ge(180), latitude=0, time=cf.month(cf.lt(8)))
<CF Field: air_temperature(time(7), latitude(1), longitude(48)) K>

* The field may be subspaced according to conditions on
  multidimensional items.

>>> print f
eastward_wind field summary
---------------------------
Data           : eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1
Cell methods   : time: mean
Axes           : time(3) = [1979-05-01T12:00:00Z, ..., 1979-05-03T12:00:00Z] gregorian
               : air_pressure(5) = [850.0, ..., 50.0] hPa
               : grid_latitude(110) = [23.32, ..., -24.64] degrees
               : grid_longitude(106) = [-20.54, ..., 25.66] degrees
Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_north
               : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_east
Coord refs     : rotated_latitude_longitude
>>> f.subspace(latitude=cf.gt(60))
<CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(35), grid_longitude(106)) m s-1>
>>> f.subspace(longitude=cf.wi(-30, 30), latitude=cf.gt(60))
<CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(35), grid_longitude(66)) m s-1>

* Three types of subspace are available:
    
  * A "compress" subspace (the default) is the smallest possible
    subspace which contains the selected elements. As many
    non-selected elements are discarded as possible, meaning that the
    subspace may not form a contiguous bloack of te original field.

  * An "envelope" subspace is the smallest subspace which contains the
    selected elements and forms a contiguous block of the original
    field. Interior, non-selected elements are set to missing data
    values.

  * A "full" subspace is is the same size as the original field, but
    with all non-selected elements set to missing data values.

  >>> f
  <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>
  >>> f.subspace(grid_longitude=cf.wi(-10, -5) | cf.wi(5, 10))
  <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(23)) m s-1>
  >>> f.subspace('compress', grid_longitude=cf.wi(-10, -5) | cf.wi(5, 10))
  <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(23)) m s-1>
  
  >>> f.subspace('envelope', grid_longitude=cf.wi(-10, -5) | cf.wi(5, 10))
  <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(46)) m s-1>
  
  >>> f.subspace('full', grid_longitude=cf.wi(-10, -5) | cf.wi(5, 10))
  <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>

  This is also works for subspaces defined by multidimensional
  curvilinear, or unstructured coordinates:

  >>> print f.subspace('envelope', longitude=cf.wi(-10, 30))
  eastward_wind field summary
  ---------------------------
  Data           : eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(91)) m s-1
  Cell methods   : time: mean
  Axes           : time(3) = [1979-05-01T12:00:00Z, ..., 1979-05-03T12:00:00Z] gregorian
                 : air_pressure(5) = [850.000061035, ..., 50.0000038147] hPa
                 : grid_latitude(110) = [23.3200002313, ..., -24.6399995089] degrees
                 : grid_longitude(91) = [-19.6600109935, ..., 19.9399887919] degrees
  Aux coords     : latitude(grid_latitude(110), grid_longitude(91)) = [[67.6943495635, ..., 24.6226629697]] degrees_north
                 : longitude(grid_latitude(110), grid_longitude(91)) = [[-44.4891982306, ..., 29.9371053319]] degrees_east
  Coord refs     : rotated_latitude_longitude


**Defining a subspace in index-space**

Subspacing in index-space uses an extended Python slicing syntax,
which is similar to :ref:`numpy array indexing
<numpy:arrays.indexing>`. Extensions to the numpy indexing
functionality are:

* The indices for each axis work independently. When more than one
  axis's slice is a 1-d boolean sequence or 1-d sequence of integers,
  then these indices work independently along each axis (similar to
  the way vector subscripts work in Fortran), rather than by their
  elements.

* Boolean indices may be any object which exposes the numpy array
  interface, such as the field's coordinate objects.

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>
>>> f.subspace[:, [0, 72], [5, 4, 3]]
<CF Field: air_temperature(time(12), latitude(2), longitude(3)) K>
>>> f.subspace[:, f.coord('latitude')<0]
<CF Field: air_temperature(time(12), latitude(36), longitude(96)) K>

**Size one axes**

Size one axes in the subspaced field are always retained, but may be
subsequently removed with the field's `~cf.Field.squeeze` method:

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>
>>> f.subspace(latitude=0)
<CF Field: air_temperature(time(12), latitude(1), longitude(96)) K>
>>> f.subspace(latitude=0).squeeze()
<CF Field: air_temperature(time(12), longitude(96)) K>

>>> f.subspace[..., 12:13]
<CF Field: air_temperature(time(12), latitude(73), longitude(1)) K>
>>> f.subspace[..., -1].squeeze(2)
<CF Field: air_temperature(time(12), latitude(73)) K>

**Assignment to the data array**

A subspace defined in index-space may have its data array values
changed by simple assignment:

>>> f
<CF Field: air_temperature(time(12), latitude(73), longitude(96)) K>
>>> f.subspace[0:6] = f.subspace[6:12]
>>> f.subspace[..., 0:48] = -99

To assign to a subspace defined in metadata-space, the equivalent
index-space indices must first be found with the field's `indices`
method, and then the assignment may be applied in index-space:

>>> index = f.indices(longitude=cf.lt(180))
>>> f.subspace[index] = cf.masked

This example could have been carried out in index-space if the
longitude coordinates were 1-d and their position in the data array
was known:

>>> f.subspace[:, :, f.coord('longitude')<180] = cf.masked

However, if the longitude coordinates were multidimensional then only
the `indices` approach would have been possible.

.. seealso:: `__getitem__`, `indices`, `where`

:Examples:

>>> f,shape
(12, 73, 96)
>>> f.subspace().shape
(12, 73, 96)
>>> f.subspace(latitude=0).shape
(12, 1, 96)
>>> f.subspace(latitude=cf.wi(-30, 30)).shape
(12, 25, 96)
>>> f.subspace(long=cf.ge(270, 'degrees_east'), lat=cf.set([0, 2.5, 10])).shape
(12, 3, 24)
>>> f.subspace(latitude=cf.lt(0, 'degrees_north'))
(12, 36, 96)
>>> f.subspace(latitude=[cf.lt(0, 'degrees_north'), 90])
(12, 37, 96)
>>> import math
>>> f.subspace('exact', longitude=cf.lt(math.pi, 'radian'), height=2)
(12, 73, 48)
>>> f.subspace(height=cf.gt(3))
IndexError: No indices found for 'height' values gt 3
>>> f.subspace(dim2=3.75).shape
(12, 1, 96)
>>> f.subspace(time=cf.le(cf.dt('1860-06-16 12:00:00')).shape
(6, 73, 96)
>>> f.subspace(time=cf.gt(cf.dt(1860, 7)),shape
(5, 73, 96)

Note that if a comparison function (such as `cf.wi`) does not specify
any units, then the units of the named item are assumed.

        '''
        return SubspaceField(self)
    #--- End: def

    def section(self, axes=None, stop=None, **kwargs):
        '''Return a FieldList of m dimensional sections of a Field of n
dimensions, where M <= N.

:Parameters:

    axes: *optional*
        A query for the m axes that define the sections of the Field
        as accepted by the Field object's axes method. The keyword
        arguments are also passed to this method. See cf.Field.axes
        for details. If an axis is returned that is not a data axis it
        is ignored, since it is assumed to be a dimension coordinate
        of size 1.

    stop: `int`, optional
        Stop after taking this number of sections and return. If stop
        is None all sections are taken.

:Returns:

    out: `cf.FieldList`
        The M dimensional sections of the Field.

:Examples:

Section a field into 2D longitude/time slices, checking the
units:

>>> f.section({None: 'longitude', units: 'radians'},
...           {None: 'time',
...            'units': 'days since 2006-01-01 00:00:00'})

Section a field into 2D longitude/latitude slices, requiring
exact names:

>>> f.section(['latitude', 'longitude'], exact=True)

Section a field into 2D longitude/latitude slices, showing
the results:

>>> f
<CF Field: eastward_wind(model_level_number(6), latitude(145),
longitude(192)) m s-1>

>>> f.section(('X', 'Y'))
[<CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>]

        '''
        return FieldList(_section(self, axes, data=False, stop=stop, **kwargs))
    #--- End: def

    def regrids(self, dst, method=None, src_cyclic=None,
                dst_cyclic=None, use_src_mask=True, use_dst_mask=False,
                fracfield=False, src_axes=None, dst_axes=None, axis_order=None,
                ignore_degenerate=True, i=False,
                _compute_field_mass=None):
        '''Return the field regridded onto a new latitude-longitude grid.

Regridding, also called remapping or interpolation, is the process of
changing the grid underneath field data values while preserving the
qualities of the original data.

By default the the regridding is a first-order conservative
interpolation, but bilinear interpolation is available. The latter
method is particular useful for cases when the latitude and longitude
coordinate cell boundaries are not known nor inferrable. Higher order
patch recovery is available as an alternative to bilinear
interpolation.  This typically results in better approximations to
values and derivatives compared to the latter, but the weight matrix
can be larger than the bilinear matrix, which can be an issue when
regridding close to the memory limit on a machine. Nearest neighbour
interpolation is also available.

**Metadata**

The field's domain must have well defined X and Y axes with latitude
and longitude coordinate values, which may be stored as dimension
coordinate objects or two dimensional auxiliary coordinate objects. If
the latitude and longitude coordinates are two dimensional then the X
and Y axes must be defined by dimension coordinates if present or by
the netCDF dimensions. In the latter case the X and Y axes must be
specified using the *src_axes* or *dst_axes* keyword. The same is true
for the destination grid, if it provided as part of another field.

The cyclicity of the X axes of the source field and destination grid
is taken into account. If an X axis is in fact cyclic but is not
registered as such by its parent field (see `cf.Field.iscyclic`), then
the cyclicity may be set with the *src_cyclic* or *dst_cyclic*
parameters. In the case of two dimensional latitude and longitude
dimension coordinates without bounds it will be necessary to specify
*src_cyclic* or *dst_cyclic* manually if the field is global.

The output field's coordinate objects which span the X and/or Y axes
are replaced with those from the destination grid. Any fields
contained in coordinate reference objects will also be regridded, if
possible.

**Mask**

The data array mask of the field is automatically taken into account,
such that the regridded data array will be masked in regions where the
input data array is masked. By default the mask of the destination
grid is not taken into account. If the destination field data has
more than two dimensions then the mask, if used, is taken from the two
dimensionsal section of the data where the indices of all axes other
than X and Y are zero.

**Implementation**

The interpolation is carried by out using the `ESMF` package - a
Python interface to the Earth System Modeling Framework (ESMF)
regridding utility.

**Logging**

Whether ESMF logging is enabled or not is determined by
`cf.REGRID_LOGGING`. If it is logging takes place after every call. By
default logging is disabled.

**Latitude-Longitude Grid**

The canonical grid with independent latitude and longitude coordinates.

**Curvilinear Grids**

Grids in projection coordinate systems can be regridded as long as two
dimensional latitude and longitude coordinates are present.

**Rotated Pole Grids**

Rotated pole grids can be regridded as long as two dimensional
latitude and longitude coordinates are present. It may be necessary to
explicitly identify the grid latitude and grid longitude coordinates
as being the X and Y axes and specify the *src_cyclic* or *dst_cyclic*
keywords.

**Tripolar Grids**

Tripolar grids are logically rectangular and so may be able to be
regridded. If no dimension coordinates are present it will be
necessary to specify which netCDF dimensions are the X and Y axes
using the *src_axes* or *dst_axes* keywords. Connections across the
bipole fold are not currently supported, but are not be necessary in
some cases, for example if the points on either side are together
without a gap. It will also be necessary to specify *src_cyclic* or
*dst_cyclic* if the grid is global.

.. versionadded:: 1.0.4

:Examples 1:

Regrid field ``f`` conservatively onto a grid contained in field
``g``:

>>> h = f.{+name}(g, 'conservative')

:Parameters:

    dst: `cf.Field` or `dict`
        The field containing the new grid. If dst is a field list the
        first field in the list is used. Alternatively a dictionary
        can be passed containing the keywords 'longitude' and
        'latitude' with either two 1D dimension coordinates or two 2D
        auxiliary coordinates. In the 2D case both coordinates must
        have their axes in the same order and this must be specified
        by the keyword 'axes' as either ``('X', 'Y')`` or ``('Y',
        'X')``.

    method: `str`
        Specify the regridding method. The *method* parameter must be
        one of:

          ==================  ========================================
          *method*            Description
          ==================  ========================================
          ``'bilinear'``      Bilinear interpolation.

          ``'patch'``         Higher order patch recovery.

          ``'conservative'``  First-order conservative regridding will
                              be used (requires both of the fields to
                              have contiguous, non-overlapping
                              bounds).

          ``'nearest_stod'``  Nearest neighbor interpolation is used
                              where each destination point is mapped
                              to the closest source point

          ``'nearest_dtos'``  Nearest neighbor interpolation is used
                              where each source point is mapped to the
                              closest destination point. A given
                              destination point may receive input from
                              multiple source points, but no source
                              point will map to more than one
                              destination point.
          ==================  ========================================

    src_cyclic: `bool`, optional
        Specifies whether the longitude for the source grid is
        periodic or not. If None then, if possible, this is determined
        automatically otherwise it defaults to False.

    dst_cyclic: `bool`, optional
        Specifies whether the longitude for the destination grid is
        periodic of not. If None then, if possible, this is determined
        automatically otherwise it defaults to False.

    use_src_mask: `bool`, optional
        For all methods other than 'nearest_stod', this must be True
        as it does not make sense to set it to False. For the
        'nearest_stod' method if it is True then points in the result
        that are nearest to a masked source point are
        masked. Otherwise, if it is False, then these points are
        interpolated to the nearest unmasked source points.

    use_dst_mask: `bool`, optional
        By default the mask of the data on the destination grid is not
        taken into account when performing regridding. If this option
        is set to true then it is. If the destination field has more
        than two dimensions then the first 2D slice in index space is
        used for the mask e.g. for an field varying with (X, Y, Z, T)
        the mask is taken from the slice (X, Y, 0, 0).

    fracfield: `bool`, optional
        If the method of regridding is conservative the fraction of
        each destination grid cell involved in the regridding is
        returned instead of the regridded data if this is
        True. Otherwise this is ignored.

    src_axes: `dict`, optional
        A dictionary specifying the axes of the 2D latitude and
        longitude coordinates of the source field when no dimension
        coordinates are present. It must have keys 'X' and 'Y'.

    dst_axes: `dict`, optional
        A dictionary specifying the axes of the 2D latitude and
        longitude coordinates of the destination field when no
        dimension coordinates are present. It must have keys 'X' and
        'Y'.

    axis_order: sequence, optional
        A sequence of items specifying dimension coordinates as
        retrieved by the `dim` method. These determine the order
        in which to iterate over the other axes of the field when
        regridding X-Y slices. The slowest moving axis will be the
        first one specified. Currently the regridding weights are
        recalculated every time the mask of an X-Y slice changes
        with respect to the previous one, so this option allows
        the user to minimise how frequently the mask changes.
    
    ignore_degenerate: `bool`, optional
        True by default. Instructs ESMPy to ignore degenerate cells
        when checking the grids for errors. Regridding will proceed
        and degenerate cells will be skipped, not producing a result,
        when set to True. Otherwise an error will be produced if
        degenerate cells are found. This will be present in the ESMPy
        log files if `cf.REGRID_LOGGING` is set to True. As of ESMF
        7.0.0 this only applies to conservative regridding.  Other
        methods always skip degenerate cells.

    {+i}
    
    _compute_field_mass: `dict`, optional
        If this is a dictionary then the field masses of the source
        and destination fields are computed and returned within the
        dictionary. The keys of the dictionary indicates the lat/long
        slice of the field and the corresponding value is a tuple
        containing the source field's mass and the destination field's
        mass. The calculation is only done if conservative regridding
        is being performed. This is for debugging purposes.

:Returns:

    out: `cf.{+Variable}`
        The regridded {+variable}.

:Examples 2:

Regrid f to the grid of g using bilinear regridding and forcing the
source field f to be treated as cyclic.

>>> h = f.regrids(g, src_cyclic=True, method='bilinear')

Regrid f to the grid of g using the mask of g.

>>> h = f.regrids(g, 'conservative', use_dst_mask=True)

Regrid f to 2D auxiliary coordinates lat and lon, which have their
dimensions ordered 'Y' first then 'X'.

>>> lat
<CF AuxiliaryCoordinate: latitude(110, 106) degrees_north>
>>> lon
<CF AuxiliaryCoordinate: longitude(110, 106) degrees_east>
>>> h = f.regrids({'longitude': lon, 'latitude': lat, 'axes': ('Y', 'X')}, 'conservative')

Regrid field, f, on tripolar grid to latitude-longitude grid of field,
g.

>>> h = f.regrids(g, 'bilinear, src_axes={'X': 'ncdim%x', 'Y': 'ncdim%y'},
...               src_cyclic=True)

Regrid f to the grid of g iterating over the 'Z' axis last and the 'T'
axis next to last to minimise the number of times the mask is changed.

>>> h = f.regrids(g, 'nearest_dtos', axis_order='ZT')

        '''
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('regrids', kwargs2)

        # Initialise ESMPy for regridding if found
        manager = Regrid.initialize()
        
        # If dst is a dictionary set flag
        if isinstance(dst, self.__class__):
            dst_dict = False
            # If dst is a field list use the first field
            if isinstance(dst, FieldList):
                dst = dst[0]
        else:
            dst_dict = True
        
        # Retrieve the source field's latitude and longitude coordinates
        src_axis_keys, src_axis_sizes, src_coord_keys, src_coords, \
            src_coords_2D = self._regrid_get_latlong('source', axes=src_axes)
        
        # Retrieve the destination field's latitude and longitude coordinates
        if dst_dict:
            try:
                dst_coords = (dst['longitude'], dst['latitude'])
            except KeyError:
                raise ValueError("Keys 'longitude' and 'latitude' must be" +
                                 " specified for destination.")
            #--- End: if
            if dst_coords[0].ndim == 1:
                dst_coords_2D = False
                dst_axis_sizes = [coord.size for coord in dst_coords]
            elif dst_coords[0].ndim == 2:
                try:
                    dst_axes = dst['axes']
                except KeyError:
                    raise ValueError("Key 'axes' must be specified for 2D" +
                                     " latitude/longitude coordinates.")
                dst_coords_2D = True
                if dst_axes == ('X', 'Y'):
                    dst_axis_sizes = dst_coords[0].shape
                elif dst_axes == ('Y', 'X'):
                    dst_axis_sizes = dst_coords[0].shape[::-1]
                else:
                    raise ValueError("Keyword 'axes' must either be " +
                                     "('X', 'Y') or ('Y', 'X').")
                if dst_coords[0].shape != dst_coords[1].shape:
                    raise ValueError('Longitude and latitude coordinates for ' +
                                     'destination must have the same shape.')
            else:
                raise ValueError('Longitude and latitude coordinates for ' +
                                 'destination must have 1 or 2 dimensions.')
            #--- End: if
            dst_axis_keys = None
        else:
            dst_axis_keys, dst_axis_sizes, dst_coord_keys, dst_coords, \
                dst_coords_2D = dst._regrid_get_latlong('destination',
                                                        axes=dst_axes)
        #--- End: if
        
        # Automatically detect the cyclicity of the source longitude if
        # src_cyclic is None
        if src_cyclic is None:
            src_cyclic = self.iscyclic(src_axis_keys[0])
        #--- End: if
        # Automatically detect the cyclicity of the destination longitude if
        # dst is not a dictionary and dst_cyclic is None
        if not dst_dict and dst_cyclic is None:
            dst_cyclic = dst.iscyclic(dst_axis_keys[0])
        #--- End: if
        
        # Get the axis indices and their order for the source field
        src_axis_indices, src_order, self = \
                            self._regrid_get_axis_indices(src_axis_keys, i=i)

        # Get the axis indices and their order for the destination field.
        if not dst_dict:
            dst_axis_indices, dst_order, dst = \
                            dst._regrid_get_axis_indices(dst_axis_keys, i=i)
        #--- End: if
        
        # Get the order of the X and Y axes for each 2D auxiliary coordinate.
        src_coord_order = None
        dst_coord_order = None
        if src_coords_2D:
            src_coord_order = self._regrid_get_coord_order(src_axis_keys,
                                                           src_coord_keys)
        #--- End: if
        if dst_coords_2D:
            if dst_dict:
                if dst_axes == ('X', 'Y'):
                    dst_coord_order = [[0, 1], [0, 1]]
                elif dst_axes == ('Y', 'X'):
                    dst_coord_order = [[1, 0], [1, 0]]
                else:
                    raise ValueError("Keyword 'axes' must either be " +
                                     "('X', 'Y') or ('Y', 'X').")
                #--- End: if
            else:
                dst_coord_order = dst._regrid_get_coord_order(dst_axis_keys,
                                                              dst_coord_keys)
            #--- End: if
        #--- End: if
        
        # Get the shape of each regridded section.
        shape = self._regrid_get_section_shape(dst_axis_sizes,
                                               src_axis_indices)

        # Check that method is valid
        if method is None:
            raise ValueError("Can't regrid: Must select a regridding method")
        #--- End: if

        if method not in ('conservative', 'patch', 'bilinear', 'nearest_stod',
                          'nearest_dtos'):
            raise ValueError("Can't regrid: Invalid method: {!r}".format(method))
        #--- End: if
        
        # Check that use_src_mask is True for all methods other than
        # nearest_stod
        if not use_src_mask and not method == 'nearest_stod':
            raise ValueError('It only makes sense for use_dst_mask to be ' +
                             'False when using the nearest_stod method.')
        #--- End: if

        type(self)._regrid_check_bounds(src_coords, dst_coords, method)
        
        # Slice the source data into 2D latitude/longitude sections getting a
        # list of reordered keys if required.
        section_keys, sections = self._regrid_get_reordered_sections(axis_order,
                                     src_axis_keys, src_axis_indices)
        
        # Bounds must be used if the regridding method is conservative.
        use_bounds = method == 'conservative'
        
        # Retrieve the destination field's mask if appropriate
        dst_mask = None 
        if not dst_dict and use_dst_mask and dst.Data.ismasked:
            dst_mask = dst._regrid_get_destination_mask(dst_order)
        
        # Retrieve the destination ESMPy grid and fields
        dstgrid = Regrid.create_grid(dst_coords, use_bounds, mask=dst_mask,
                                     cyclic=dst_cyclic, coords_2D=dst_coords_2D,
                                     coord_order=dst_coord_order)
        # dstfield will be reyused to receive the regridded source
        # data for each section, one after the other
        dstfield = Regrid.create_field(dstgrid, 'dstfield')
        dstfracfield = Regrid.create_field(dstgrid, 'dstfracfield')

        # Regrid each section
        old_mask = None
        unmasked_grid_created = False
        for k in section_keys:
            d = sections[k]  # d is a cf.Data object
            # Retrieve the source field's grid, create the ESMPy grid and a
            # handle to regridding.dst_dict
            src_data = d.squeeze().transpose(src_order).array
            if (not (method == 'nearest_stod' and use_src_mask)
                and numpy_ma_is_masked(src_data)):
                mask = src_data.mask
                if not numpy_array_equal(mask, old_mask):
                    # Release old memory
                    if old_mask is not None:
                        regridSrc2Dst.destroy()
                        srcfracfield.destroy()
                        srcfield.destroy()
                        srcgrid.destroy()
                    #--- End: if
                    # (Re)create the source ESMPy grid and fields
                    srcgrid = Regrid.create_grid(src_coords, use_bounds,
                                                 mask=mask, cyclic=src_cyclic,
                                                 coords_2D=src_coords_2D,
                                                 coord_order=src_coord_order)
                    srcfield = Regrid.create_field(srcgrid, 'srcfield')
                    srcfracfield = Regrid.create_field(srcgrid, 'srcfracfield')
                    # (Re)initialise the regridder
                    regridSrc2Dst = Regrid(srcfield, dstfield, srcfracfield,
                                           dstfracfield, method=method,
                                           ignore_degenerate=ignore_degenerate)
                    old_mask = mask
                #--- End: if
            else:
                # The source data for this section is either a) not
                # masked or b) has the same mask as the previous
                # section.
                if not unmasked_grid_created or old_mask is not None:
                    # Create the source ESMPy grid and fields
                    srcgrid = Regrid.create_grid(src_coords, use_bounds,
                                                 cyclic=src_cyclic,
                                                 coords_2D=src_coords_2D,
                                                 coord_order=src_coord_order)
                    srcfield = Regrid.create_field(srcgrid, 'srcfield')
                    srcfracfield = Regrid.create_field(srcgrid, 'srcfracfield')
                    # Initialise the regridder. This also creates the
                    # weights needed for the regridding.
                    regridSrc2Dst = Regrid(srcfield, dstfield, srcfracfield,
                                           dstfracfield, method=method,
                                           ignore_degenerate=ignore_degenerate)
                    unmasked_grid_created = True
                    old_mask = None
                #--- End: if
            #--- End: if
            
            # Fill the source and destination fields (the destination
            # field gets filled with a fill value, the source field
            # with the section's data)
            self._regrid_fill_fields(src_data, srcfield, dstfield)
            
            # Run regridding
            dstfield = regridSrc2Dst.run_regridding(srcfield, dstfield)

            # Compute field mass if requested for conservative regridding
            if _compute_field_mass is not None and method == 'conservative':
                # Update the _compute_field_mass dictionary in-place,
                # thereby making the field mass available after
                # returning
                self._regrid_compute_field_mass(_compute_field_mass,
                                                k, srcgrid, srcfield,
                                                srcfracfield, dstgrid,
                                                dstfield)
            #--- End: if
            
            # Get the regridded data or frac field as a numpy array
            regridded_data = self._regrid_get_regridded_data(method,
                                                             fracfield,
                                                             dstfield,
                                                             dstfracfield)
            
            # Insert regridded data, with axes in order of the
            # original section. This puts the regridded data back into
            # the sections dictionary, with the same key, as a new
            # Data object. Note that the reshape is necessary to
            # replace any size 1 dimensions that we squeezed out
            # earlier.
            sections[k] = \
                Data(regridded_data.transpose(src_order).reshape(shape),
                     units=self.Units)
        #--- End: for
        
        # Construct new data from regridded sdst_dictections
        new_data = Regrid.reconstruct_sectioned_data(sections)
        
        # Construct new field
        if i:
            f = self
        else:
            f = self.copy(_omit_Data=True)
        #--- End:if
        
        ## Update ancillary variables of new field
        #f._conform_ancillary_variables(src_axis_keys, keep_size_1=False)
        
        # Update coordinate references of new field
        f._regrid_update_coordinate_references(dst, src_axis_keys,
                                               method, use_dst_mask,
                                               i, src_cyclic=False,
                                               dst_cyclic=False)
        
        # Update coordinates of new field
        f._regrid_update_coordinates(dst, dst_dict, dst_coords,
                                     src_axis_keys, dst_axis_keys,
                                     dst_axis_sizes=dst_axis_sizes,
                                     dst_coords_2D=dst_coords_2D,
                                     dst_coord_order=dst_coord_order)
        
        # Copy across the destination fields coordinate references if necessary
        if not dst_dict:
            f._regrid_copy_coordinate_references(dst, dst_axis_keys)
        #--- End: if
        
        # Insert regridded data into new field
        f.insert_data(new_data, axes=self.data_axes())
        
        # Set the cyclicity of the destination longitude
        x = f.dim('X')
        if x is not None and x.Units.equivalent(Units('degrees')):
            f.cyclic('X', iscyclic=dst_cyclic, period=Data(360, 'Degrees'))
        
        # Release old memory from ESMF (this ought to happen garbage
        # collection, but it doesn't seem to work there!)
        regridSrc2Dst.destroy()
        dstfracfield.destroy()
        srcfracfield.destroy()
        dstfield.destroy()
        srcfield.destroy()
        dstgrid.destroy()
        srcgrid.destroy()
        
#        if f.data.fits_in_one_chunk_in_memory(f.data.dtype.itemsize):
#            f.varray

        return f
    #--- End: def

    def regridc(self, dst, axes, method=None, use_src_mask=True,
                use_dst_mask=False, fracfield=False, axis_order=None,
                ignore_degenerate=True, i=False, _compute_field_mass=None):
        '''Return the field with the specified Cartesian axes regridded onto a
new grid.

Between 1 and 3 dimensions may be regridded.

Regridding, also called remapping or interpolation, is the process of
changing the grid underneath field data values while preserving the
qualities of the original data.

By default the the regridding is a first-order conservative
interpolation, but bilinear interpolation is available. The latter
method is particular useful for cases when the latitude and longitude
coordinate cell boundaries are not known nor inferrable. Higher order
patch recovery is available as an alternative to bilinear
interpolation.  This typically results in better approximations to
values and derivatives compared to the latter, but the weight matrix
can be larger than the bilinear matrix, which can be an issue when
regridding close to the memory limit on a machine. It is only
available in 2D. Nearest neighbour interpolation is also available.

**Metadata**

The field's domain must have axes matching those specified in
*src_axes*. The same is true for the destination grid, if it provided
as part of another field. Optionally the axes to use from the
destination grid may be specified separately in *dst_axes*.

The output field's coordinate objects which span the specified axes
are replaced with those from the destination grid. Any fields
contained in coordinate reference objects will also be regridded, if
possible.

**Mask**

The data array mask of the field is automatically taken into account,
such that the regridded data array will be masked in regions where the
input data array is masked. By default the mask of the destination
grid is not taken into account. If the destination field data has
more dimensions than the number of axes specified then, if used, its
mask is taken from the 1-3 dimensional section of the data where the
indices of all axes other than X and Y are zero.

**Implementation**

The interpolation is carried by out using the `ESMF` package - a
Python interface to the Earth System Modeling Framework (ESMF)
regridding utility.

**Logging**

Whether ESMF logging is enabled or not is determined by
`cf.REGRID_LOGGING`. If it is logging takes place after every call. By
default logging is disabled.

:Examples 1:

Regrid the time axes of field ``f`` conservatively onto a grid
contained in field ``g``:

>>> h = f.{+name}(g, axes='T', 'conservative')

:Parameters:

    dst: `cf.Field` or `dict`
        The field containing the new grid or a dictionary with the
        axes specifiers as keys referencing dimension coordinates.
        If dst is a field list the first field in the list is used.

    axes:
        Select dimension coordinates from the source and destination
        fields for regridding. See `cf.Field.axes` for options for
        selecting specific axes. However, the number of axes returned
        by `cf.Field.axes` must be the same as the number of
        specifiers passed in.

    method: `str`
        Specify the regridding method. The *method* parameter must be
        one of:

          ==================  ========================================
          *method*            Description
          ==================  ========================================
          ``'bilinear'``      Multilinear interpolation.

          ``'patch'``         Higher order patch recovery.

          ``'conservative'``  First-order conservative regridding will
                              be used (requires both of the fields to
                              have contiguous, non-overlapping
                              bounds).

          ``'nearest_stod'``  Nearest neighbour interpolation is used
                              where each destination point is mapped
                              to the closest source point

          ``'nearest_dtos'``  Nearest neighbour interpolation is used
                              where each source point is mapped to the
                              closest destination point. A given
                              destination point may receive input from
                              multiple source points, but no source
                              point will map to more than one
                              destination point.
          ==================  ========================================

    use_src_mask: `bool`, optional
        For all methods other than 'nearest_stod', this must be True
        as it does not make sense to set it to False. For the
        'nearest_stod' method if it is True then points in the result
        that are nearest to a masked source point are
        masked. Otherwise, if it is False, then these points are
        interpolated to the nearest unmasked source points.

    use_dst_mask: `bool`, optional
        By default the mask of the data on the destination grid is not
        taken into account when performing regridding. If this option
        is set to True then it is.

    fracfield: `bool`, optional
        If the method of regridding is conservative the fraction of each
        destination grid cell involved in the regridding is returned instead
        of the regridded data if this is True. Otherwise this is ignored.

    axis_order: sequence, optional
        A sequence of items specifying dimension coordinates as
        retrieved by the `dim` method. These determine the order
        in which to iterate over the other axes of the field when
        regridding slices. The slowest moving axis will be the
        first one specified. Currently the regridding weights are
        recalculated every time the mask of a slice changes
        with respect to the previous one, so this option allows
        the user to minimise how frequently the mask changes.
    
    ignore_degenerate: `bool`, optional
        True by default. Instructs ESMPy to ignore degenerate cells
        when checking the grids for errors. Regridding will proceed
        and degenerate cells will be skipped, not producing a result,
        when set to True. Otherwise an error will be produced if
        degenerate cells are found. This will be present in the ESMPy
        log files if cf.REGRID_LOGGING is set to True. As of ESMF
        7.0.0 this only applies to conservative regridding.  Other
        methods always skip degenerate cells.

    {+i}
    
    _compute_field_mass: `dict`, optional
        If this is a dictionary then the field masses of the source
        and destination fields are computed and returned within the
        dictionary. The keys of the dictionary indicates the lat/long
        slice of the field and the corresponding value is a tuple
        containing the source field's mass and the destination field's
        mass. The calculation is only done if conservative regridding
        is being performed. This is for debugging purposes.

:Returns:

    out: `cf.{+Variable}`
        The regridded {+variable}.

:Examples 2:

Regrid the T axis of field ``f`` conservatively onto the grid
specified in the dimension coordinate ``t``:

>>> h = f.regridc({'T': t}, axes=('T'), 'nearest_stod')

Regrid the T axis of field ``f`` using bilinear interpolation onto
a grid contained in field ``g``:

>>> h = f.regridc(g, axes=('T'), method='bilinear')

Regrid the X and Y axes of field ``f`` conservatively onto a grid
contained in field ``g``:

>>> h = f.regridc(g, axes=('X','Y'), 'conservative')

Regrid the X and T axes of field ``f`` conservatively onto a grid
contained in field ``g`` using the destination mask:

>>> h = f.regridc(g, axes=('X','Y'), use_dst_mask=True, method='bilinear')

        '''
#        # List functionality
#        if self._list:
#            kwargs2 = self._parameters(locals())
#            return self._list_method('regridc', kwargs2)
        
        # Initialise ESMPy for regridding if found
        manager = Regrid.initialize()
        
        # If dst is a dictionary set flag
        if isinstance(dst, self.__class__):
            dst_dict = False
            # If dst is a field list use the first field
            if isinstance(dst, FieldList):
                dst = dst[0]
        else:
            dst_dict = True
        
        # Get the number of axes
        if isinstance(axes, basestring):
            axes = (axes,)

        n_axes = len(axes)
        if n_axes < 1 or n_axes > 3:
            raise ValueError('Between 1 and 3 axes must be individually ' +
                             'specified.')
        
        # Retrieve the source axis keys and dimension coordinates
        src_axis_keys, src_coords = self._regrid_get_cartesian_coords('source',
                                                                      axes)
        
        # Retrieve the destination axis keys and dimension coordinates
        if dst_dict:
            dst_coords = []
            for axis in axes:
                try:
                    dst_coords.append(dst[axis])
                except KeyError:
                    raise ValueError('Axis ' + str(axis) +
                                     ' not specified in dst.')
            #--- End: for
            dst_axis_keys = None
        else:
            dst_axis_keys, dst_coords = \
                        dst._regrid_get_cartesian_coords('destination', axes)
        
        # Get the axis indices and their order for the source field
        src_axis_indices, src_order, self = \
                        self._regrid_get_axis_indices(src_axis_keys, i=i)
        
        # Get the axis indices and their order for the destination field.
        if not dst_dict:
            dst_axis_indices, dst_order, dst = \
                        dst._regrid_get_axis_indices(dst_axis_keys, i=i)

        # Pad out a single dimension with an extra one (see comments
        # in _regrid_check_bounds)
        axis_keys_ext = []
        coords_ext = []
        src_axis_indices_ext = src_axis_indices
        src_order_ext = src_order
        if n_axes == 1 and self.squeeze().ndim > 1:
            src_shape = numpy_array(self.shape)
            tmp = src_shape.copy()
            tmp[src_axis_indices] = -1
            max_length = -1
            max_ind = -1
            for ind, length in enumerate(tmp):
                if length > max_length:
                    max_length = length
                    max_ind = ind
            if src_shape[src_axis_indices].prod()*max_length*8 < CHUNKSIZE():
                axis_keys_ext, coords_ext = \
                    self._regrid_get_cartesian_coords('source', [max_ind])
                src_axis_indices_ext, src_order_ext, self = \
                    self._regrid_get_axis_indices(axis_keys_ext +
                                                  src_axis_keys, i=i)
        
        # Calculate shape of each regridded section
        shape = self._regrid_get_section_shape([coord.size for coord in
                                                coords_ext + dst_coords],
                                               src_axis_indices_ext)
        
        # Check that method is valid
        if method is None:
            raise ValueError("Can't regrid: Must select a regridding method")
        #--- End: if
        
        if method not in ('conservative', 'patch', 'bilinear', 'nearest_stod',
                          'nearest_dtos'):
            raise ValueError("Can't regrid: Invalid method: {!r}".format(method))
        #--- End: if

        # Check that use_src_mask is True for all methods other than
        # nearest_stod
        if not use_src_mask and not method == 'nearest_stod':
            raise ValueError('It only makes sense for use_dst_mask to be ' +
                             'False when using the nearest_stod method.')
        #--- End: if

        if method == 'patch' and n_axes != 2:
            raise ValueError('Higher order patch recovery is only available ' +
                             'in 2D.')
        #--- End: if
        
        type(self)._regrid_check_bounds(src_coords,
                                        dst_coords, method,
                                        ext_coords=coords_ext)

        # Deal with case of 1D nonconservative regridding
        nonconservative1D = False
        if method != 'conservative' and n_axes == 1 and coords_ext == []:
            nonconservative1D = True
            coords_ext = [DimensionCoordinate(data=Data(
                [numpy_finfo('float32').epsneg, numpy_finfo('float32').eps]))]
        

        # Section the data into slices of up to three dimensions getting a
        # list of reordered keys if required. Reordering on an extended axis
        # will not have any effect as all the items in the keys will be None.
        # Therefore it is only checked if the axes specified in axis_order are
        # in the regridding axees as this is informative to the user.
        section_keys, sections = self._regrid_get_reordered_sections(axis_order,
            src_axis_keys, src_axis_indices_ext)
        
        # Use bounds if the regridding method is conservative.
        use_bounds = method == 'conservative'
        
        # Retrieve the destination field's mask if appropriate
        dst_mask = None
        if not dst_dict and use_dst_mask and dst.Data.ismasked:
            dst_mask = dst._regrid_get_destination_mask(dst_order,
                                                        cartesian=True,
                                                        coords_ext=coords_ext)
        
        # Create the destination ESMPy grid and fields
        dstgrid = Regrid.create_grid(coords_ext + dst_coords, use_bounds,
                                     mask=dst_mask, cartesian=True)
        dstfield = Regrid.create_field(dstgrid, 'dstfield')
        dstfracfield = Regrid.create_field(dstgrid, 'dstfracfield')
        
        # Regrid each section
        old_mask = None
        unmasked_grid_created = False
        for k in section_keys:
            d = sections[k]
            subsections = d.Data.section(src_axis_indices, chunks=True,
                                         min_step=2)
            for k2 in subsections.keys():
                d2 = subsections[k2]
                # Retrieve the source field's grid, create the ESMPy grid and a
                # handle to regridding.
                src_data = d2.squeeze().transpose(src_order_ext).array
                if nonconservative1D:
                    src_data = numpy_tile(src_data, (2,1))
                if (not (method == 'nearest_stod' and use_src_mask)
                    and numpy_ma_is_masked(src_data)):
                    mask = src_data.mask
                    if not numpy_array_equal(mask, old_mask):
                        # Release old memory
                        if old_mask is not None:
                            regridSrc2Dst.destroy()
                            srcfracfield.destroy()
                            srcfield.destroy()
                            srcgrid.destroy()
                        #--- End: if
                        # (Re)create the source ESMPy grid and fields
                        srcgrid = Regrid.create_grid(coords_ext + src_coords,
                                                     use_bounds, mask=mask,
                                                     cartesian=True)
                        srcfield = Regrid.create_field(srcgrid, 'srcfield')
                        srcfracfield = Regrid.create_field(srcgrid,
                                                           'srcfracfield')
                        # (Re)initialise the regridder
                        regridSrc2Dst = Regrid(srcfield, dstfield, srcfracfield,
                                               dstfracfield, method=method,
                                               ignore_degenerate=ignore_degenerate)
                        old_mask = mask
                    #--- End: if
                else:
                    if not unmasked_grid_created or old_mask is not None:
                        # Create the source ESMPy grid and fields
                        srcgrid = Regrid.create_grid(coords_ext + src_coords,
                                                     use_bounds, cartesian=True)
                        srcfield = Regrid.create_field(srcgrid, 'srcfield')
                        srcfracfield = Regrid.create_field(srcgrid,
                                                           'srcfracfield')
                        # Initialise the regridder
                        regridSrc2Dst = Regrid(srcfield, dstfield, srcfracfield,
                                               dstfracfield, method=method,
                                               ignore_degenerate=ignore_degenerate)
                        unmasked_grid_created = True
                        old_mask = None
                    #--- End: if
                #--- End: if
                
                # Fill the source and destination fields
                self._regrid_fill_fields(src_data, srcfield, dstfield)
                
                # Run regridding
                dstfield = regridSrc2Dst.run_regridding(srcfield, dstfield)
                
                # Compute field mass if requested for conservative regridding
                if _compute_field_mass is not None and method == 'conservative':
                    self._regrid_compute_field_mass(_compute_field_mass,
                                                    k, srcgrid,
                                                    srcfield,
                                                    srcfracfield,
                                                    dstgrid, dstfield)
                #--- End: if
                
                # Get the regridded data or frac field as a numpy array
                regridded_data = self._regrid_get_regridded_data(method,
                                                                 fracfield,
                                                                 dstfield,
                                                                 dstfracfield)
                
                if nonconservative1D:
                    regridded_data = regridded_data[0]
                
                # Insert regridded data, with axes in correct order
                subsections[k2] = Data(
                    regridded_data.squeeze().transpose(src_order_ext).reshape(shape),
                    units=self.Units)
            #--- End: for
            sections[k] = Regrid.reconstruct_sectioned_data(subsections)
        #--- End: for
        
        # Construct new data from regridded sections
        new_data = Regrid.reconstruct_sectioned_data(sections)
        
        # Construct new field
        if i:
            f = self
        else:
            f = self.copy(_omit_Data=True)
        #--- End:if
        
        ## Update ancillary variables of new field
        #f._conform_ancillary_variables(src_axis_keys, keep_size_1=False)
        
        # Update coordinate references of new field
        f._regrid_update_coordinate_references(dst, src_axis_keys,
                                               method, use_dst_mask,
                                               i, cartesian=True,
                                               axes=axes,
                                               n_axes=n_axes)
        
        # Update coordinates of new field
        f._regrid_update_coordinates(dst, dst_dict, dst_coords,
                                     src_axis_keys, dst_axis_keys,
                                     cartesian=True)
        
        # Copy across the destination fields coordinate references if necessary
        if not dst_dict:
            f._regrid_copy_coordinate_references(dst, dst_axis_keys)
        #--- End: if
        
        # Insert regridded data into new field
        f.insert_data(new_data, axes=self.data_axes())
        
        # Release old memory
        regridSrc2Dst.destroy()
        dstfracfield.destroy()
        srcfracfield.destroy()
        dstfield.destroy()
        srcfield.destroy()
        dstgrid.destroy()
        srcgrid.destroy()
        
        return f
    #--- End: def

    def derivative(self, axis, cyclic=None, one_sided_at_boundary=False,
                   i=False):
        '''Return the centred finite difference along the specified axis.

If the axis is cyclic then the boundary is wrapped around, otherwise
missing values are used at the boundary unless one-sided finite
differences are requested.

:Parameters:

    {+axes}

    cyclic: `bool`, optional
        If True then the boundary is wrapped around, otherwise the
        value of *one_sided_at_boundary* determines the boundary
        condition. If None then the cyclicity of the axis is
        autodetected.

    one_sided_at_boundary: `bool`, optional
        If True then one-sided finite differences are used at the
        boundary, otherwise missing values are used.

    {+i}

:Returns:

    out: `cf.{+Variable}`

        '''

        # Retrieve the axis
        dims = self.dims(axis)
        len_dims = len(dims)
        if not len_dims:
            raise ValueError('Invalid axis specifier')
        elif len_dims != 1:
            raise ValueError('Axis specified is not unique.')
        #--- End: if
        axis_key, coord = dims.popitem()

        # Get the axis index
        axis_index = self.data_axes().index(axis_key)

        # Automatically detect the cyclicity of the axis if cyclic is None
        if cyclic is None:
            cyclic = self.iscyclic(axis_key)
        #--- End: if

        # Set the boundary conditions
        if cyclic:
            mode = 'wrap'
        elif one_sided_at_boundary:
            mode = 'nearest'
        else:
            mode = 'constant'
        #--- End: if

        # Find the finite difference of the field
        f = self.convolution_filter(('user', [1, 0, -1]), axis=axis_key,
                                    mode=mode, update_bounds=False, i=i)

        # Find the finite difference of the axis
        d = convolve1d(coord, [1, 0, -1], mode=mode, cval=numpy_nan)
        if not cyclic and not one_sided_at_boundary:
            with numpy_errstate(invalid='ignore'):
                d = numpy_ma_masked_invalid(d)
            #--- End: with
        #--- End: if

        # Reshape the finite difference of the axis for broadcasting
        shape = [1] * self.ndim
        shape[axis_index] = d.size
        d = d.reshape(shape)

        # Find the derivative
        f.Data /= Data(d, coord.units)

        # Update the standard name and long name
        standard_name = getattr(f, 'standard_name', None)
        long_name = getattr(f, 'long_name', None)
        if standard_name is not None:
            del f.standard_name
            f.long_name = 'derivative of ' + standard_name
        elif long_name is not None:
            f.long_name = 'derivative of ' + long_name
        #--- End: if

        return f
    #--- End: def

#--- End: class


# ====================================================================
#
# SubspaceField object
#
# ====================================================================

class SubspaceField(SubspaceVariable):
    '''Return a subspace of a field.

A subspace may be defined in "domain-space" via data array values of
its domain items: dimension coordinate, auxiliary coordinate, cell
measure, domain ancillary and field ancillary objects.

Alternatively, a subspace my be defined be in "index-space" via
explicit indices for the data array using an extended Python slicing
syntax.

Subspacing by values of 1-d coordinates allows a subspaced field to be
defined via coordinate values of its domain. The benefits of
subspacing in this fashion are:

  * The axes to be subspaced may identified by name.
  * The position in the data array of each axis need not be known and
    the axes to be subspaced may be given in any order.
  * Axes for which no subspacing is required need not be specified.
  * Size 1 axes in the subspaced field are always retained, but may be
    subsequently removed with the `~cf.Field.squeeze` method.

  * Size 1 axes of the domain which are not spanned by the data array
    may be specified.

Metadata values are provided as keyword arguments. Metadata items are
identified by their identity or their axis's identifier in the field.

``f.subspace(*args, **kwargs)`` is equivalent to ``f[f.indices(*args,
**kwargs)]``. See `cf.Field.indices` for details.

.. seealso:: `__getitem__`, `indices`, `where`

:Examples:

>>> f,shape
(12, 73, 96)
>>> f.subspace().shape
(12, 73, 96)
>>> f.subspace(latitude=0).shape
(12, 1, 96)
>>> f.subspace(latitude=cf.wi(-30, 30)).shape
(12, 25, 96)
>>> f.subspace(long=cf.ge(270, 'degrees_east'), lat=cf.set([0, 2.5, 10])).shape
(12, 3, 24)
>>> f.subspace(latitude=cf.lt(0, 'degrees_north'))
(12, 36, 96)
>>> f.subspace(latitude=[cf.lt(0, 'degrees_north'), 90])
(12, 37, 96)
>>> import math
>>> f.subspace('exact', longitude=cf.lt(math.pi, 'radian'), height=2)
(12, 73, 48)
>>> f.subspace(height=cf.gt(3))
IndexError: No indices found for 'height' values gt 3
>>> f.subspace(dim2=3.75).shape
(12, 1, 96)
>>> f.subspace(time=cf.le(cf.dt('1860-06-16 12:00:00')).shape
(6, 73, 96)
>>> f.subspace(time=cf.gt(cf.dt(1860, 7)),shape
(5, 73, 96)

Note that if a comparison function (such as `cf.wi`) does not specify
any units, then the units of the named item are assumed.

    '''
        
    __slots__ = []

    def __call__(self, *args, **kwargs):
        '''

Return a subspace of the field defined by coordinate values.

:Parameters:

    kwargs: *optional*
        Keyword names identify coordinates; and keyword values specify
        the coordinate values which are to be reinterpreted as indices
        to the field's data array.


~~~~~~~~~~~~~~ /??????
        Coordinates are identified by their exact identity or by their
        axis's identifier in the field's domain.

        A keyword value is a condition, or sequence of conditions,
        which is evaluated by finding where the coordinate's data
        array equals each condition. The locations where the
        conditions are satisfied are interpreted as indices to the
        field's data array. If a condition is a scalar ``x`` then this
        is equivalent to the `cf.Query` object ``cf.eq(x)``.

:Returns:

    out: `cf.{+Variable}`

:Examples:

>>> f.indices(lat=0.0, lon=0.0)
>>> f.indices(lon=cf.lt(0.0), lon=cf.set([0, 3.75]))
>>> f.indices(lon=cf.lt(0.0), lon=cf.set([0, 356.25]))
>>> f.indices(lon=cf.lt(0.0), lon=cf.set([0, 3.75, 356.25]))

'''
    def __call__(self, *args, **kwargs):
        '''
        '''
        field = self.variable

        if not args and not kwargs:
            return field.copy()    

        return field[field.indices(*args, **kwargs)]
    #--- End: def

    def __getitem__(self, indices):
        '''Called to implement evaluation of x[indices].

x.__getitem__(indices) <==> x[indices]

Returns a subspace of a field.

        '''
        return self.variable[indices]
    #--- End: def

    def __setitem__(self, indices, value):
        '''Called to implement assignment to x[indices]

x.__setitem__(indices, value) <==> x[indices]

        '''      
        self.variable[indices] = value
    #--- End: def

#--- End: class


# ====================================================================
#
# FieldList object
#
# ====================================================================

class FieldList(list):
    '''An ordered sequence of fields.

Each element of a field list is a `cf.Field` object.

A field list supports the python list-like operations (such as
indexing and methods like `!append`).

>>> fl = cf.FieldList()
>>> len(fl)
0
>>> f
<CF Field: air_temperaturetime(12), latitude(73), longitude(96) K>
>>> fl = cf.FieldList(f)
>>> len(fl)
1
>>> fl = cf.FieldList([f, f])
>>> len(fl)
2
>>> fl = cf.FieldList(cf.FieldList([f] * 3))
>>> len(fl)
3
>>> len(fl + fl)
6

These methods provide functionality similar to that of a
:ref:`built-in list <python:tut-morelists>`. The main difference is
that when a field element needs to be assesed for equality its
`~cf.Field.equals` method is used, rather than the ``==`` operator.
    '''   

    def __init__(self, fields=None):
        '''
**Initialization**

:Parameters:

    fields: (sequence of) `cf.Field`, optional
         Create a new field list with these fields.

'''
        if fields is not None:
            if isinstance(fields, Field):
                self.append(fields)
            else:
                self.extend(fields)         
    #--- End: def

    def __repr__(self):
        '''Called by the :py:obj:`repr` built-in function.

x.__repr__() <==> repr(x)

        '''
        
        out = [repr(f) for f in self]
        out = ',\n '.join(out)
        return '['+out+']'
    #--- End: def

    def __str__(self):
        '''Called by the :py:obj:`str` built-in function.

x.__str__() <==> str(x)

        '''
        return '\n'.join(str(f) for f in self)
    #--- End: def

    # ================================================================
    # Overloaded list methods
    # ================================================================    
    def __add__(self, x):
        '''Called to implement evaluation of f + x

f.__add__(x) <==> f + x

:Examples 1:

>>> h = f + g
>>> f += g

:Returns:

    out: `cf.FieldList`

        '''
        return type(self)(list.__add__(self, x))
    #--- End: def

    def __mul__(self, x):
        '''Called to implement evaluation of f * x

f.__mul__(x) <==> f * x

:Examples:

>>> h = f * 2
>>> f *= 2

:Returns:

    out: `cf.FieldList`

        '''
        return type(self)(list.__mul__(self, x))
    #--- End: def

    def __getslice__(self, i, j):
        '''Called to implement evaluation of f[i:j]

f.__getslice__(i, j) <==> f[i:j]

:Examples:

>>> g = f[0:1]
>>> g = f[1:-4]
>>> g = f[:1]
>>> g = f[1:]

:Returns:

    out: `cf.FieldList`

        '''
        return type(self)(list.__getslice__(self, i, j))
    #--- End: def

    def __getitem__(self, index):
        '''Called to implement evaluation of f[index]

f.__getitem_(index) <==> f[index]

:Examples:

>>> g = f[0]
>>> g = f[-1:-4:-1]
>>> g = f[2:2:2]

:Returns:

    out: `cf.Field` or `cf.FieldList`
        If *index* is an integer then a field is returned. If *index*
        is a slice then a field list is returned, which may be empty.

        '''
        out = list.__getitem__(self, index)

        if isinstance(out, list):
            return type(self)(out)

        return out
    #--- End: def

    __len__     = list.__len__
    __setitem__ = list.__setitem__    
    append      = list.append
    extend      = list.extend
    insert      = list.insert
    pop         = list.pop
    reverse     = list.reverse
    sort        = list.sort

    def __contains__(self, y):
        '''Called to implement membership test operators.

x.__contains__(y) <==> y in x

Each field in the field list is compared with the field's
`~cf.Field.equals` method, as aopposed to the ``==`` operator.

Note that ``y in fl`` is equivalent to ``any(f.equals(y) for f in fl)``.

        '''
        for f in self:
            if f.equals(y):
                return True
            
        return False
    #--- End: def

    def close(self):
        '''Close all files referenced by each field.

Note that a closed file will be automatically reopened if its contents
are subsequently required.

:Examples 1:

>>> f.{+name}()

:Returns:

    `None`

        '''
        for f in self:
            f.close()
        #--- End: for
    #--- End: def

    def count(self, value):
        '''Return number of occurrences of value

Each field in the field list is compared with the field's
`~cf.Field.equals` method, as opposed to the ``==`` operator.

Note that ``fl.count(value)`` is equivalent to ``sum(f.equals(value)
for f in fl)``.

.. seealso:: `cf.Field.equals`, :py:obj:`list.count`

:Examples:

>>> f = cf.FieldList([a, b, c, a])
>>> f.count(a)
2
>>> f.count(b)
1
>>> f.count(a+1)
0

        '''
        return len([None for f in self if f.equals(value)])
    #--- End def

    def index(self, value, start=0, stop=None):
        '''Return first index of value.

Each field in the field list is compared with the field's
`~cf.Field.equals` method, as aopposed to the ``==`` operator.

It is an error if there is no such field.

.. seealso:: :py:obj:`list.index`

:Examples:

>>>

        '''      
        if start < 0:
            start = len(self) + start

        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop = len(self) + stop

        for i, f in enumerate(self[start:stop]):
            if f.equals(x):
               return i + start
        #--- End: for

        raise ValueError(
            "{0!r} is not in {1}".format(x, self.__class__.__name__))
    #--- End: def

    def remove(self, value):
        '''Remove first occurrence of value.

Each field in the field list is compared with its `~cf.Field.equals`
method, as opposed to the ``==`` operator.

.. seealso:: :py:obj:`list.remove`

        '''
        for i, f in enumerate(self):
            if f.equals(value):
                del self[i]
                return

        raise ValueError(
            "{0}.remove(x): x not in {0}".format(self.__class__.__name__))
    #--- End: def

    def sort(self, cmp=None, key=None, reverse=False):
        '''Stable sort of the field list *IN PLACE*

By default the field list is sorted by the identities of its fields.

.. versionadded:: 1.0.4

.. seealso:: `reverse`, :py:obj:`sorted`

:Examples 1:

>>> fl.sort()

:Parameters:

    cmp: function, optional
        Specifies a custom comparison function of two arguments
        (iterable elements) which should return a negative, zero or
        positive number depending on whether the first argument is
        considered smaller than, equal to, or larger than the second
        argument. The default value is `None`.
        
          *Example:*
            ``cmp=lambda x,y: cmp(x.lower(), y.lower())``.

    key: function, optional
        Specify a function of one argument that is used to extract a
        comparison key from each list element. By default fiel list is
        sorted by field identity, i.e. the default value of *key* is
        ``lambda f: f.identity()``.

    reverse: `bool`, optional
        If set to True, then the list elements are sorted as if each
        comparison were reversed.

:Returns:

    `None`

:Examples 2:

>>> fl
[<CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>,
 <CF Field: ocean_meridional_overturning_streamfunction(time(12), region(4), depth(40), latitude(180)) m3 s-1>,
 <CF Field: air_temperature(time(12), latitude(64), longitude(128)) K>,
 <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>]
>>> fl.sort()
>>> fl
[<CF Field: air_temperature(time(12), latitude(64), longitude(128)) K>,
 <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>,
 <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>,
 <CF Field: ocean_meridional_overturning_streamfunction(time(12), region(4), depth(40), latitude(180)) m3 s-1>]
>>> fl.sort(reverse=True)
>>> fl
[<CF Field: ocean_meridional_overturning_streamfunction(time(12), region(4), depth(40), latitude(180)) m3 s-1>,
 <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>,
 <CF Field: eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1>,
 <CF Field: air_temperature(time(12), latitude(64), longitude(128)) K>]

>>> [f.datum(0) for f in fl]
[masked,
 -0.12850454449653625,
 -0.12850454449653625,
 236.51275634765625]
>>> fl.sort(key=lambda f: f.datum(0), reverse=True)
>>> [f.datum(0) for f in fl]
[masked,
 236.51275634765625,
 -0.12850454449653625,
 -0.12850454449653625]

>>> from operator import attrgetter
>>> [f.long_name for f in fl]
['Meridional Overturning Streamfunction',
 'U COMPNT OF WIND ON PRESSURE LEVELS',
 'U COMPNT OF WIND ON PRESSURE LEVELS',
 'air_temperature']
>>> fl.sort(cmp=lambda x,y: cmp(x.lower(), y.lower()), key=attrgetter('long_name'))
>>> [f.long_name for f in fl]
['air_temperature',
 'Meridional Overturning Streamfunction',
 'U COMPNT OF WIND ON PRESSURE LEVELS',
 'U COMPNT OF WIND ON PRESSURE LEVELS']

        '''
        return super(FieldList, self).sort(cmp, key, reverse)
    #--- End: def

#    # ================================================================
#    # Special methods
#    # ================================================================
#    def __array__(self): self._forbidden('special method', '__array__')
#    def __data__(self): self._forbidden('special method', '__data__')

#    # ================================================================
#    # Private methods
#    # ================================================================
#    def _binary_operation(self, y, method):
#        if isinstance(y, self.__class__):
#            if len(y) != 1:
#                raise ValueError(
#                    "Can't {0}: Incompatible {1} lengths ({2}, {3})".format(
#                        method, self.__class__.__name__, len(self), len(y)))#
#
#        if method[2] == 'i':
#            # In place
#            for f in self:
#                f._binary_operation(y, method)
#            return self
#        else:         
#            # Not in place
#            return type(self)([f._binary_operation(y, method) for f in self])
#    #--- End: def
#
#    def _unary_operation(self, method):
#        return type(self)([f._unary_operation(method) for f in self])
#    #--- End: def
#
#    def _forbidden(self, x, name):
#        raise AttributeError(
#            "{0} has no {1} {2!r}. {2!r} may be accessed on each field element.".format(
#                self.__class__.__name__, x, name))
#    #--- End: def
#
#    # ================================================================
#    # CF properties
#    # ================================================================
#    @property
#    def add_offset(self): self._forbidden('CF property', 'add_offset')
#    @property
#    def calendar(self): self._forbidden('CF property', 'calendar')
#    @property
#    def cell_methods(self): self._forbidden('CF property', 'cell_methods')
#    @property
#    def comment(self): self._forbidden('CF property', 'comment')
#    @property
#    def Conventions(self): self._forbidden('CF property', 'Conventions')
#    @property
#    def featureType(self): self._forbidden('CF property', 'featureType')
#    @property
#    def _FillValue(self): self._forbidden('CF property', '_FillValue')
#    @property
#    def flag_masks(self): self._forbidden('CF property', 'flag_masks')
#    @property
#    def flag_meanings(self): self._forbidden('CF property', 'flag_meanings')
#    @property
#    def flag_values(self): self._forbidden('CF property', 'flag_values')
#    @property
#    def history(self): self._forbidden('CF property', 'history')
#    @property
#    def institution(self): self._forbidden('CF property', 'institution')
#    @property
#    def leap_month(self): self._forbidden('CF property', 'leap_month')
#    @property
#    def leap_year(self): self._forbidden('CF property', 'leap_year')
#    @property
#    def long_name(self): self._forbidden('CF property', 'long_name')
#    @property
#    def missing_value(self): self._forbidden('CF property', 'missing_value')
#    @property
#    def month_lengths(self): self._forbidden('CF property', 'month_lengths')
#    @property
#    def references(self): self._forbidden('CF property', 'references')
#    @property
#    def scale_factor(self): self._forbidden('CF property', 'scale_factor')
#    @property
#    def source(self): self._forbidden('CF property', 'source')
#    @property
#    def standard_error_multiplier(self): self._forbidden('CF property', 'standard_error_multiplier')
#    @property
#    def standard_name(self): self._forbidden('CF property', 'standard_name')
#    @property
#    def title(self): self._forbidden('CF property', 'title')
#    @property
#    def units(self): self._forbidden('CF property', 'units')
#    @property
#    def valid_max(self): self._forbidden('CF property', 'valid_max')
#    @property
#    def valid_min(self): self._forbidden('CF property', 'valid_min')
#    @property
#    def valid_range(self): self._forbidden('CF property', 'valid_range')
#
#    # ================================================================
#    # Attributes
#    # ================================================================
#    @property
#    def array(self): self._forbidden('attribute', 'array')
#    @property
#    def attributes(self): self._forbidden('attribute', 'attributes')
#    @property
#    def Data(self): self._forbidden('attribute', 'Data')
#    @property
#    def data(self): self._forbidden('attribute', 'data')
#    @property
#    def DSG(self): self._forbidden('attribute', 'DSG')
#    @property
#    def day(self): self._forbidden('attribute', 'day')
#    @property
#    def Axes(self): self._forbidden('attribute', 'Axes')
#    @property
#    def dtarray(self): self._forbidden('attribute', 'dtarray')
#    @property
#    def dtvarray(self): self._forbidden('attribute', 'dtvarray')
#    @property
#    def dtype(self): self._forbidden('attribute', 'dtype')
#    @property
#    def Flags(self): self._forbidden('attribute', 'Flags')
#    @property
#    def hardmask(self): self._forbidden('attribute', 'hardmask')
#    @property
#    def hour(self): self._forbidden('attribute', 'hour')
#    @property
#    def isscalar(self): self._forbidden('attribute', 'isscalar')
#    @property
#    def Flags(self): self._forbidden('attribute', 'Flags')
#    @property
#    def minute(self): self._forbidden('attribute', 'minute')
#    @property
#    def month(self): self._forbidden('attribute', 'month')
#    @property
#    def ndim(self): self._forbidden('attribute', 'ndim')
#    @property
#    def properties(self): self._forbidden('attribute', 'properties')
#    @property
#    def rank(self): self._forbidden('attribute', 'rank')
#    @property
#    def second(self): self._forbidden('attribute', 'second')
#    @property
#    def shape(self): self._forbidden('attribute', 'shape')
#    @property
#    def size(self): self._forbidden('attribute', 'size') 
#    @property
#    def T(self): self._forbidden('attribute', 'T')
#    @property
#    def Units(self): self._forbidden('attribute', 'Units')
#    @property
#    def varray(self): self._forbidden('attribute', 'varray')
#    @property
#    def X(self): self._forbidden('attribute', 'X')
#    @property
#    def Y(self): self._forbidden('attribute', 'Y')
#    @property
#    def year(self): self._forbidden('attribute', 'year')
#    @property
#    def Z(self): self._forbidden('attribute', 'Z')
#    
#    # ================================================================
#    # Methods
#    # ================================================================
#    def all(self, *args, **kwargs): self._forbidden('method', 'all')
#    def any(self, *args, **kwargs): self._forbidden('method', 'any')
#    def allclose(self, *args, **kwargs): self._forbidden('method', 'allclose')
#    def aux(self, *args, **kwargs): self._forbidden('method', 'aux')
#    def auxs(self, *args, **kwargs): self._forbidden('method', 'auxs')
#    def axes(self, *args, **kwargs): self._forbidden('method', 'axes')
#    def axis(self, *args, **kwargs): self._forbidden('method', 'axis')
#    def axis_name(self, *args, **kwargs): self._forbidden('method', 'axis_name')
#    def axis_size(self, *args, **kwargs): self._forbidden('method', 'axis_size')
#    def coord(self, *args, **kwargs): self._forbidden('method', 'coord')
#    def coords(self, *args, **kwargs): self._forbidden('method', 'coords')
#    def cyclic(self, *args, **kwargs): self._forbidden('method', 'cyclic')
#    def data_axes(self, *args, **kwargs): self._forbidden('method', 'data_axes')
#    def dim(self, *args, **kwargs): self._forbidden('method', 'dim')
#    def dims(self, *args, **kwargs): self._forbidden('method', 'dims')
#    def field(self, *args, **kwargs): self._forbidden('method', 'field')
#    def iscyclic(self, *args, **kwargs): self._forbidden('method', 'iscyclic')
#    def insert_aux(self, *args, **kwargs): self._forbidden('method', 'insert_aux')
#    def insert_axis(self, *args, **kwargs): self._forbidden('method', 'insert_axis')
#    def insert_data(self, *args, **kwargs): self._forbidden('method', 'insert_data')
#    def insert_dim(self, *args, **kwargs): self._forbidden('method', 'insert_dim')
#    def insert_measure(self, *args, **kwargs): self._forbidden('method', 'insert_measure')
#    def insert_ref(self, *args, **kwargs): self._forbidden('method', 'insert_ref')
#    def indices(self, *args, **kwargs): self._forbidden('method', 'indices')
#    def item(self, *args, **kwargs): self._forbidden('method', 'item')
#    def item_axes(self, *args, **kwargs): self._forbidden('method', 'item_axes')
#    def items(self, *args, **kwargs): self._forbidden('method', 'items')
#    def items_axes(self, *args, **kwargs): self._forbidden('method', 'items_axes')
#    def match(self, *args, **kwargs): self._forbidden('method', 'match')
#    def max(self, *args, **kwargs): self._forbidden('method', 'max')
#    def mean(self, *args, **kwargs): self._forbidden('method', 'mean')
#    def measure(self, *args, **kwargs): self._forbidden('method', 'measure')
#    def measures(self, *args, **kwargs): self._forbidden('method', 'measures')
#    def mid_range(self, *args, **kwargs): self._forbidden('method', 'mid_range')
#    def min(self, *args, **kwargs): self._forbidden('method', 'min')
#    def period(self, *args, **kwargs): self._forbidden('method', 'period')
#    def range(self, *args, **kwargs): self._forbidden('method', 'range')
#    def ref(self, *args, **kwargs): self._forbidden('method', 'ref')
#    def refs(self, *args, **kwargs): self._forbidden('method', 'refs')
#    def remove_axes(self, *args, **kwargs): self._forbidden('method', 'remove_axes')
#    def remove_axis(self, *args, **kwargs): self._forbidden('method', 'remove_axis')
#    def remove_data(self, *args, **kwargs): self._forbidden('method', 'remove_data')
#    def remove_item(self, *args, **kwargs): self._forbidden('method', 'remove_item')
#    def remove_items(self, *args, **kwargs): self._forbidden('method', 'remove_items')
#    def sample_size(self, *args, **kwargs): self._forbidden('method', 'sample_size')
#    def sd(self, *args, **kwargs): self._forbidden('method', 'sd')
#    def sum(self, *args, **kwargs): self._forbidden('method', 'sum')
#    def transpose_item(self, *args, **kwargs): self._forbidden('method', 'transpose_item')
#    def unique(self, *args, **kwargs): self._forbidden('method', 'unique')
#    def var(self, *args, **kwargs): self._forbidden('method', 'var')
#    
#    @property
#    def binary_mask(self):
#        '''For each field, a field of the binary (0 and 1) mask of the data
#array.
#
#Values of 1 indicate masked elements.
#
#.. seealso:: `mask`
#
#:Examples:
#
#>>> f[0].shape
#(12, 73, 96)
#>>> m = f.binary_mask
#>>> m[0].long_name
#'binary_mask'
#>>> m[0].shape
#(12, 73, 96)
#>>> m[0].dtype
#dtype('int32')
#>>> m[0].data
#<CF Data: [[[1, ..., 0]]] >
#
#        '''
#        return self._list_attribute('binary_mask')
#    #--- End: def
#
#    @property
#    def mask(self):
#        '''For each field, a field of the mask of the data array.
#
#Values of True indicate masked elements.
#
#.. seealso:: `binary_mask`
#
#:Examples:
#
#>>> f[0].shape
#(12, 73, 96)
#>>> m = f.mask
#>>> m[0].long_name
#'mask'
#>>> m[0].shape
#(12, 73, 96)
#>>> m[0].dtype
#dtype('bool')
#>>> m[0].data
#<CF Data: [[[True, ..., False]]] >
#
#        '''
#        return self._list_attribute('mask')
#    #--- End: def

    def __deepcopy__(self, memo):
        '''Called by the `copy.deepcopy` standard library function.

        '''
        return self.copy()
    #--- End: def

    def _parameters(self, d):
        del d['self']
        if 'kwargs' in d:
            d.update(d.pop('kwargs'))
        return d
    #--- End: def

    def _deprecated_method(self, name):
        return "{} method has been removed from a field list. Use on individual fields.".format(name)

    def anchor(self, *args, **kwargs):       raise DeprecationError(self._deprecated_method('anchor'))
    def ceil(self, *args, **kwargs):         raise DeprecationError(self._deprecated_method('ceil'))
    def cell_area(self, *args, **kwargs):    raise DeprecationError(self._deprecated_method('cell_area'))
    def collapse(self, *args, **kwargs):     raise DeprecationError(self._deprecated_method('collapse'))
    def cos(self, *args, **kwargs):          raise DeprecationError(self._deprecated_method('cos'))
    def cyclic(self, *args, **kwargs):       raise DeprecationError(self._deprecated_method('cyclic'))    
    def domain_mask(self, *args, **kwargs):  raise DeprecationError(self._deprecated_method('domain_mask'))
    def expand_dims(self, *args, **kwargs):  raise DeprecationError(self._deprecated_method('expand_dims'))
    def field(self, *args, **kwargs):        raise DeprecationError(self._deprecated_method('field'))
    def flip(self, *args, **kwargs):         raise DeprecationError(self._deprecated_method('flip'))
    def indices(self, *args, **kwargs):      raise DeprecationError(self._deprecated_method('indices'))
    def period(self, *args, **kwargs):       raise DeprecationError(self._deprecated_method('period'))
    def regridc(self, *args, **kwargs):      raise DeprecationError(self._deprecated_method('regridc'))    
    def regrids(self, *args, **kwargs):      raise DeprecationError(self._deprecated_method('regrids'))
    def remove_item(self, *args, **kwargs):  raise DeprecationError(self._deprecated_method('remove_item'))
    def remove_items(self, *args, **kwargs): raise DeprecationError(self._deprecated_method('remove_items'))
    def remove_axis(self, *args, **kwargs):  raise DeprecationError(self._deprecated_method('remove_axis'))
    def remove_axes(self, *args, **kwargs):  raise DeprecationError(self._deprecated_method('remove_axes'))
    def roll(self, *args, **kwargs):         raise DeprecationError(self._deprecated_method('roll'))
    def round(self, *args, **kwargs):        raise DeprecationError(self._deprecated_method('round'))
    def section(self, *args, **kwargs):      raise DeprecationError(self._deprecated_method('section'))
    def sin(self, *args, **kwargs):          raise DeprecationError(self._deprecated_method('sin'))
    def squeeze(self, *args, **kwargs):      raise DeprecationError(self._deprecated_method('squeeze'))
    def subspace(self, *args, **kwargs):     raise DeprecationError(self._deprecated_method('subspace'))
    def tan(self, *args, **kwargs):          raise DeprecationError(self._deprecated_method('tan'))
    def transpose(self, *args, **kwargs):    raise DeprecationError(self._deprecated_method('transpose'))
    def unlimited(self, *args, **kwargs):    raise DeprecationError(self._deprecated_method('unlimited'))
    def unsqueeze(self, *args, **kwargs):    raise DeprecationError(self._deprecated_method('unsqueeze'))
    def where(self, *args, **kwargs):        raise DeprecationError(self._deprecated_method('where'))
    def weights(self, *args, **kwargs):      raise DeprecationError(self._deprecated_method('weights'))

    def concatenate(self, axis=0, _preserve=True):
        '''

Join a sequence of fields together.

This is different to `cf.aggregate` because it does not account for
all metadata. For example, it assumes that the axis order is the same
in each field.

.. versionadded:: 1.0

.. seealso:: `cf.aggregate`, `cf.Data.concatenate`

:Parameters:

    axis: `int`, optional

:Returns:

    out: `cf.Field`

:Examples:

'''
        return self[0].concatenate(self, axis=axis, _preserve=_preserve)
    #--- End: def

    
    def copy(self, _omit_Data=False, _only_Data=False,
             _omit_special=None, _omit_properties=False,
             _omit_attributes=False):
        '''Return a deep copy.

``f.copy()`` is equivalent to ``copy.deepcopy(f)``.

:Examples 1:

>>> g = f.copy()

:Returns:

    out: `cf.FieldList`
        The deep copy.

:Examples 2:

>>> g = f.copy()
>>> g is f
False
>>> f.equals(g)
True
>>> import copy
>>> h = copy.deepcopy(f)
>>> h is f
False
>>> f.equals(g)
True

        '''
        kwargs2 = self._parameters(locals())
        return type(self)([f.copy(**kwargs2) for f in self])
    #--- End: def
    
    def dump(self, display=True, _level=0, _title='Field', _q='-'):
        '''A full description of each field.

By default, the description is given without abbreviation with the
exception of data arrays (which are abbreviated to their first and
last values) and fields contained in coordinate references and
ancillary variables (which are given as one-line summaries).

:Examples 1:
        
>>> fl.dump()

:Parameters:

    display: `bool`, optional
        If False then return the descriptionfor each field as a
        string. By default the descriptions are printed.

          *Example:*
            ``fl.dump()`` is equivalent to ``for f in fl: print
            f.dump(display=False)``.

:Returns:

    out: `None` or `list`
        If *display* is True then the description is printed and
        `None` is returned. Otherwise a list of strings containing the
        description for each field is returned.

        '''   
        kwargs2 = self._parameters(locals())

        if display:
            for f in self:
                f.dump(**kwargs2)

            return
        else:
            return [f.dump(**kwargs2) for f in self]
    #--- End: def

    def equals(self, other, rtol=None, atol=None, ignore_fill_value=False,
               traceback=False, ignore=(), _set=False):
        '''True if two field lists are equal, False otherwise.

Two {+variable}s are equal if they have the same number of elements
and the field elements are equal pairwise, i.e. ``f.equals(g)`` is
equivalent to ``all(x.equals(y) for x, y in map(None, f, g))``.

Two fields are equal if ...

Note that a single element {+variable} may be equal to field, for
example ``f[0:1].equals(f[0])`` and ``f[0].equals(f[0:1])`` are always
True.

.. seealso:: `set_equals`, `cf.Field.equals`

:Examples 1:

>>> b = f.equals(g)

:Parameters:

    other: `object`
        The object to compare for equality.

    {+atol}

    {+rtol}

    ignore_fill_value: `bool`, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback: `bool`, optional
        If True then print a traceback highlighting where the two
        {+variable}s differ.

    ignore: `tuple`, optional
        The names of CF properties to omit from the comparison. By
        default, the CF Conventions property is omitted.

:Returns: 
  
    out: `bool`
        Whether or not the two {+variable}s are equal.

:Examples 2:


.. seealso:: `cf.Field.equals`

:Examples 1:

>>> g = f.copy()
>>> g.equals(f)
True

        '''
        # Check for object identity
        if self is other:
            return True

        # Check that each instance is of the same type
        if not isinstance(other, self.__class__):
            if traceback:
                print("{0}: Different types: {0}, {1}".format(
			self.__class__.__name__,
			other.__class__.__name__))
	    return False
        #--- End: if

        # Check that there are equal numbers of fields
        len_self = len(self)
        if len_self != len(other): 
            if traceback:
                print("{}: Different numbers of elements: {}, {}".format(
		    self.__class__.__name__,
		    len_self,
		    len(other)))
            return False
        #--- End: if

        if len_self == 1:
            _set = False
            
	if not _set:
       	    # ----------------------------------------------------
    	    # Check the lists pair-wise
    	    # ----------------------------------------------------
    	    for i, (f, g) in enumerate(zip(self, other)):
    	        if not f.equals(g, rtol=rtol, atol=atol,
                                ignore_fill_value=ignore_fill_value,
    				ignore=ignore, traceback=traceback):
    	            if traceback:
    		        print("{}: Different element {}: {!r}, {!r}".format(
    			    self.__class__.__name__, i, f, g))
                    return False
        else:
    	    # ----------------------------------------------------
    	    # Check the lists set-wise
    	    # ----------------------------------------------------
    	    # Group the variables by identity
    	    self_identity = {}
            for f in self:
                self_identity.setdefault(f.identity(), []).append(f)

    	    other_identity = {}
            for f in other:
                other_identity.setdefault(f.identity(), []).append(f)

    	    # Check that there are the same identities
    	    if set(self_identity) != set(other_identity):
    	        if traceback:
    		    print("{}: Different sets of identities: {}, {}".format(
    			self.__class__.__name__,
    			set(self_identity),
    			set(other_identity)))
    	        return False
            #--- End: if

            # Check that there are the same number of variables
    	    # for each identity
            for identity, fl in self_identity.iteritems():
    	        gl = other_identity[identity]
    	        if len(fl) != len(gl):
    		    if traceback:
    		        print("{}: Different numbers of {!r} {}s: {}, {}".format(
    			    self.__class__.__name__,
    			    identity,
                            fl[0].__class__.__name__,
    			    len(fl),
                            len(gl)))
                    return False
            #--- End: for

    	    # For each identity, check that there are matching pairs
            # of equal fields.
            for identity, fl in self_identity.iteritems():
    	        gl = other_identity[identity]

                for f in fl:
    		    found_match = False
                    for i, g in enumerate(gl):
                        if f.equals(g, rtol=rtol, atol=atol,
                                    ignore_fill_value=ignore_fill_value,
    				    ignore=ignore, traceback=False):
                            found_match = True
    		    	    del gl[i]
                            break
                #--- End: for
                
    		if not found_match:
    		    if traceback:                        
    			print("{}: No {} equal to: {!r}".format(
    			    self.__class__.__name__,
    			    g.__class__.__name__,
    			    f))
                    return False
	    #--- End: if

        #--- End: if

        # ------------------------------------------------------------
    	# Still here? Then the field lists are equal
    	# ------------------------------------------------------------
        return True	    
    #--- End: def

    def select(self, description=None, items=None, rank=None, ndim=None,
               exact=False, match_and=True, inverse=False):
        '''Return the fields that satisfy the given conditions.

Different types of conditions may be set with the parameters:
         
=============  =======================================================
Parameter      What gets tested
=============  =======================================================
*description*  Field properties and attributes
             
*items*        Field domain items
         
*rank*         The number of field domain axes

*ndim*         The number of field data array axes
=============  =======================================================

By default, when multiple criteria are given the field matches if it
satisfies the conditions given by each one.

If no fields satisfy the conditions then an empty `cf.FieldList` is
returned.

Note that ``fl.select(**kwargs)`` is equivalent to ``FieldList(g for g
in f if g.match(**kwargs))``

.. seealso:: `cf.Field.items`, `cf.Field.match`

**Quick start examples**

There is great flexibility in the types of test which can be
specified, and as a result the documentation is very detailed in
places. These preliminary, simple examples show that the usage need
not always be complicated and may help with understanding the keyword
descriptions.

1. Select fields which contain air temperature data, as given
   determined by the `identity` method:

   >>> fl.select('air_temperature')

2. Select fields which contain air temperature data, as given determined
   by the `identity` method, or have a long name which contains the
   string "temp":

   >>> fl.select(['air_temperature', {'long_name': cf.eq('.*temp.*', regex=true)}])

3. Select fields which have at least one longitude grid cell point on
   the Greenwich meridian:

   >>> fl.select(items={'longitude': 0})

4. Select fields which have at least one latitude grid cell of less
   than 1 degree in size:

   >>> fl.select(items={'latitude': cf.cellsize(cf.lt(1, 'degree'))})

5. Select fields which have exactly 4 domain axes:

   >>> fl.select(rank=4)

6. Examples 1 to 4 may be combined to select fields which have exactly
   4 domain axes, contain air temperature data, has at least one
   longitude grid cell point on the Greenwich meridian and have at
   least one latitude grid cells with a size of less than 1 degree:

   >>> fl.select('air_temperature',
   ...           items={'longitude': 0,
   ...                  'latitude': cf.cellsize(cf.lt(1, 'degree'))},
   ...           rank=4)

7. Select fields which contain at least one Gregorian calendar monthly
   mean data array value:

   >>> f.lselect({'cell_methods': cf.CellMethods('time: mean')},
   ...           items={'time': cf.cellsize(cf.wi(28, 31, 'days'))})

Further examples are given within and after the description of the
arguments.

:Parameters:

    description: *optional*
        Set conditions on the field's CF property and attribute
        values. *description* may be one, or a sequence of:

          * `None` or an empty dictionary. Always matches the
            field. This is the default.

     ..

          * A string which identifies string-valued metadata of the
            field and a value to compare it against. The value may
            take one of the following forms:

              ==============  ======================================
              *description*   Interpretation
              ==============  ======================================
              Contains ``:``  Selects on the CF property specified
                              before the first ``:``

              Contains ``%``  Selects on the attribute specified
                              before the first ``%``              
              
              Anything else   Selects on identity as returned by the
                              `identity` method
              ==============  ======================================

            By default the part of the string to be compared with the
            item is treated as a regular expression understood by the
            :py:obj:`re` module and the field matches if its
            appropriate value matches the regular expression using the
            :py:obj:`re.match` method (i.e. if zero or more characters
            at the beginning of field's value match the regular
            expression pattern). See the *exact* parameter for
            details.
            
              *Example:*
                To select a field with `identity` beginning with "lat":
                ``description='lat'``.

              *Example:*
                To select a field with long name beginning with "air":
                ``description='long_name:air'``.

              *Example:*
                To select a field with netCDF variable name of exactly
                "tas": ``description='ncvar%tas$'``.

              *Example:*
                To select a field with `identity` which ends with the
                letter "z": ``description='.*z$'``.

              *Example:*
                To select a field with long name which starts with the
                string ".*a": ``description='long_name%\.\*a'``. 

        ..

          * A `cf.Query` object to be compared with field's identity,
            as returned by its `identity` method.

              *Example:*
                To select a field with `identity` of exactly
                "air_temperature" you could set
                ``description=cf.eq('air_temperature')`` (see `cf.eq`).

              *Example:*
                To select a field with `identity` ending with
                "temperature" you could set
                ``description=cf.eq('.*temperature$', exact=False)`` (see
                `cf.eq`).

     ..

          * A dictionary which identifies properties of the field with
            corresponding tests on their values. The field matches if
            **all** of the tests in the dictionary are passed.

            In general, each dictionary key is a CF property name with
            a corresponding value to be compared against the field's
            CF property value. 

            If the dictionary value is a string then by default it is
            treated as a regular expression understood by the
            :py:obj:`re` module and the field matches if its
            appropriate value matches the regular expression using the
            :py:obj:`re.match` method (i.e. if zero or more characters
            at the beginning of field's value match the regular
            expression pattern). See the *exact* parameter for
            details.
            
              *Example:*
                To select a field with standard name of exactly
                "air_temperature" and long name beginning with the
                letter "a": ``description={'standard_name':
                cf.eq('air_temperature'), 'long_name': 'a'}`` (see
                `cf.eq`).

            Some key/value pairs have a special interpretation:

              ==================  ====================================
              Special key         Value
              ==================  ====================================
              ``'units'``         The value must be a string and by
                                  default is evaluated for
                                  equivalence, rather than equality,
                                  with the field's `units` property,
                                  for example a value of ``'Pa'``
                                  will match units of Pascals or
                                  hectopascals, etc. See the *exact*
                                  parameter.
                            
              ``'calendar'``      The value must be a string and by
                                  default is evaluated for
                                  equivalence, rather than equality,
                                  with the field's `calendar`
                                  property, for example a value of
                                  ``'noleap'`` will match a calendar
                                  of noleap or 365_day. See the
                                  *exact* parameter.
                              
              ``'cell_methods'``  The value must be a `cf.CellMethods`
                                  object containing *N* cell methods
                                  and by default is evaluated for
                                  equivalence with the last *N* cell
                                  methods contained within the field's
                                  `cell_methods` property. See the
                                  *exact* parameter.

              `None`              The value is interpreted as for a
                                  string value of the *description*
                                  parameter. For example,
                                  ``description={None: 'air'}`` is
                                  equivalent to ``description='air'`` 
                                  and ``description={None:
                                  'ncvar%pressure'}`` is equivalent to
                                  ``description='ncvar%pressure'``.
              ==================  ====================================
            
              *Example:*
                To select a field with standard name starting with
                "air", units of temperature and a netCDF variable name
                beginning with "tas" you could set
                ``description={'standard_name': 'air', 'units': 'K',
                None: 'ncvar%tas'}``.

              *Example:*
                To select a field whose last two cell methods are
                equivalent to "time: minimum area: mean":
                ``description={'cell_methods': cf.Cellmethods('time:
                minimum area: mean')``. This would select a field
                which has, for example, cell methods of "height: mean
                time: minimum area: mean".

        If *description* is a sequence of any combination of the above then
        the field matches if it matches **at least one** element of
        the sequence:

          *Example:* 

            >>> f.select('air_temperature')
            <CF Field: air_temperature(latitude(73), longitude(96) K>
            >>> f.select({'units': 'hPa'})
            []
            >>> f.select(['air_temperature', {'units': 'hPa'])
            <CF Field: air_temperature(latitude(73), longitude(96) K>
              
        If the sequence is empty then the field always matches.
 
    items: `dict`, optional
        A dictionary which identifies domain items of the field
        (dimension coordinate, auxiliary coordinate, cell measure or
        coordinate reference objects) with corresponding tests on
        their elements. The field matches if **all** of the specified
        items exist and their tests are passed.

        Each dictionary key specifies an item to test as the one that
        would be returned by this call of the field's `item` method:
        ``f.item(key, exact=exact)`` (see `cf.Field.item`).

        The corresponding value is, in general, any object for which
        the item may be compared with for equality (``==``). The test
        is passed if the result evaluates to True, or if the result is
        an array of values then the test is passed if at least one
        element evaluates to true.

        If the value is `None` then the test is always passed,
        i.e. this case tests for item existence.

          *Example:*
             To select a field which has a latitude coordinate value of
             exactly 30: ``items={'latitude': 30}``.

          *Example:*
             To select a field whose longitude axis spans the Greenwich
             meridian: ``items={'longitude': cf.contain(0)}`` (see
             `cf.contain`).

          *Example:*
             To select a field which has a time coordinate value of
             2004-06-01: ``items={'time': cf.dt('2004-06-01')}`` (see
            `cf.dt`).

          *Example:*
             To select a field which has a height axis: ``items={'Z':
             None}``.

          *Example:*
             To select a field which has a time axis and depth
             coordinates greater then 1000 metres: ``items={'T': None,
             'depth': cf.gt(1000, 'm')}`` (see `cf.gt`).

          *Example:*
            To select a field with time coordinates after than 1989 and
            cell sizes of between 28 and 31 days: ``items={'time':
            cf.dtge(1990) & cf.cellsize(cf.wi(28, 31, 'days'))}`` (see
            `cf.dtge`, `cf.cellsize` and `cf.wi`).

    rank: *optional*
        Specify a condition on the number of axes in the field's
        domain. The field matches if its number of domain axes equals
        *rank*. A range of values may be selected if *rank* is a
        `cf.Query` object. Not to be confused with the *ndim*
        parameter (the number of data array axes may be fewer than the
        number of domain axes).

          *Example:*
            ``rank=2`` selects a field with exactly two domain axes
            and ``rank=cf.wi(3, 4)`` selects a field with three or
            four domain axes (see `cf.wi`).

    ndim: *optional*
        Specify a condition on the number of axes in the field's data
        array. The field matches if its number of data array axes
        equals *ndim*. A range of values may be selected if *ndim* is
        a `cf.Query` object. Not to be confused with the *rank*
        parameter (the number of domain axes may be greater than the
        number of data array axes).

          *Example:*
            ``ndim=2`` selects a field with exactly two data array
            axes and ``ndim=cf.le(2)`` selects a field with fewer than
            three data array axes (see `cf.le`).

    exact: `bool`, optional
        The *exact* parameter applies to the interpretation of string
        values of the *description* parameter and of keys of the *items*
        parameter. By default *exact* is False, which means that:

          * A string value is treated as a regular expression
            understood by the :py:obj:`re` module. 

          * Units and calendar values in a *description* dictionary are
            evaluated for equivalence rather then equality
            (e.g. "metre" is equivalent to "m" and to "km").

          * A cell methods value containing *N* cell methods in a
            *description* dictionary is evaluated for equivalence with the
            last *N* cell methods contained within the field's
            `cell_methods` property.

        ..

          *Example:*
            To select a field with a standard name which begins with
            "air" and any units of pressure:
            ``f.select({'standard_name': 'air', 'units': 'hPa'})``.

          *Example:*          
            ``f.select({'cell_methods': cf.CellMethods('time: mean
            (interval 1 hour)')})`` would select a field with cell
            methods of "area: mean time: mean (interval 60 minutes)".

        If *exact* is True then:

          * A string value is not treated as a regular expression.

          * Units and calendar values in a *description* dictionary are
            evaluated for exact equality rather than equivalence
            (e.g. "metre" is equal to "m", but not to "km").

          * A cell methods value in a *description* dictionary is evaluated
            for exact equality to the field's cell methods.
          
        ..

          *Example:*          
            To select a field with a standard name of exactly
            "air_pressure" and units of exactly hectopascals:
            ``f.select({'standard_name': 'air_pressure', 'units':
            'hPa'}, exact=True)``.

          *Example:*          
            To select a field with a cell methods of exactly "time:
            mean (interval 1 hour)": ``f.select({'cell_methods':
            cf.CellMethods('time: mean (interval 1 hour)')``.

        Note that `cf.Query` objects provide a mechanism for
        overriding the *exact* parameter for individual values.

          *Example:*
            ``f.select({'standard_name': cf.eq('air', exact=False),
            'units': 'hPa'}, exact=True)`` will select a field with a
            standard name which begins "air" but has units of exactly
            hectopascals (see `cf.eq`).
    
          *Example:*
            ``f.select({'standard_name': cf.eq('air_pressure'),
            'units': 'hPa'})`` will select a field with a standard name
            of exactly "air_pressure" but with units which equivalent
            to hectopascals (see `cf.eq`).


    match_and: `bool`, optional
        By default *match_and* is True and the field matches if it
        satisfies the conditions specified by each test parameter
        (*description*, *items*, *rank* and *ndim*).

        If *match_and* is False then the field will match if it
        satisfies at least one test parameter's condition.

          *Example:*
            To select a field with a standard name of "air_temperature"
            **and** 3 data array axes: ``f.select('air_temperature',
            ndim=3)``. To select a field with a standard name of
            "air_temperature" **or** 3 data array axes:
            ``f.select('air_temperature", ndim=3, match_and=False)``.
    
    inverse: `bool`, optional
        If True then return the field matches if it does **not**
        satisfy the given conditions.

          *Example:*
          
            >>> len(f.select('air', ndim=4, inverse=True)) == len(f) - len(f.select('air', ndim=4))
            True

:Returns:

    out: `cf.FieldList`
        A `cf.FieldList` of the matching fields.

:Examples:

Field identity starts with "air":

>>> fl.select('air')

Field identity ends contains the string "temperature":

>>> fl.select('.*temperature')

Field identity is exactly "air_temperature":

>>> fl.select('^air_temperature$')
>>> fl.select('air_temperature', exact=True)

Field has units of temperature:

>>> fl.select({'units': 'K'}):

Field has units of exactly Kelvin:

>>> fl.select({'units': 'K'}, exact=True)

Field identity which starts with "air" and has units of temperature:

>>> fl.select({None: 'air', 'units': 'K'})

Field identity starts with "air" and/or has units of temperature:

>>> fl.select(['air', {'units': 'K'}])

Field standard name starts with "air" and/or has units of exactly Kelvin:

>>> fl.select([{'standard_name': cf.eq('air', exact=False), {'units': 'K'}],
...           exact=True)

Field has height coordinate values greater than 63km:

>>> fl.select(items={'height': cf.gt(63, 'km')})

Field has a height coordinate object with some values greater than
63km and a north polar point on its horizontal grid:

>>> fl.select(items={'height': cf.gt(63, 'km'),
...                  'latitude': cf.eq(90, 'degrees')})

Field has some longitude cell sizes of 3.75:

>>> fl.select(items={'longitude': cf.cellsize(3.75)})

Field latitude cell sizes within a tropical region are all no greater
than 1 degree:

>>> fl.select(items={'latitude': (cf.wi(-30, 30, 'degrees') &
...                               cf.cellsize(cf.le(1, 'degrees')))})

Field contains monthly mean air pressure data and all vertical levels
within the bottom 100 metres of the atmosphere have a thickness of 20
metres or less:

>>> fl.select({None: '^air_pressure$', 'cell_methods': cf.CellMethods('time: mean')},
...           items={'height': cf.le(100, 'm') & cf.cellsize(cf.le(20, 'm')),
...                  'time': cf.cellsize(cf.wi(28, 31, 'days'))})

        '''
        kwargs2 = self._parameters(locals())

        return type(self)(f for f in self if f.match(**kwargs2))
    #--- End: def

    def select_field(self, description=None, items=None, rank=None,
                     ndim=None, exact=False, match_and=True,
                     inverse=False):
        '''Return the  unique field that satisfies the given conditions.

``fl.select_field(**kwargs)`` is equivalent to
``fl.select(**kwargs)[0]`` with an exception being raised if the
`select` call returns a field list containing zero or two or more
fields.

.. versionadded:: 2.0.3

.. seealso:: `select`, `cf.Field.items`, `cf.Field.match`

:Returns:

    out: `cf.Field`
        The unique matching field.

'''
        kwargs2 = self._parameters(locals())

        out = [f for f in self if f.match(**kwargs2)]
        if len(out) == 1:
            return out[0]

        raise ValueError(
            "Error whilst selecting a unique field: {} fields found".format(len(out)))
    #--- End: def



    def select1(self, description=None, items=None, rank=None, ndim=None,
                exact=False, match_and=True, inverse=False):

        '''Return the  unique field that satisfies the given conditions.

``fl.select1(**kwargs)`` is equivalent to ``fl.select(**kwargs)[0]``
with an exception being raised if the `select` call returns a field
list containing zero or two or more fields.

.. versionadded:: 2.0.2

.. seealso:: `select`, `cf.Field.items`, `cf.Field.match`

:Returns:

    out: `cf.Field`
        The unique matching field.

        '''
        
        print "WARNING: Use select_field in favour of select1. select1 will be deprecated a later version"
        kwargs2 = self._parameters(locals())
        return self.select_field(**kwargs2)
    #--- End: def

    def set_equals(self, other, rtol=None, atol=None, ignore_fill_value=False, 
                   traceback=False, ignore=('Conventions',)):
        '''set equals
        '''
        kwargs2 = self._parameters(locals())
        kwargs2['_set'] = True
        
        return self.equals(**kwargs2)
    #---End: def

#--- End: class

class Items(dict):
    '''
Keys are item identifiers, values are item objects.
    '''
    
    # Mapping of role name to single-character id (DO NOT CHANGE)
    _role_name = {
        'f': 'field ancillary',
        'a': 'auxiliary coordinate',
        'c': 'domain ancillary',
        'd': 'dimension coordinate',
        'm': 'cell measure',
        'r': 'coordinate reference',
    }

    def __init__(self):
        '''
'''
        self.f = set()  # Field ancillary identifiers,      e.g. 'fav0'
        self.a = set()  # Auxiliary coordinate identifiers, e.g. 'aux0'
        self.c = set()  # Domain ancillary identifiers,     e.g. 'cct0'
        self.d = set()  # Dimension coordinate identifiers, e.g. 'dim0'
        self.m = set()  # Cell measures identifier,         e.g. 'msr0'
        self.r = set()  # Coordinate reference identifiers, e.g. 'ref0'

        # Map of item identifiers to their roles. For example,
        # self._role['aux2'] = 'a'
        self._role = {}

        # The axes identifiers for each item. For example,
        # self._role['aux2'] = ['dim1, 'dim0']
        self._axes = {}

        # Domain axis objects. For example: self.Axes['dim1'] = cf.DomainAxis(20)
        self.Axes = Axes()
        
        self.cell_methods = CellMethods()
    #--- End: def

    def __call__(self, description=None, role=None, axes=None,
                 axes_all=None, axes_subset=None, axes_superset=None,
                 ndim=None, match_and=True, exact=False,
                 inverse=False, copy=False):#, _restrict_inverse=False):
        '''Return items which span domain axes.

The set of all items comprises:

  * Dimension coordinate objects
  * Auxiliary coordinate objects
  * Cell measure objects
  * Coordinate reference objects
  * Coordinate conversion terms
  * Ancillary variable objects

The output is a dictionary whose key/value pairs are item identifiers
with corresponding values of items of the field.

{+item_selection}

{+items_criteria}

.. seealso:: `auxs`, `axes`, `measures`, `coords`, `dims`, `item`, `match`
             `remove_items`, `refs`

:Examples 1:

Select all items whose identities (as returned by their `!identity`
methods) start "height":

>>> i('height')

Select all items which span only one axis:

>>> i(ndim=1)

Select all cell measure objects:

>>> i(role='m')

Select all items which span the "time" axis:

>>> i(axes='time')

Select all CF latitude coordinate objects:

>>> i('Y')

Select all multidimensional dimension and auxiliary coordinate objects
which span at least the "time" and/or "height" axes and whose long
names contain the string "qwerty":

>>> i('long_name:.*qwerty', 
...         role='da',
...         axes=['time', 'height'],
...         ndim=cf.ge(2))

:Parameters:

    {+description}

          *Example:* 

            >>> x = i(['aux1',
            ...             'time',
            ...             {'units': 'degreeN', 'long_name': 'foo'}])
            >>> y = {}
            >>> for items in ['aux1', 'time', {'units': 'degreeN', 'long_name': 'foo'}]:
            ...     y.update(i(items))
            ...
            >>> set(x) == set(y)
            True

    role: (sequence of) `str`, optional
        Select items of the given roles. Valid roles are:
    
        =======  ============================
        role     Items selected
        =======  ============================
        ``'d'``  Dimension coordinate objects
        ``'a'``  Auxiliary coordinate objects
        ``'m'``  Cell measure objects
        ``'c'``  Domain ancillary objects
        ``'f'``  Field ancillary objects
        ``'r'``  Coordinate reference objects
        =======  ============================
    
        Multiple roles may be specified by a sequence of role
        identifiers.
    
          *Example:*
            Selecting auxiliary coordinate and cell measure objects
            may be done with any of the following values of *role*:
            ``'am'``, ``'ma'``, ``('a', 'm')``, ``['m', 'a']``,
            ``set(['a', 'm'])``, etc.
 
        By default all roles are considered, i.e. by default
        ``role=('d', 'a', 'm', 'f', 'c', 'r')``.
    
    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

          *Example:*
            ``i(role='da', inverse=True)`` selects the same
            items as ``i(role='mr')``.

    {+copy}

:Returns:

    out: `dict`
        A dictionary whose keys are domain item identifiers with
        corresponding values of items. The dictionary may be empty.

:Examples:

        '''
        if role is None:
            pool = dict(self)
        else:
            pool = {}
            for r in role:
                for key in getattr(self, r):
                    pool[key] = self[key]
                    
        if inverse:
            master = pool.copy()            

#        if inverse:  
#            if not _restrict_inverse or role is None:
#                master = pool.copy()
#            else:
#                master = {}
#                if _restrict_inverse:
#                    for r in _restrict_inverse:
#                        for key in getattr(self, r):
#                            master[key] = pool[key]
#                else:
#                    for r in role:
#                        for key in getattr(self, r):
#                            master[key] = pool[key]
#
#        #--- End: if

        if (description is None and axes is None and axes_all is None and
            axes_subset is None and axes_superset is None and ndim is None):
            out = pool.copy()
        else:       
            out = {}

#        if pool and role is not None:
#            # --------------------------------------------------------
#            # Select items which have a given role
#            # --------------------------------------------------------
#            out = {}
#            for r in role:        
#                for key in getattr(self, r):
#                    out[key] = self[key]
#
#            if match_and:
#                pool = out
#            else:
#                for key in out:
#                    del pool[key]
#        #--- End: if

        if pool and axes is not None:
            # --------------------------------------------------------
            # Select items which span at least one of the given axes,
            # and possibly others.
            # --------------------------------------------------------
            axes_out = {}
            for key, value in pool.iteritems():
                if axes.intersection(self.axes(key)):
                    axes_out[key] = value

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and axes_subset is not None:
            # --------------------------------------------------------
            # Select items whose data array spans all of the specified
            # axes, taken in any order, and possibly others.
            # --------------------------------------------------------
            axes_out = {}
            for key, value in pool.iteritems():
                if axes_subset.issubset(self.axes(key)):
                    axes_out[key] = value                            

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and axes_superset is not None:
            # --------------------------------------------------------
            # Select items whose data array spans a subset of the
            # specified axes, taken in any order, and no others.
            # --------------------------------------------------------
            axes_out = {}
            for key, value in pool.iteritems():
                if axes_superset.issuperset(self.axes(key)):
                    axes_out[key] = value                            

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and axes_all is not None:
            # --------------------------------------------------------
            # Select items which span all of the given axes and no
            # others
            # --------------------------------------------------------
            axes_out = {}
            for key, value in pool.iteritems():
                if axes_all == set(self.axes(key)):
                    axes_out[key] = value                            

            if match_and:
                out = pool = axes_out
            else:                
                for key in axes_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and ndim is not None:
            # --------------------------------------------------------
            # Select items whose number of data array axes satisfies a
            # condition
            # --------------------------------------------------------
            ndim_out = {}
            for key, item in pool.iteritems():
                if ndim == len(self.axes(key)):
                    ndim_out[key] = item
            #--- End: for

            if match_and:                
                out = pool = ndim_out
            else:
                for key in ndim_out:
                    out[key] = pool.pop(key)
        #--- End: if

        if pool and description is not None:
            # --------------------------------------------------------
            # Select items whose properties satisfy conditions
            # --------------------------------------------------------
            items_out = {}

            if isinstance(description, (basestring, dict, Query)):
                description = (description,)

            if description:
                pool2 = pool.copy()

                match = []
                for m in description:
                    if m.__hash__ and m in pool:
                        # m is an item identifier
                        items_out[m] = pool2.pop(m)
                    else:                    
                        match.append(m)
                #--- End: for

                if match and pool:                
                    for key, item in pool2.iteritems():
                        if item.match(match, exact=exact):
                            # This item matches the critieria
                            items_out[key] = item
                #--- End: if

                if match_and:                
                    out = pool = items_out
                else:
                    for key in items_out:
                        out[key] = pool.pop(key)
            #--- End: if
        #--- End: if

        if inverse:
            # --------------------------------------------------------
            # Select items other than those previously selected
            # --------------------------------------------------------
            for key in out:
                del master[key]
                                
            out = master
        #--- End: if

        if copy:
            # --------------------------------------------------------
            # Copy the items
            # --------------------------------------------------------
            out2 = {}
            for key, item in out.iteritems():
                out2[key] = item.copy()
                
            out = out2
        #--- End: if

        # ------------------------------------------------------------
        # Return the selected items
        # ------------------------------------------------------------
        return out
    #--- End: def

    def auxs(self):
        '''Auxiliary coordinate objects and their identifiers
        
:Returns:
        
    out: `dict`
          A dictionary of auxiliary coordinate objects keyed by their
          identifiers.

:Examples:

>>> i.auxs()
{'aux0': <CF AuxiliaryCorodinate: >}

        '''
        return dict([(key, self[key]) for key in self.a])

    def dims(self):
        '''Return dimension coordinate objects and their identifiers
        
:Returns:
        
    out: `dict`
          A dictionary of dimension coordinate objects keyed by their
          identifiers.

:Examples:

>>> i.dims()
{'dim0': <CF DimensionCoordinate: >}

        '''
        return dict([(key, self[key]) for key in self.d])
 
    def direction(self, axis):
        '''

Return True if an axis is increasing, otherwise return False.

An axis is considered to be increasing if its dimension coordinate
values are increasing in index space or if it has no dimension
coordinates.

:Parameters:

    axis: `str`
        A domain axis identifier, such as ``'dim0'``.

:Returns:

    out: `bool`
        Whether or not the axis is increasing.
        
:Examples:

>>> i.direction('dim0')
True
>>> i.direction('dim2')
False
        '''
        if axis not in self.d:
            return True

        return self[axis].direction()
    #--- End: def
        
    def domain_ancs(self):
        '''Return domain ancillary objects and their identifiers

:Returns:
        
    out: `dict`
        A dictionary of domain ancillary objects keyed by their
        identifiers.

:Examples:

>>> i.domain_ancs()
{'cct0': <CF DomainAncillary: >}

        '''
        return dict([(key, self[key]) for key in self.c])
        
    def field_ancs(self):
        '''Return field ancillary objects and their identifiers
        
:Returns:
        
    out: `dict`
          A dictionary of field ancillary objects keyed by their
          identifiers.

:Examples:

>>> i.field_ancs()
{'fav0': <CF FieldAncillary: >}

        '''
        return dict([(key, self[key]) for key in self.f])

    def msrs(self):
        '''Return cell measure objects and their identifiers
        
:Returns:
        
    out: `dict`
          A dictionary of cell measure objects keyed by their
          identifiers.

:Examples:

>>> i.msrs()
{'msr0': <CF CellMeasures: >}

        '''        
        return dict([(key, self[key]) for key in self.m])
        
    def refs(self):
        '''Return coordinate reference objects and their identifiers
        
:Returns:
        
    out: `dict`
          A dictionary of coordinate reference objects keyed by their
          identifiers.

:Examples:

>>> i.refs()
{'ref0': <CF CoordinateReference: >}

        '''  
        return dict([(key, self[key]) for key in self.r])

    def all_axes(self):
        '''
        '''        
        out = []
        for item_axes  in self._axes.itervalues():
            out.extend(item_axes)

        return set(out)

    def axes(self, key=None, axes=None, default=None):
        '''
:Examples 1:

>>> i.axes()

:Parameters:

    key: `str`, optional

    axes: sequence of `str`, optional

    default:

:Returns:

    out: `dict` or `list` or `None`

:Examples 2:

i.axes()
{'aux0': ('dim1', 'dim0'),
 'aux1': ('dim0',),
 'aux2': ('dim0',),
 'aux3': ('dim0',),
 'aux4': ('dim0',),
 'aux5': ('dim0',)}
>>>i.axes(key='aux0')
('dim1', 'dim0')
>>> print i.axes(key='aux0', axes=['dim0', 'dim1'])
None
>>> i.axes(key='aux0')
('dim0', 'dim1')

'''
        if key is None:
            # Return all of the items' axes
            return self._axes.copy()

        if axes is None:
            if self.role(key) != 'r':                            
                # Not a coordinate reference
                return self._axes.get(key, default)
            else:
                # Is a coordinate reference
                r_axes = []
                ref = self.get(key, None)
                
                if ref is None:
                    return default

                _axes = self._axes
                for key in self(ref.coordinates | set(ref.ancillaries.values()),
                                exact=True):
                    r_axes.extend(_axes.get(key, ()))
                
                return set(r_axes)

        elif self.role(key) == 'r':
            raise ValueError("Can't set coordinate reference axes")
 
        # Still here? The set new item axes.
        self._axes[key] = tuple(axes)
    #--- End: def
    
    def axes_to_items(self):
        '''
:Examples:

>>> i.axes_to_items()
{
 ('dim1',): {
        'd': {'dim1': <>},
        'a': {},
        'm': {}
        'c': {}
        'f': {}
        }
 ('dim1', 'dim2',): {
        'd': {},
        'a': {'aux0': <>, 'aux1': <>},
        'm': {}
        'c': {}
        'f': {}
        }
}
'''
        axes = self._axes
        out = {}

        for item_axes in axes.values():
            out[item_axes] = {}
                
        for role in ('d', 'a', 'm', 'c', 'f'):
            for item_axes, items in out.iteritems():
                items_role = {}
                for key in getattr(self, role):
                    if axes[key] == item_axes:
                        items_role[key] = self[key]
                items[role] = items_role
        return out
    #--- End: def

    def axis_name(self, axis, default=None):
        '''Return the canonical name for an axis.

:Parameters:

:Returns:

    out: `str`
        The canonical name for the axis.

:Examples:

        '''
        if default is None:
            default = 'axis%{}'.format(axis)

        if axis in self.d:
            # Get the name from the dimension coordinate
            return self[axis].name(default=default)

        aux = self.item(role='a', axes_all=set((axis,)))
        if aux is not None:
            # Get the name from the unique 1-d auxiliary coordinate
            return aux.name(default=default)
        
        ncdim = self.Axes[axis].ncdim
        if ncdim is not None:
            # Get the name from netCDF dimension name            
            return 'ncdim%{0}'.format(ncdim)
        else:
            # Get the name from the axis identifier
            return 'axis%{0}'.format(axis)
    #--- End: def

    def axis_identity(self, axis):
        '''Return the canonical name for an axis.

:Parameters:

:Returns:

    out: `str`
        The canonical name for the axis.

:Examples:

        '''      
        if axis in self.d:
            # Get the name from the dimension coordinate
            dim = self[axis]            
            identity = dim.identity()
            if identity is None:
                for ctype in ('T', 'X', 'Y', 'Z'):
                    if getattr(dim, ctype):
                        identity = ctype
                        break
            #--- End: if
            if identity is None:
                identity = 'axis%{0}'.format(axis)
        else:
            aux = self.item(role='a', axes_all=set((axis,)))
            if aux is not None:
                # Get the name from the unique 1-d auxiliary coordinate
                identity = aux.identity(default='axis%{0}'.format(axis))
            else:
                identity = 'axis%{0}'.format(axis)

        return identity
    #--- End: def
            #--- End: if

    def close(self):
        '''
Close all files referenced by all of the items.

Note that a closed file will be automatically reopened if its contents
are subsequently required.

:Examples 1:

>>> i.close()

:Returns:

    `None`

'''
        for item in self.itervalues():
            item.close()
    #--- End: def

    def copy(self, shallow=False):
        '''

Return a deep or shallow copy.

``i.copy()`` is equivalent to ``copy.deepcopy(i)``.

``i.copy(shallow=True)`` is equivalent to ``copy.copy(i)``.

:Parameters:

    shallow: `bool`, optional

:Returns:

    out: `Items`
        The copy.

:Examples:

>>> i = j.copy()

'''
        X = type(self)
        new = X.__new__(X)

        # Copy the domain axes
        new.Axes = self.Axes.copy()
        
        # Copy the actual items (e.g. dimension coordinates, field
        # ancillaries, etc.)
        if shallow:
            for key, value in self.iteritems():
                new[key] = value
        else:
            for key, value in self.iteritems():
                new[key] = value.copy()

        # Copy the item axes
#        axes = {}
#        for key, value in self._axes.iteritems():
#            axes[key] = value[:]
#        new._axes = axes
        
        # Copy the identifiers
        new.f = self.f.copy()     # Field ancillaries
        new.a = self.a.copy()     # Auxiliary coordinates
        new.c = self.c.copy()     # Domain ancillaries
        new.d = self.d.copy()     # Dimension coordinates
        new.m = self.m.copy()     # Cell measures
        new.r = self.r.copy()     # Coordinate references

        # Copy the roles
        new._role = self._role.copy()

        new.cell_methods = self.cell_methods.copy()

        # Copy item axes (this is OK because it is a dictionary of
        # tuples).
        new._axes = self._axes.copy()

        return new
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False,
               _equivalent=False, ignore=()):
        '''

'''
        if self is other:
            return True
        
        # Check that each instance is the same type
        if type(self) != type(other):
            if traceback:
                print("{0}: Different object types: {0}, {1}".format(
                    self.__class__.__name__, other.__class__.__name__))
            return False

        if not self.Axes.equals(other.Axes, traceback=traceback):
            if traceback:
                print("{0}: Different domain axes: {1}, {2}".format(
                    self.__class__.__name__, self.Axes, other.Axes))
            return False
            
        
        if rtol is None:
            rtol = RTOL()
        if atol is None:
            atol = ATOL()

        # ------------------------------------------------------------
        # 
        # ------------------------------------------------------------
        axes0_to_axes1 = {}

        key1_to_key0 = {}

        axes_to_items0 = self.axes_to_items()
        axes_to_items1 = other.axes_to_items()

        for axes0, items0 in axes_to_items0.iteritems():
            matched_all_items_with_these_axes = False

            directions0 = [self.direction(axis0) for axis0 in axes0]

            len_axes0 = len(axes0) 
            for axes1, items1 in axes_to_items1.items():
                matched_roles = False

                if len_axes0 != len(axes1):
                    # axes1 and axes0 contain differents number of
                    # axes.
                    continue
            
                directions1 = [other.direction(axis1) for axis1 in axes1]        

                for role in ('d', 'a', 'm', 'f', 'c'):
                    matched_role = False

                    role_items0 = items0[role]
                    role_items1 = items1[role]

                    if len(role_items0) != len(role_items1):
                        # There are the different numbers of items
                        # with this role
                        matched_all_items_with_these_axes = False
                        break

                    # Check that there are matching pairs of equal
                    # items
                    for key0, item0 in role_items0.iteritems():
                        matched_item = False
                        for key1, item1 in role_items1.items():
                            if _equivalent:
#                                # Flip item1 axes, if necessary
#                                flip = [i
#                                        for i, (d0, d1) in enumerate(zip(directions0, directions1))
#                                        if d0 != d1]
#                                if flip:
#                                    item1 = item1.flip(flip)
#
#                                # Transpose item1 axes, if necessary
#                                
#
#                                item0.compare = item0.equivalent
                                pass
                            else:
                                item0_compare = item0.equals
                               
                            if item0_compare(item1, rtol=rtol, atol=atol,
                                             ignore_fill_value=ignore_fill_value,
                                             ignore=ignore, traceback=False):
                                del role_items1[key1]
                                key1_to_key0[key1] = key0
                                matched_item = True
                                break
                        #--- End: for

                        if not matched_item:
                            break
                    #--- End: for

                    if role_items1:
                        break

                    del items1[role]
                #--- End: for

                matched_all_items_with_these_axes = not items1

                if matched_all_items_with_these_axes:
                    del axes_to_items1[axes1]
                    break
            #--- End: for

            if not matched_all_items_with_these_axes:
                if traceback:
                    names = [self.axis_name(axis0) for axis0 in axes0]
                    print("Can't match items spanning {} axes".format(names))
                return False

            # Map item axes in the two instances
            axes0_to_axes1[axes0] = axes1
        #--- End: for

        axis0_to_axis1 = {}
        axis1_to_axis0 = {}
        for axes0, axes1 in axes0_to_axes1.iteritems():
            for axis0, axis1 in zip(axes0, axes1):
                if axis0 in axis0_to_axis1 and axis1 != axis0_to_axis1[axis0]:
                    if traceback:
                        print(
"Field: Ambiguous axis mapping ({} -> {} and {})".format(
    self.axis_name(axes0), other.axis_name(axis1),
    other.axis_name(axis0_to_axis1[axis0])))
                    return False
                elif axis1 in axis1_to_axis0 and axis0 != axis1_to_axis0[axis1]:
                    if traceback:
                        print(
"Field: Ambiguous axis mapping ({} -> {} and {})".format(
    self.axis_name(axis0), self.axis_name(axis1_to_axis0[axis0]),
    other.axis_name(axes1)))
                    return False

                axis0_to_axis1[axis0] = axis1
                axis1_to_axis0[axis1] = axis0
        #--- End: for     

        #-------------------------------------------------------------
        # Cell methods
        #-------------------------------------------------------------
        if len(self.cell_methods) != len(other.cell_methods):
            if traceback:
                print(
"Field: Different cell methods: {0!r}, {1!r}".format(
    self.cell_methods, other.cell_methods))
            return False

        for cm0, cm1 in zip(self.cell_methods, other.cell_methods):
            # Check that there are the same number of axes
            axes0 = cm0.axes
            axes1 = list(cm1.axes)
            if len(cm0.axes) != len(axes1):
                if traceback:
                    print (
"Field: Different cell methods (mismatched axes): {0!r}, {1!r}".format(
    self.cell_methods, other.cell_methods))
                return False

            argsort = []
            for axis0 in axes0:
                if axis0 is None:
                    return False
                for axis1 in axes1:
                    if axis0 in axis0_to_axis1 and axis1 in axis1_to_axis0:
                        if axis1 == axis0_to_axis1[axis0]:
                            axes1.remove(axis1)
                            argsort.append(cm1.axes.index(axis1))
                            break
                    elif axis0 in axis0_to_axis1 or axis1 in axis1_to_axis0:
                        print axis0, axis1
                        if traceback:
                            print (
"Field: Different cell methods (mismatched axes): {0!r}, {1!r}".format(
    self.cell_methods, other.cell_methods))

                        return False
                    elif axis0 == axis1:
                        axes1.remove(axis1)
                        argsort.append(cm1.axes.index(axis1))
                    elif axis1 is None:
                        if traceback:
                            print (
"Field: Different cell methods (undefined axis): {0!r}, {1!r}".format(
    self.cell_methods, other.cell_methods))
                        return False
            #--- End: for

            if len(cm1.axes) != len(argsort):
                if traceback:
                    print (
"Field: Different cell methods: {0!r}, {1!r}".format(
    self.cell_methods, other.cell_methods))
                return False

            cm1.sort(argsort=argsort)
            cm1.axes = axes0

            if not cm0.equals(cm1, atol=atol, rtol=rtol,
                              ignore_fill_value=ignore_fill_value,
                              traceback=traceback):
                if traceback:
                    print (
"Field: Different cell methods: {0!r}, {1!r}".format(
    self.cell_methods, other.cell_methods))
                return False                
        #--- End: for

        # ------------------------------------------------------------
        # Coordinate references
        # ------------------------------------------------------------
        refs1 = other.refs()
        for ref0 in self.refs().values():
            found_match = False
            for key1, ref1 in refs1.items():
                if not ref0.equals(ref1, rtol=rtol, atol=atol,
                                   ignore_fill_value=ignore_fill_value, traceback=False):
                    continue

                # Coordinates
                coordinates0 = set(
                    [self.key(value, role='da', exact=True, default=value)
                     for value in ref0.coordinates])
                coordinates1 = set(
                    [key1_to_key0.get(other.key(value, role='da', exact=True), value)
                     for value in ref1.coordinates])
                if coordinates0 != coordinates1:
                    continue

                # Domain ancillary terms
                terms0 = dict(
                    [(term,
                      self.key(value, role='c', exact=True, default=value))
                     for term, value in ref0.ancillaries.iteritems()])
                terms1 = dict(
                    [(term,
                      key1_to_key0.get(other.key(value, role='c', exact=True), value))
                     for term, value in ref1.ancillaries.iteritems()])
                if terms0 != terms1:
                    continue

                found_match = True
                del refs1[key1]                                       
                break
            #--- End: for

            if not found_match:
                if traceback:
                    print("Field: No match for {0!r})".format(ref0))
                return False
        #--- End: for

        # ------------------------------------------------------------
        # Still here? Then the two Items are equal
        # ------------------------------------------------------------
        return True
    #--- End: def

    def analyse_axis(self, axis):
        '''
        '''
        if axis in self.d:
            # This axis of the domain has a dimension coordinate
            dim = self[axis]

            identity = dim.identity()
            if identity is None:
                # Dimension coordinate has no identity, but it may
                # have a recognised axis.
                for ctype in ('T', 'X', 'Y', 'Z'):
                    if getattr(dim, ctype):
                        identity = ctype
                        break
            #--- End: if

            if identity is not None and dim._hasData:
                axis_to_id[axis]      = identity
                id_to_axis[identity]  = axis
                axis_to_coord[axis]   = key
                id_to_coord[identity] = key
                axis_to_dim[axis]     = key
                id_to_dim[identity]   = key
        else:
            auxs = self(role='a', ndim=1)
            if len(auxs) == 1:                
                # This axis of the domain does not have a
                # dimension coordinate but it does have exactly
                # one 1-d auxiliary coordinate, so that will do.
                key, aux = auxs.popitem()
                identity = aux.identity()
                if identity is None:
                    # Auxiliary coordinate has no identity, but it may
                    # have a recognised axis.
                    for ctype in ('T', 'X', 'Y', 'Z'):
                        if getattr(dim, ctype):
                            identity = ctype
                            break
                #--- End: if

                if identity is not None and aux._hasData:                
                    axis_to_id[axis]      = identity
                    id_to_axis[identity]  = axis
                    axis_to_coord[axis]   = key
                    id_to_coord[identity] = key
                    axis_to_aux[axis]     = key
                    id_to_aux[identity]   = key
    #--- End: def

    def insert_field_anc(self, item, key, axes, copy=True):
        if copy:
            item = item.copy()
        self[key] = item
        self._axes[key] = tuple(axes)
        self.f.add(key)
        self._role[key] = 'f'
        
    def insert_aux(self, item, key, axes, copy=True):
        '''
        '''
        if copy:
            item = item.copy()
        self[key] = item
        self._axes[key] = tuple(axes)
        self.a.add(key)
        self._role[key] = 'a'

    def insert_domain_anc(self, item, key, axes, copy=True):
        '''
        '''
        if copy:
            item = item.copy()
        self[key] = item
        self._axes[key] = tuple(axes)
        self.c.add(key)
        self._role[key] = 'c'

    def insert_dim(self, item, key, axes, copy=True):
        '''
        '''
        if copy:
            item = item.copy()
        self[key] = item
        self._axes[key] = tuple(axes)
        self.d.add(key)
        self._role[key] = 'd'

    def insert_measure(self, item, key, axes, copy=True):
        '''
        '''
        if copy:
            item = item.copy()
        self[key] = item
        self._axes[key] = tuple(axes)
        self.m.add(key)
        self._role[key] = 'm'

    def insert_ref(self, item, key, copy=True):
        if copy:
            item = item.copy()
        self[key] = item
        self.r.add(key)
        self._role[key] = 'r'

    def insert_item(self, role, item, key, copy=True):
        if copy:
            item = item.copy()
        self[key] = item
        getattr(self, role).add(key)
        self._role[key] = role

    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    `None`

'''
        print cf_inspect(self)
    #--- End: def

    def item(self, description=None, key=False, default=None, **kwargs):
        '''
'''    
        if key:
            return self.key(description=description, default=default, **kwargs)

        d = self(description, **kwargs)
        if not d:
            return default

        items = d.popitem()

        return default if d else items[1]
    #--- End: def

    def key(self, description=None, default=None, **kwargs):
        '''
'''    
        d = self(description, **kwargs)
        if not d:
            return default

        items = d.popitem()

        return default if d else items[0]
    #--- End: def

    def key_item(self, description=None, default=(None, None), **kwargs):
        '''
'''    
        d = self(description, **kwargs)
        if not d:
            return default

        items = d.popitem()

        return default if d else items
    #--- End: def

    def remove_item(self, key):
        '''
'''
        self._axes.pop(key, None)
        getattr(self, self._role.pop(key)).discard(key)
        return self.pop(key)
    #--- End: def

    def role(self, key):
        return self._role[key]
    #--- End: def

#--- End: class
