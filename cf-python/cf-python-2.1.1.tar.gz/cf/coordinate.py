from itertools import izip

from numpy import empty       as numpy_empty
from numpy import result_type as numpy_result_type

from .boundedvariable  import BoundedVariable, Bounds
from .functions        import parse_indices
from .timeduration     import TimeDuration
from .units            import Units

from .data.data import Data


# ====================================================================
#
# Coordinate object
#
# ====================================================================

class Coordinate(BoundedVariable):
    '''

Base class for a CF dimension or auxiliary coordinate construct.


**Attributes**

===============  ========  ===================================================
Attribute        Type      Description
===============  ========  ===================================================
`!climatology`   ``bool``  Whether or not the bounds are intervals of
                           climatological time. Presumed to be False if unset.
===============  ========  ===================================================

'''
#    def __new__(cls, *args, **kwargs):
#        '''
#
#Called to create a new instance with the `!_cyclic` attribute set to
#True. ``*args`` and ``**kwargs`` are passed to the `__init__` method.
#
#''' 
#        self = super(Coordinate, cls).__new__(Coordinate)
#        self._cyclic = True
#        return self
#    #--- End: def

#    def __init__(self, properties={}, attributes={}, data=None, bounds=None,
#                 copy=True):
#        '''
#
#**Initialization**
#
#:Parameters:
#
#    properties : dict, optional
#        Initialize a new instance with CF properties from a
#        dictionary's key/value pairs.
#
#    attributes : dict, optional
#        Provide the new instance with attributes from a dictionary's
#        key/value pairs.
#
#    data : cf.Data, optional
#        Provide the new instance with an N-dimensional data array.
#
#    bounds : cf.Data or cf.Bounds, optional
#        Provide the new instance with cell bounds.
#
#    copy : bool, optional
#        If False then do not copy arguments prior to
#        initialization. By default arguments are deep copied.
#
#'''         
#        super(BoundedVariable, self).__init__(properties=properties,
#                                              attributes=attributes,
#                                              data=data,
#                                              bounds=bounds,
#                                              copy=copy)
#
#        # Set default standard names based on units
#    #--- End: def 

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def ctype(self):
        '''

The CF coordinate type.

One of ``'T'``, ``'X'``, ``'Y'`` or ``'Z'`` if the coordinate object
is for the respective CF axis type, otherwise None.

.. seealso:: `T`, `X`, `~cf.Coordinate.Y`, `Z`

:Examples:

>>> c.X
True
>>> c.ctype
'X'

>>> c.T
True
>>> c.ctype
'T'

'''
        for t in ('T', 'X', 'Y', 'Z'):
            if getattr(self, t):
                return t
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isauxiliary(self):
        '''False, denoting that the variable is not an auxiliary coordinate
object.

.. seealso::`isdimension`, `isdomainancillary`, `isfieldancillary`,
            `ismeasure`

:Examples:

>>> c.isauxiliary
False

        '''
        return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isdimension(self): 
        '''False, denoting that the variable is not a dimension coordinate
object.

.. seealso:: `isauxiliary``, `isdomainancillary`, `isfieldancillary`,
             `ismeasure`

:Examples:

>>> c.isdimension
False
        '''
        return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: T (read only)
    # ----------------------------------------------------------------
    @property
    def T(self):
        '''True if and only if the coordinates are for a CF T axis.
        
CF T axis coordinates are for a reference time axis hhave one or more
of the following:

  * The `axis` property has the value ``'T'``
  * Units of reference time (see `cf.Units.isreftime` for details)
  * The `standard_name` property is one of ``'time'`` or
    ``'forecast_reference_time'longitude'``

.. seealso:: `ctype`, `X`, `~cf.Coordinate.Y`, `Z`

:Examples:

>>> c.Units
<CF Units: seconds since 1992-10-8>
>>> c.T
True

>>> c.standard_name in ('time', 'forecast_reference_time')
True
>>> c.T
True

>>> c.axis == 'T' and c.T
True

        '''      
        if self.ndim > 1:
            return self.getprop('axis', None) == 'T'

        if (self.Units.isreftime or
            self.getprop('standard_name', 'T') in ('time',
                                                   'forecast_reference_time') or
            self.getprop('axis', None) == 'T'):
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: X (read only)
    # ----------------------------------------------------------------
    @property
    def X(self):
        '''True if and only if the coordinates are for a CF X axis.
        
CF X axis coordinates are for a horizontal axis have one or more of
the following:

  * The `axis` property has the value ``'X'``
  * Units of longitude (see `cf.Units.islongitude` for details)
  * The `standard_name` property is one of ``'longitude'``,
    ``'projection_x_coordinate'`` or ``'grid_longitude'``

.. seealso:: `ctype`, `T`, `~cf.Coordinate.Y`, `Z`

:Examples:

>>> c.Units
<CF Units: degreeE>
>>> c.X
True
 
>>> c.standard_name
'longitude'
>>> c.X
True

>>> c.axis == 'X' and c.X
True

        '''              
        if self.ndim > 1:
            return self.getprop('axis', None) == 'X'
            
        if (self.Units.islongitude or
            self.getprop('axis', None) == 'X' or
            self.getprop('standard_name', None) in ('longitude',
                                                    'projection_x_coordinate',
                                                    'grid_longitude')):
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: Y (read only)
    # ----------------------------------------------------------------
    @property
    def Y(self):
        '''True if and only if the coordinates are for a CF Y axis.

CF Y axis coordinates are for a horizontal axis and have one or more
of the following:

  * The `axis` property has the value ``'Y'``
  * Units of latitude (see `cf.Units.islatitude` for details)
  * The `standard_name` property is one of ``'latitude'``,
    ``'projection_y_coordinate'`` or ``'grid_latitude'``

.. seealso:: `ctype`, `T`, `X`, `Z`

:Examples:

>>> c.Units
<CF Units: degree_north>
>>> c.Y
True

>>> c.standard_name == 'latitude'
>>> c.Y
True
'''              
        if self.ndim > 1:
            return self.getprop('axis', None) == 'Y'

        if (self.Units.islatitude or 
            self.getprop('axis', None) == 'Y' or 
            self.getprop('standard_name', 'Y') in ('latitude',
                                                   'projection_y_coordinate',
                                                   'grid_latitude')):  
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: Z (read only)
    # ----------------------------------------------------------------
    @property
    def Z(self):
        '''True if and only if the coordinates are for a CF Z axis.

CF Z axis coordinates are for a vertical axis have one or more of the
following:

  * The `axis` property has the value ``'Z'``
  * Units of pressure (see `cf.Units.ispressure` for details), level,
    layer, or sigma_level
  * The `positive` property has the value ``'up'`` or ``'down'``
    (case insensitive)
  * The `standard_name` property is one of
    ``'atmosphere_ln_pressure_coordinate'``,
    ``'atmosphere_sigma_coordinate'``,
    ``'atmosphere_hybrid_sigma_pressure_coordinate'``,
    ``'atmosphere_hybrid_height_coordinate'``,
    ``'atmosphere_sleve_coordinate``', ``'ocean_sigma_coordinate'``,
    ``'ocean_s_coordinate'``, ``'ocean_s_coordinate_g1'``,
    ``'ocean_s_coordinate_g2'``, ``'ocean_sigma_z_coordinate'`` or
    ``'ocean_double_sigma_coordinate'``

.. seealso:: `ctype`, `T`, `X`, `~cf.Coordinate.Y`

:Examples:

>>> c.Units
<CF Units: Pa>
>>> c.Z
True

>>> c.Units.equivalent(cf.Units('K')) and c.positive == 'up'
True
>>> c.Z
True 

>>> c.axis == 'Z' and c.Z
True

>>> c.Units
<CF Units: sigma_level>
>>> c.Z
True

>>> c.standard_name
'ocean_sigma_coordinate'
>>> c.Z
True

'''   
        if self.ndim > 1:
            return self.getprop('axis', None) == 'Z'
        
        units = self.Units
        if (units.ispressure or
            str(self.getprop('positive', 'Z')).lower() in ('up', 'down') or
            self.getprop('axis', None) == 'Z' or
            (units and units.units in ('level', 'layer' 'sigma_level')) or
            self.getprop('standard_name', None) in
            ('atmosphere_ln_pressure_coordinate',
             'atmosphere_sigma_coordinate',
             'atmosphere_hybrid_sigma_pressure_coordinate',
             'atmosphere_hybrid_height_coordinate',
             'atmosphere_sleve_coordinate',
             'ocean_sigma_coordinate',
             'ocean_s_coordinate',
             'ocean_s_coordinate_g1',
             'ocean_s_coordinate_g2',
             'ocean_sigma_z_coordinate',
             'ocean_double_sigma_coordinate')):
            return True
        else:
            return False
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: axis
    # ----------------------------------------------------------------
    @property
    def axis(self):
        '''The axis CF property.

The `axis` property may be used to specify the type of coordinates. It
may take one of the values `'X'`, `'Y'`, `'Z'` or `'T'` which stand
for a longitude, latitude, vertical, or time axis respectively. A
value of `'X'`, `'Y'` or `'Z'` may also also used to identify generic
spatial coordinates (the values `'X'` and `'Y'` being used to identify
horizontal coordinates).

:Examples:

>>> c.axis = 'Y'
>>> c.axis
'Y'
>>> del c.axis

>>> c.setprop('axis', 'T')
>>> c.getprop('axis')
'T'
>>> c.delprop('axis')

        '''
        return self.getprop('axis')
    #--- End: def
    @axis.setter
    def axis(self, value): 
        self.setprop('axis', value)    
    @axis.deleter
    def axis(self):       
        self.delprop('axis')

    # ----------------------------------------------------------------
    # CF property: positive
    # ----------------------------------------------------------------
    @property
    def positive(self):
        '''The positive CF property.

The direction of positive (i.e., the direction in which the coordinate
values are increasing), whether up or down, cannot in all cases be
inferred from the `units`. The direction of positive is useful for
applications displaying the data. The `positive` attribute may have
the value `'up'` or `'down'` (case insensitive).

For example, if ocean depth coordinates encode the depth of the
surface as `0` and the depth of 1000 meters as `1000` then the
`postive` property will have the value `'down'`.
      
:Examples:

>>> c.positive = 'up'
>>> c.positive
'up'
>>> del c.positive

>>> c.setprop('positive', 'down')
>>> c.getprop('positive')
'down'
>>> c.delprop('positive')

        '''
        return self.getprop('positive')
    #--- End: def

    @positive.setter
    def positive(self, value):
        self.setprop('positive', value)  
        self._direction = None
   #--- End: def
 
    @positive.deleter
    def positive(self):
        self.delprop('positive')       
        self._direction = None

    def asauxiliary(self, copy=True):
        '''

Return the coordinate recast as an auxiliary coordinate.

:Parameters:

    copy : bool, optional
        If False then the returned auxiliary coordinate is not
        independent. By default the returned auxiliary coordinate is
        independent.

:Returns:

    out : cf.AuxiliaryCoordinate
        The coordinate recast as an auxiliary coordinate.

:Examples:

>>> a = c.asauxiliary()
>>> a = c.asauxiliary(copy=False)

'''
        return AuxiliaryCoordinate(attributes=self.attributes(),
                                   properties=self.properties(),
                                   data=getattr(self, 'Data', None),
                                   bounds=getattr(self, 'bounds', None),
                                   copy=copy)
    #--- End: def

    def asdimension(self, copy=True):
        '''

Return the coordinate recast as a dimension coordinate.

:Parameters:

    copy : bool, optional
        If False then the returned dimension coordinate is not
        independent. By default the returned dimension coordinate is
        independent.

:Returns:

    out : cf.DimensionCoordinate
        The coordinate recast as a dimension coordinate.

:Examples:

>>> d = c.asdimension()
>>> d = c.asdimension(copy=False)

'''        
        if self._hasData:
            if self.ndim > 1:
                raise ValueError(
                    "Dimension coordinate must be 1-d (not %d-d)" %
                    self.ndim)
        elif self._hasbounds:
            if self.bounds.ndim > 2:
                raise ValueError(
                    "Dimension coordinate must be 1-d (not %d-d)" %
                    self.ndim)

        return DimensionCoordinate(attributes=self.attributes(),
                                   properties=self.properties(),
                                   data=getattr(self, 'Data', None),
                                   bounds=getattr(self, 'bounds', None),
                                   copy=copy)
    #--- End: def

    def dump(self, display=True, omit=(), field=None, key=None,
             _level=0, _title=None): 
        '''

Return a string containing a full description of the coordinate.

:Parameters:

    display : bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

    omit : sequence of strs
        Omit the given CF properties from the description.

:Returns:

    out : None or str
        A string containing the description.

:Examples:

'''
#        indent0 = '    ' * _level
#        indent1 = '    ' * (_level+1)
        
        if _title is None:
            if self.isdimension:
                _title = 'Dimension Coordinate: '
            elif self.isauxiliary:
                _title = 'Auxiliary Coordinate: '
            else:
                _title = 'Coordinate: '
            _title = _title + self.name(default='')

        return super(Coordinate, self).dump(
            display=display, omit=omit, field=field, key=key,
             _level=_level, _title=_title)
    #--- End: def

#--- End: class


# ====================================================================
#
# DimensionCoordinate object
#
# ====================================================================

class DimensionCoordinate(Coordinate):
    '''A CF dimension coordinate construct.

**Attributes**

==============  ========  ============================================
Attribute       Type      Description
==============  ========  ============================================
`!climatology`  ``bool``  Whether or not the bounds are intervals of
                          climatological time. Presumed to be False if
                          unset.
==============  ========  ============================================

    '''
#    def _query_contain(self, value):
#        '''#
#
#'''
#        if not self._hasbounds:
#            return self == value#
#
#        return (self.lower_bounds <= value) & (self.upper_bounds >= value)
#    #--- End: def

    def _centre(self, period):
        '''

It assumed, but not checked, that the period has been set.

.. seealso:: `roll`

'''

        if self.direction():
            mx = self.Data[-1]
        else:
            mx = self.Data[0]
            
        return ((mx // period) * period).squeeze(i=True)
    #--- End: def

    def _infer_direction(self):
        '''
    
Return True if a coordinate is increasing, otherwise return False.

A coordinate is considered to be increasing if its *raw* data array
values are increasing in index space or if it has no data not bounds
data.

If the direction can not be inferred from the coordinate's data then
the coordinate's units are used.

The direction is inferred from the coordinate's data array values or
its from coordinates. It is not taken directly from its `cf.Data`
object.

:Returns:

    out : bool
        Whether or not the coordinate is increasing.
        
:Examples:

>>> c.array
array([  0  30  60])
>>> c._get_direction()
True
>>> c.array
array([15])
>>> c.bounds.array
array([  30  0])
>>> c._get_direction()
False

'''
        if self._hasData:
            # Infer the direction from the dimension coordinate's data
            # array
            c = self.Data
            if c._size > 1:
                c = c[0:2].unsafe_array
                return c.item(0,) < c.item(1,)
        #--- End: if

        # Still here? 
        if self._hasbounds:
            # Infer the direction from the dimension coordinate's
            # bounds
            b = self.bounds
            if b._hasData:
                b = b.Data
                b = b[(0,)*(b.ndim-1)].unsafe_array
                return b.item(0,) < b.item(1,)
        #--- End: if

#        # Still here? Then infer the direction from the dimension
#        # coordinate's positive CF property.
#        positive = self.getprop('positive', None)
#        if positive is not None and positive[0] in 'dD':
#            return False
#
        # Still here? Then infer the direction from the units.
        return not self.Units.ispressure
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def cellsize(self):
        '''

A `cf.Data` object containing the coordinate cell sizes.

:Examples:

>>> print c.bounds
<CF Bounds: latitude(47, 2) degrees_north>
>>> print c.bounds.array
[[-90. -87.]
 [-87. -80.]
 [-80. -67.]]
>>> print d.cellsize
<CF Data: [3.0, ..., 13.0] degrees_north>
>>> print d.cellsize.array
[  3.   7.  13.]
>>> print c.sin().cellsize.array
[ 0.00137047  0.01382178  0.0643029 ]

>>> del c.bounds
>>> c.cellsize
AttributeError: Can't get cell sizes when coordinates have no bounds


'''
        if not self._hasbounds:
            raise AttributeError(
                "Can't get cell sizes when coordinates have no bounds")

        cells = self.bounds.data

#        if bounds_range is not None:
#            bounds_range = Data.asdata(bounds_range)#
#
#            if not bounds_range.Units:
#                bounds_range = bounds_range.override_units(self.Units)
#            cells.clip(*bounds_range, units=bounds_range.Units, i=True)
#        #--- End: if
        if self.direction():            
            cells = cells[:, 1] - cells[:, 0]
        else:
            cells = cells[:, 0] - cells[:, 1]

        cells.squeeze(1, i=True)
        
#        if units:
#            if cells.Units.equivalent(units):
#                cells.Units = units
#            else:
#                raise ValueError("sdfm 845 &&&&")
        
        return cells
    #--- End: def
           
    @property
    def decreasing(self): 
        '''

True if the dimension coordinate is increasing, otherwise
False.

A dimension coordinate is increasing if its coordinate values are
increasing in index space.

The direction is inferred from one of, in order of precedence:

* The data array
* The bounds data array
* The `units` CF property

:Returns:

    out : bool
        Whether or not the coordinate is increasing.
        
True for dimension coordinate constructs, False otherwise.

>>> c.decreasing
False
>>> c.flip().increasing
True

'''
        return not self.direction()
    #--- End: def

    @property
    def increasing(self): 
        '''

True for dimension coordinate constructs, False otherwise.

>>> c.increasing
True
>>> c.flip().increasing
False

'''
        return self.direction()
    #--- End: def

    @property
    def isauxiliary(self):
        '''False, denoting that the variable is not an auxiliary coordinate
object.

.. seealso::`isdimension`, `isdomainancillary`, `isfieldancillary`,
            `ismeasure`

True for auxiliary coordinate constructs, False otherwise.

.. seealso:: `ismeasure`, `isdimension`

:Examples:

>>> c.isauxiliary
False
        '''
        return False
    #--- End: def

    @property
    def isdimension(self): 
        '''True, denoting that the variable is a dimension coordinate object.

.. seealso::`isauxiliary`, `isdomainancillary`, `isfieldancillary`,
            `ismeasure`

:Examples:

>>> c.isdimension
True

        '''
        return True
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def lower_bounds(self):
        '''

The lower dimension coordinate bounds in a `cf.Data` object.

.. seealso:: `bounds`, `upper_bounds`

:Examples:

>>> print c.bounds.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> c.lower_bounds
<CF Data: [3, ..., -1]>
>>> print c.lower_bounds.array
[ 3  1 -1]

'''
        if not self._hasbounds or not self.bounds._hasData:
            raise ValueError("Can't get lower bounds when there are no bounds")

        if self.direction():
            i = 0
        else:
            i = 1

        return self.bounds.data[..., i].squeeze(1, i=True)
    #--- End: def

    @property
    def role(self):
        '''

:Examples:

>>> c.role
'd'

'''
        return 'd'
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def upper_bounds(self):
        '''

The upper dimension coordinate bounds in a `cf.Data` object.

.. seealso:: `bounds`, `lower_bounds`

:Examples:

>>> print c.bounds.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> c.upper_bounds      
<CF Data: [5, ..., 1]>
>>> c.upper_bounds.array     
array([5, 3, 1])

'''
        if not self._hasbounds or not self.bounds._hasData:
            raise ValueError("Can't get upper bounds when there are no bounds")

        if self.direction():
            i = 1
        else:
            i = 0

        return self.bounds.data[..., i].squeeze(1, i=True)
    #--- End: def

    def asdimension(self, copy=True):
        '''

Return the dimension coordinate.

:Parameters:

    copy : bool, optional
        If False then the returned dimension coordinate is not
        independent. By default the returned dimension coordinate is
        independent.

:Returns:

    out : cf.DimensionCoordinate
        The dimension coordinate.

:Examples:

>>> d = c.asdimension()
>>> print d is c
True

>>> d = c.asdimension(copy=False)
>>> print d == c
True
>>> print d is c
False

'''
        if copy:
            return self.copy()
        
        return self
    #--- End: def

    def direction(self):
        '''Return True if the dimension coordinate values are increasing,
otherwise return False.

Dimension coordinates values are increasing if its coordinate values
are increasing in index space.

The direction is inferred from one of, in order of precedence:

* The data array
* The bounds data array
* The `units` CF property

:Returns:

    out : bool
        Whether or not the coordinate is increasing.
        
:Examples:

>>> c.array
array([  0  30  60])
>>> c.direction()
True

>>> c.bounds.array
array([  30  0])
>>> c.direction()
False

        ''' 
        _direction = self._direction
        if _direction is not None:
            return _direction

        _direction = self._infer_direction()
        self._direction = _direction

        return _direction
    #--- End: def
#ppp
    # DimensionCoordinate method
    def get_bounds(self, create=False, insert=False, bound=None,
                   cellsize=None, flt=0.5, copy=True):
        '''Get or create the cell bounds.
    
Either return its existing bounds or, if there are none, optionally
create bounds based on the coordinate array values.

:Parameters:

    create: `bool`, optional
        If True then create bounds if and only if the the dimension
        coordinate does not already have them. Bounds for Voronoi
        cells are created unless *bound* or *cellsize* is set.

    insert: `bool`, optional
        If True then insert the created bounds into the coordinate in
        place. By default the created bounds are not inserted. Ignored
        if *create* is not True.

    bound: optional
        If set to a value larger (smaller) than the largest (smallest)
        coordinate value then bounds are created which include this
        value and for which each coordinate is in the centre of its
        bounds. Ignored if *create* is False.

    cellsize: optional
        Define the exact size of each cell that is created. Created
        cells are allowed to overlap do not have to be contigious.
        Ignored if *create* is False. The *cellsize* parameter may be
        one of:

          * A data-like scalar (see below) that defines the cell size,
            either in the same units as the coordinates or in the
            units provided. Note that in this case, the position of
            each coordinate within the its cell is controlled by the
            *flt* parameter.

              *Example:*     
                To specify cellsizes of 10, in the same units as the
                coordinates: ``cellsize=10``.
    
              *Example:*
                To specify cellsizes of 1 day: ``cellsize=cf.Data(1,
                'day')`` (see `cf.Data` for details).
    
              *Example:*
                 For coordinates ``1, 2, 10``, setting ``cellsize=1``
                 will result in bounds of ``(0.5, 1.5), (1.5, 2.5),
                 (9.5, 10.5)``.
      
              *Example:*
                 For coordinates ``1, 2, 10`` kilometres, setting
                 ``cellsize=cf.Data(5000, 'm')`` will result in bounds
                 of ``(-1.5, 3.5), (-0.5, 4.5), (7.5, 12.5)`` (see
                 `cf.Data` for details).
      
              *Example:*
                 For decreasing coordinates ``2, 0, -12`` setting,
                 ``cellsize=2`` will result in bounds of ``(3, 1), (1,
                 -1), (-11, -13)``.

        ..

          * A `cf.TimeDuration` defining the cell size. Only
            applicable to reference time coordinates. It is possible
            to "anchor" the cell bounds via the `cf.TimeDuration`
            parameters. For example, to specify cell size of one
            calendar month, starting and ending on the 15th day:
            ``cellsize=cf.M(day=15)`` (see `cf.M` for details). Note
            that the *flt* parameter is ignored in this case.
      
              *Example:*
                 For coordinates ``1984-12-01 12:00, 1984-12-02 12:00,
                 2000-04-15 12:00`` setting, ``cellsize=cf.D()`` will
                 result in bounds of ``(1984-12-01, 1984-12-02),
                 (1984-12-02, 1984-12-03), (2000-05-15, 2000-04-16)``
                 (see `cf.D` for details).

              *Example:*
                 For coordinates ``1984-12-01, 1984-12-02,
                 2000-04-15`` setting, ``cellsize=cf.D()`` will result
                 in bounds of ``(1984-12-01, 1984-12-02), (1984-12-02,
                 1984-12-03), (2000-05-15, 2000-04-16)`` (see `cf.D`
                 for details).

              *Example:*
                 For coordinates ``1984-12-01, 1984-12-02,
                 2000-04-15`` setting, ``cellsize=cf.D(hour=12)`` will
                 result in bounds of ``(1984-11:30 12:00, 1984-12-01
                 12:00), (1984-12-01 12:00, 1984-12-02 12:00),
                 (2000-05-14 12:00, 2000-04-15 12:00)`` (see `cf.D`
                 for details).

              *Example:*
                 For coordinates ``1984-12-16 12:00, 1985-01-16
                 12:00`` setting, ``cellsize=cf.M()`` will result in
                 bounds of ``(1984-12-01, 1985-01-01), (1985-01-01,
                 1985-02-01)`` (see `cf.M` for details).

              *Example:*
                 For coordinates ``1984-12-01 12:00, 1985-01-01
                 12:00`` setting, ``cellsize=cf.M()`` will result in
                 bounds of ``(1984-12-01, 1985-01-01), (1985-01-01,
                 1985-02-01)`` (see `cf.M` for details).

              *Example:*
                 For coordinates ``1984-12-01 12:00, 1985-01-01
                 12:00`` setting, ``cellsize=cf.M(day=20)`` will
                 result in bounds of ``(1984-11-20, 1984-12-20),
                 (1984-12-20, 1985-01-20)`` (see `cf.M` for details).

              *Example:*
                 For coordinates ``1984-03-01, 1984-06-01`` setting,
                 ``cellsize=cf.Y()`` will result in bounds of
                 ``(1984-01-01, 1985-01-01), (1984-01-01,
                 1985-01-01)`` (see `cf.Y` for details). Note that in
                 this case each cell has the same bounds. This because
                 ``cf.Y()`` is equivalent to ``cf.Y(month=1, day=1)``
                 and the closest 1st January to both coordinates is
                 1st January 1984.

        {+data-like-scalar}

    flt: `float`, optional
        When creating cells with sizes specified by the *cellsize*
        parameter, define the fraction of the each cell which is less
        its coordinate value. By default *flt* is 05, so that each
        cell has its coordinate at it's centre. Ignored if *cellsize*
        is not set. 

          *Example:*
             For coordinates ``1, 2, 10``, setting ``cellsize=1,
             flt=0.5`` will result in bounds of ``(0.5, 1.5), (1.5,
             2.5), (9.5, 10.5)``.
  
          *Example:*
             For coordinates ``1, 2, 10``, setting ``cellsize=1,
             flt=0.25`` will result in bounds of ``(0.75, 1.75),
             (1.75, 2.75), (9.75, 10.75)``.
  
          *Example:* 
             For decreasing coordinates ``2, 0, -12``, setting
             ``cellsize=6, flt=0.9`` will result in bounds of ``(2.6,
             -3.4), (0.6, -5.4), (-11.4, -17.4)``.

    copy: `bool`, optional
        If False then the returned bounds are not independent of the
        existing bounds, if any, or those inserted, if *create* and
        *insert* are both True. By default the returned bounds are
        independent.

:Returns:

    out: `cf.Bounds`
        The existing or created bounds.

:Examples:

>>> c.get_bounds()
>>> c.get_bounds(create=True)
>>> c.get_bounds(create=True, bound=60)
>>> c.get_bounds(create=True, insert=True)
>>> c.get_bounds(create=True, bound=-9000.0, insert=True, copy=False)

        '''
        if self._hasbounds:
            if copy:
                return self.bounds.copy()
            else:
                return self.bounds
         
        if not create:
            raise ValueError(
                "Dimension coordinates have no bounds and create={0}".format(create))

        array = self.unsafe_array
        size = array.size    

        if cellsize is not None:
            if bound:
                raise ValueError(
"bound parameter can't be True when setting the cellsize parameter")

            if not isinstance(cellsize, TimeDuration):
                # ----------------------------------------------------
                # Create bounds based on cell sizes defined by a
                # data-like object
                # 
                # E.g. cellsize=10
                #      cellsize=cf.Data(1, 'day')
                # ----------------------------------------------------
                cellsize = Data.asdata(abs(cellsize))
                if cellsize.Units:
                    if self.Units.isreftime:
                        if not cellsize.Units.istime:
                            raise ValueError("q123423423jhgsjhbd jh ")
                        cellsize.Units = Units(self.Units._utime.units)
                    else:
                        if not cellsize.Units.equivalent(self.Units):
                            raise ValueError("jhgsjhbd jh ")
                        cellsize.Units = self.Units
                cellsize = cellsize.datum()
                
                cellsize0 = cellsize * flt
                cellsize1 = cellsize * (1 - flt)
                if not self.direction():
                    cellsize0, cellsize1 = -cellsize1, -cellsize0
                
                bounds = numpy_empty((size, 2), dtype=array.dtype)
                bounds[:, 0] = array - cellsize0
                bounds[:, 1] = array + cellsize1
            else:
                # ----------------------------------------------------
                # Create bounds based on cell sizes defined by a
                # TimeDuration object
                # 
                # E.g. cellsize=cf.s()
                #      cellsize=cf.m()
                #      cellsize=cf.h()
                #      cellsize=cf.D()
                #      cellsize=cf.M()
                #      cellsize=cf.Y()
                #      cellsize=cf.D(hour=12)
                #      cellsize=cf.M(day=16)
                #      cellsize=cf.M(2)
                #      cellsize=cf.M(2, day=15, hour=12)
                # ----------------------------------------------------
                if not self.Units.isreftime:
                    raise ValueError(
"Can't create reference time bounds for non-reference time coordinates: {0!r}".format(
    self.Units))

                bounds = numpy_empty((size, 2), dtype=object)

                cellsize_bounds = cellsize.bounds
                calendar = getattr(self, 'calendar', None)
                direction = bool(self.direction())

                for c, b in izip(self.dtarray, bounds):
                    b[...] = cellsize_bounds(c, direction=direction)
        else:
            if bound is None:
                # ----------------------------------------------------
                # Creat Voronoi bounds
                # ----------------------------------------------------
                if size < 2:
                    raise ValueError(
"Can't create bounds for Voronoi cells from one value")

                bounds_1d = [array.item(0,)*1.5 - array.item(1,)*0.5]
                bounds_1d.extend((array[0:-1] + array[1:])*0.5)
                bounds_1d.append(array.item(-1,)*1.5 - array.item(-2,)*0.5)
    
                dtype = type(bounds_1d[0])
    
            else:
                # ----------------------------------------------------
                # Create
                # ----------------------------------------------------
                direction = self.direction()
                if not direction and size > 1:
                    array = array[::-1]
    
                bounds_1d = [bound]
                if bound <= array.item(0,):
                    for i in xrange(size):
                        bound = 2.0*array.item(i,) - bound
                        bounds_1d.append(bound)
                elif bound >= array.item(-1,):
                    for i in xrange(size-1, -1, -1):
                        bound = 2.0*array.item(i,) - bound
                        bounds_1d.append(bound)
    
                    bounds_1d = bounds_1d[::-1]
                else:
                    raise ValueError("bad bound value")
    
                dtype = type(bounds_1d[-1])
    
                if not direction:               
                    bounds_1d = bounds_1d[::-1]
            #--- End: if

            bounds = numpy_empty((size, 2), dtype=dtype)
            bounds[:,0] = bounds_1d[:-1]
            bounds[:,1] = bounds_1d[1:]        
        #--- End: if

        # Create coordinate bounds object
        bounds = Bounds(data=Data(bounds, self.Units), copy=False)
                           
        if insert:
            # Insert coordinate bounds in-place
            self.insert_bounds(bounds, copy=copy)

        return bounds            
    #--- End: def

    def period(self, *value):
        '''Set the period for cyclic coordinates.

:Parameters:

    value: data-like or `None`, optional
        The period. The absolute value is used.

        {+data-like-scalar}

:Returns:

    out: `cf.Data` or `None`
        The period prior to the change, or the current period if no
        *value* was specified. In either case, None is returned if the
        period had not been set previously.

:Examples:

>>> print c.period()
None
>>> c.Units
<CF Units: degrees_east>
>>> print c.period(360)
None
>>> c.period()
<CF Data: 360.0 'degrees_east'>
>>> import math
>>> c.period(cf.Data(2*math.pi, 'radians'))
<CF Data: 360.0 degrees_east>
>>> c.period()
<CF Data: 6.28318530718 radians>
>>> c.period(None)
<CF Data: 6.28318530718 radians>
>>> print c.period()
None
>>> print c.period(-360)
None
>>> c.period()
<CF Data: 360.0 degrees_east>

        '''     
        old = self._period
        if old is not None:
            old = old.copy()

        if not value:
            return old
  
        value = value[0]

        if value is not None:
            value = Data.asdata(abs(value*1.0))
            units = value.Units
            if not units:
                value = value.override_units(self.Units)
            elif not units.equivalent(self.Units):
                raise ValueError(
"Period units {0!r} are not equivalent to coordinate units {1!r}".format(
    units, self.Units))

            range = self.Data.range()
            if range >= value:
                raise ValueError(
"The coordinate range {0!r} is not less than the period {1!r}".format(
    range, value))
        #--- End: if

        self._period = value

        return old
    #--- End: def

    def roll(self, axis, shift, i=False):
        '''
    {+i}

'''
        if self.size <= 1:
            if i:
                return self
            else:
                return self.copy()
        #--- End: if

        shift %= self.size

        period = self._period

        if not shift:
            # Null roll
            if i:
                return self
            else:
                return self.copy()
        elif period is None:
            raise ValueError(
"Can't roll {} array by {} positions when no period has been set".format(
    self.__class__.__name__, shift))

        direction = self.direction()

        centre = self._centre(period)

        c = super(DimensionCoordinate, self).roll(axis, shift, i=i)

        isbounded = c._hasbounds
        if isbounded:
            b = c.bounds
            if not b._hasData:
                isbounded = False
        #--- End: if
 
        if direction:
            # Increasing
            c[:shift] -= period
            if isbounded:
                b[:shift] -= period

            if c.Data[0] <= centre - period:
                c += period
                if isbounded:
                    b += period 
        else:
            # Decreasing
            c[:shift] += period
            if isbounded:
                b[:shift] += period

            if c.Data[0] >= centre + period:
                c -= period
                if isbounded:
                    b -= period
        #--- End: if 

        c._direction = direction

#
#
#        if self.direction():
#            indices = c > c[-1]
#        else:
#            indices = c > c[0]
#
#        c.setdata(c - period, None, indices)
#
#        isbounded = c._hasbounds
#        if isbounded:
#            b = c.bounds
#            if b._hasData:
#                indices.expand_dims(1, i=True)
#                b.setdata(b - period, None, indices)
#            else:
#                isbounded = False
#        #--- End: if
#
#        shift = None
#        if self.direction():
#            # Increasing
#            if c.datum(0) <= centre - period:
#                shift = period
##                c += period
#            elif c.datum(-1) >= centre + period:
#                shift = -period
##                c -= period
#        else:
#            # Decreasing
#            if c.datum(0) >= centre + period:
#                shift = -period
##                c -= period                
#            elif c.datum(-1) <= centre - period:
#                shift = period
##                c += period
#        #--- End: if
#        
#        if shift:
#            c += shift
#            if isbounded:
#                b += shift
#        #--- End: if

        return c
    #--- End: def

#--- End: class


# ====================================================================
#
# AuxiliaryCoordinate object
#
# ====================================================================

class AuxiliaryCoordinate(Coordinate):
    '''

A CF auxiliary coordinate construct.


**Attributes**

===============  ========  ===================================================
Attribute        Type      Description
===============  ========  ===================================================
`!climatology`   ``bool``  Whether or not the bounds are intervals of
                           climatological time. Presumed to be False if unset.
===============  ========  ===================================================

'''
    @property
    def isauxiliary(self):
        '''True, denoting that the variable is a aucilliary coordinate object.

.. seealso::`isdimension`, `isdomainancillary`, `isfieldancillary`,
            `ismeasure`

:Examples:

>>> c.isauxiliary
True

        '''
        return True
    #--- End: def

    @property
    def isdimension(self): 
        '''False, denoting that the variable is not a dimension coordinate
object.

.. seealso::`isauxiliary`, `isdomainancillary`, `isfieldancillary`,
            `ismeasure`

:Examples:

>>> c.isdimension
False
        '''
        return False
    #--- End: def

    @property
    def role(self):
        '''

:Examples:

>>> c.role
'a'

'''
        return 'a'
    #--- End: def
 
    def asauxiliary(self, copy=True):
        '''

Return the auxiliary coordinate.

:Parameters:

    copy : bool, optional   
        If False then the returned auxiliary coordinate is not
        independent. By default the returned auxiliary coordinate is
        independent.

:Returns:

    out : cf.AuxiliaryCoordinate
        The auxiliary coordinate.

:Examples:

>>> d = c.asauxiliary()     
>>> print d is c
True

>>> d = c.asauxiliary(copy=False)
>>> print d == c
True
>>> print d is c
False

'''
        if copy:
            return self.copy()
        
        return self
    #--- End: def

#--- End: class

