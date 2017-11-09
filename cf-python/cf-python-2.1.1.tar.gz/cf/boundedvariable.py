from itertools import izip

from numpy import size        as numpy_size
from numpy import expand_dims as numpy_expand_dims

from .functions    import parse_indices
from .variable     import Variable, SubspaceVariable

from .data.data import Data

_debug = False

# ====================================================================
#
# Bounded variable object
#
# ====================================================================

class BoundedVariable(Variable):
    '''Base class for CF dimension coordinate, auxiliary coordinate and
domain ancillary objects.

    '''
    def __init__(self, properties={}, attributes={}, data=None,
                 bounds=None, source=None, copy=True):
        '''**Initialization**

:Parameters:

:Parameters:

    properties: `dict`, optional
        Initialize a new instance with CF properties from a
        dictionary's key/value pairs.

    attributes: `dict`, optional
        Provide the new instance with attributes from a dictionary's
        key/value pairs.

    data: `cf.Data`, optional
        Provide the new instance with an N-dimensional data array.

    bounds: `cf.Data` or `cf.Bounds`, optional
        Provide the new instance with cell bounds.

    source: `cf.BoundedVariable`, optional
        Take the attributes, CF properties and data array from the
        source object. Any attributes, CF properties or data array
        specified with other parameters are set after initialisation
        from the source instance.

    copy: `bool`, optional
        If False then do not copy arguments prior to
        initialization. By default arguments are deep copied.

        '''         
        # DO NOT CHANGE _period IN PLACE
        self._period    = None

        if source is not None:
            if bounds is None:
                if isinstance(source, BoundedVariable):
                    bounds = getattr(self, 'bounds', None)
                
        # Set attributes, CF properties and data
        super(BoundedVariable, self).__init__(properties=properties,
                                              attributes=attributes,
                                              data=data,
                                              source=source,
                                              copy=copy)

        # Bounds
        if bounds is not None:
            self.insert_bounds(bounds, copy=copy)

        # Set default standard names based on units
    #--- End: def

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]
        
        '''
        if indices is Ellipsis:
            return self.copy()

        # Parse the index
        if not isinstance(indices, tuple):
            indices = (indices,)

        arg0 = indices[0]
        if isinstance(arg0, basestring) and arg0 == 'mask':
            auxiliary_mask = indices[:2]
            indices2       = indices[2:]
        else:
            auxiliary_mask = None
            indices2       = indices
          
        indices, roll = parse_indices(self.shape, indices2, cyclic=True)

        if roll:
            new = self
            data = self.Data
            axes = data._axes
            cyclic_axes = data._cyclic
            for iaxis, shift in roll.iteritems():
                if axes[iaxis] not in cyclic_axes:
                    raise IndexError(
                        "Can't do a cyclic slice on a non-cyclic axis")

                new = new.roll(iaxis, shift)
            #--- End: for
        else:
            new = self.copy(_omit_Data=True)

        data = self.Data

        if auxiliary_mask:
            findices = tuple(auxiliary_mask) + tuple(indices)
        else:
            findices = tuple(indices)

        if _debug:
            cname = self.__class__.__name__
            print '{}.__getitem__: shape    = {}'.format(cname, self.shape)
            print '{}.__getitem__: indices2 = {}'.format(cname, indices2)
            print '{}.__getitem__: indices  = {}'.format(cname, indices)
            print '{}.__getitem__: findices = {}'.format(cname, findices)

        new.Data = data[findices]

        # Subspace the bounds, if there are any
        if not new._hasbounds:
            bounds = None
        else:
            bounds = self.bounds
            if bounds._hasData:
                findices = list(findices)
                if data.ndim <= 1:
#                    indices = list(indices)
                    index = indices[0]
                    if isinstance(index, slice):
                        if index.step < 0:
                            # This scalar or 1-d variable has been
                            # reversed so reverse its bounds (as per
                            # 7.1 of the conventions)
                            findices.append(slice(None, None, -1))
                    elif data.size > 1 and index[-1] < index[0]:
                        # This 1-d variable has been reversed so
                        # reverse its bounds (as per 7.1 of the
                        # conventions)
                        findices.append(slice(None, None, -1))                    
                #--- End: if

                if auxiliary_mask:
                    findices[1] = [mask.expand_dims(-1) for mask in findices[1]]

                if _debug:
                    print '{}.__getitem__: findices for bounds ='.format(self.__class__.__name__, findices)
                
                new.bounds.Data = bounds.Data[tuple(findices)]
        #--- End: if

        new._direction = None

        # Return the new bounded variable
        return new
    #--- End: def

    def __eq__(self, y):
        '''

The rich comparison operator ``==``

x.__eq__(y) <==> x==y

'''
        return self._binary_operation(y, '__eq__', False)
    #--- End: def

    def __ne__(self, y):
        '''

The rich comparison operator ``!=``

x.__ne__(y) <==> x!=y

'''
        return self._binary_operation(y, '__ne__', False)
    #--- End: def

    def __ge__(self, y):
        '''

The rich comparison operator ``>=``

x.__ge__(y) <==> x>=y

'''
        return self._binary_operation(y, '__ge__', False)
    #--- End: def

    def __gt__(self, y):
        '''

The rich comparison operator ``>``

x.__gt__(y) <==> x>y

'''
        return self._binary_operation(y, '__gt__', False)
    #--- End: def

    def __le__(self, y):
        '''

The rich comparison operator ``<=``

x.__le__(y) <==> x<=y

'''
        return self._binary_operation(y, '__le__', False)
    #--- End: def

    def __lt__(self, y):
        '''

The rich comparison operator ``<``

x.__lt__(y) <==> x<y

'''
        return self._binary_operation(y, '__lt__', False)
    #--- End: def
    
    def _query_contain(self, value):
        '''

'''
        if not self._hasbounds:
            return self == value

#        bounds = self.bounds.Data
#        mn = bounds.min(axes=-1)
#        mx = bounds.max(axes=-1)

        return (self.lower_bounds <= value) & (self.upper_bounds >= value)

#        return ((mn <= value) & (mx >= value)).squeeze(axes=-1, i=True)
    #--- End: def

    def _binary_operation(self, other, method, bounds=True):
        '''Implement binary arithmetic and comparison operations.

The operations act on the {+variable}'s data array with the numpy
broadcasting rules.

If the {+variable} has bounds then they are operated on with the same
data as the the {+variable}'s data array.

It is intended to be called by the binary arithmetic and comparison
methods, such as `!__sub__` and `!__lt__`.

:Parameters:

    other:

    method: `str`
        The binary arithmetic or comparison method name (such as
        ``'__imul__'`` or ``'__ge__'``).

    bounds: `bool`, optional

:Returns:

    new: `cf.+{Variable}`
        A new {+variable}, or the same {+variable} if the operation
        was in-place.

:Examples:

        '''
        inplace = method[2] == 'i'

        hasbounds = bounds and self._hasbounds
        
        if hasbounds and inplace and other is self:
            other = other.copy()
        
        new = super(BoundedVariable, self)._binary_operation(other, method)

        if hasbounds:
            if numpy_size(other) > 1:
                try:
                    other = other.expand_dims(-1)
                except AttributeError:
                    other = numpy_expand_dims(other, -1)
                
            new_bounds = self.bounds._binary_operation(other, method)

            if not inplace:
                new.insert_bounds(new_bounds, copy=False)
        #--- End: if

        if not bounds and new._hasbounds:
            del new.bounds
            
        if inplace:
            return self
        else:
            return new
    #--- End: def

    def _change_axis_names(self, dim_name_map):
        '''

Change the axis names.

Warning: dim_name_map may be changed in place

:Parameters:

    dim_name_map : dict

:Returns:

    None

:Examples:

'''
        # Change the axis names of the data array
        super(BoundedVariable, self)._change_axis_names(dim_name_map)

        if self._hasbounds:
            bounds = self.bounds
            if bounds._hasData:
                b_axes = bounds.Data._axes
                if self._hasData:
                    # Change the dimension names of the bounds
                    # array. Note that it is assumed that the bounds
                    # array dimensions are in the same order as the
                    # variable's data array dimensions. It is not
                    # required that the set of original bounds
                    # dimension names (bar the trailing dimension)
                    # equals the set of original variable's data array
                    # dimension names. The bounds array dimension
                    # names will be changed to match the updated
                    # variable's data array dimension names.
                    dim_name_map = {b_axes[-1]: 'bounds'}
                    for c_dim, b_dim in izip(self.Data._axes, b_axes):
                         dim_name_map[b_dim] = c_dim
                else:
                    dim_name_map[b_axes[-1]] = 'bounds'

                bounds._change_axis_names(dim_name_map)
    #--- End: def

    def _equivalent_data(self, other, rtol=None, atol=None, traceback=False):
        ''':Parameters:

    copy : bool, optional

        If False then the *other* bounded variable construct might get
        change in place.

:Returns:

    None

:Examples:

>>>

        '''
        hasbounds = self.hasbounds
        if hasbounds != other._hasbounds:
            # add traceback
            if traceback:
                print 'one has bounds, teh other not'
            return False

        direction0 = self.direction()
        direction1 = other.direction()
        if (direction0 != direction1 and 
            direction0 is not None and direction1 is not None):
            other = other.flip()

        # Compare the data arrays
        if not super(BoundedVariable, self)._equivalent_data(
                other, rtol=rtol, atol=atol, traceback=True):            
            if traceback:
                # add traceback
                print 'non equivaelnt data arrays'
            return False

        if hasbounds:
            # Both variables have bounds
            if not self.bounds._equivalent_data(other.bounds, rtol=rtol,
                                                atol=atol):
                if traceback:
                    # add traceback
                    print 'non equivaelnt bounds data'
                return False
        #--- End: if

        # Still here? Then the data are equivalent.
        return True
    #--- End: def

    def _parse_axes(self, axes):
        if axes is None:
            return axes

        ndim = self.ndim
        return [(i + ndim if i < 0 else i) for i in axes]
    #--- End: def
    
    # ----------------------------------------------------------------
    # Attribute (a special attribute)
    # ----------------------------------------------------------------
    @property
    def bounds(self):
        '''

The `cf.Bounds` object containing the cell bounds.

.. versionadded:: 2.0

.. seealso:: `lower_bounds`, `upper_bounds`

:Examples:

>>> c
<CF {+Variable}: latitude(64) degrees_north>
>>> c.bounds
<CF Bounds: latitude(64, 2) degrees_north>
>>> c.bounds = b
AttributeError: Can't set 'bounds' attribute. Consider the insert_bounds method.
>>> c.bounds.max()
<CF Data: 90.0 degrees_north>
>>> c.bounds -= 1
AttributeError: Can't set 'bounds' attribute. Consider the insert_bounds method.
>>> b = c.bounds
>>> b -= 1
>>> c.bounds.max()       
<CF Data: 89.0 degrees_north>

'''
        return self._get_special_attr('bounds')
    #--- End: def
    @bounds.setter
    def bounds(self, value):
        raise AttributeError(
            "Can't set 'bounds' attribute. Use the insert_bounds method.")
    #--- End: def
    @bounds.deleter
    def bounds(self):  
        self._del_special_attr('bounds')
        self._hasbounds = False
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def cellsize(self):
        '''

A `cf.Data` object containing the variable cell sizes.

.. versionadded:: 2.0

:Examples:

>>> print c.bounds
<CF {+Variable}: latitude(47, 2) degrees_north>
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
AttributeError: Can't get cell sizes when cells have no bounds


'''
        if not self._hasbounds:
            raise AttributeError(
                "Can't get cell sizes when cells have no bounds")

        cells = self.bounds.data
        cells = (cells[:, 1] - cells[:, 0]).abs()
        cells.squeeze(1, i=True)
        
        return cells
    #--- End: def
           
    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def dtype(self):
        '''Numpy data-type of the data array.

.. versionadded:: 2.0 

:Examples:

>>> c.dtype
dtype('float64')
>>> import numpy
>>> c.dtype = numpy.dtype('float32')

        '''
        if self._hasData:
            return self.Data.dtype
        
        if self._hasbounds:
            return self.bounds.dtype

        raise AttributeError("%s doesn't have attribute 'dtype'" %
                             self.__class__.__name__)
    #--- End: def
    @dtype.setter
    def dtype(self, value):
        if self._hasData:
            self.Data.dtype = value

        if self._hasbounds:
            self.bounds.dtype = value
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def isperiodic(self): 
        '''

.. versionadded:: 2.0 

>>> print c.period()
None
>>> c.isperiodic
False
>>> c.period(cf.Data(360, 'degeres_east'))
None
>>> c.isperiodic
True
>>> c.period(None)
<CF Data: 360 degrees_east>
>>> c.isperiodic
False

'''
        return self._period is not None
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def lower_bounds(self):
        '''The lower cell bounds.

The lower cell bounds are returned in a `cf.Data` object.

Note that ``c.lower_bounds`` is equivalent to
``c.bounds.data.min(axes=-1)``.

.. versionadded:: 2.0

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
        if not self._hasbounds:
            raise ValueError("Can't get lower bounds when there are no bounds")

        return self.bounds.lower_bounds
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def subspace(self):
        '''Return a new bounded variable whose data and bounds are subspaced in a
consistent manner.

This attribute may be indexed to select a subspace from dimension
index values.

**Subspacing by indexing**

Subspacing by dimension indices uses an extended Python slicing
syntax, which is similar numpy array indexing. There are two
extensions to the numpy indexing functionality:

* Size 1 dimensions are never removed.

  An integer index i takes the i-th element but does not reduce the
  rank of the output array by one.

* When advanced indexing is used on more than one dimension, the
  advanced indices work independently.

  When more than one dimension's slice is a 1-d boolean array or 1-d
  sequence of integers, then these indices work independently along
  each dimension (similar to the way vector subscripts work in
  Fortran), rather than by their elements.

.. versionadded:: 2.0 

:Examples:

        '''
        return SubspaceBoundedVariable(self)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute
    # ----------------------------------------------------------------
    @property
    def Units(self):
        '''

The Units object containing the units of the data array.

.. versionadded:: 2.0 

'''
        return Variable.Units.fget(self)
    #--- End: def

    @Units.setter
    def Units(self, value):
        Variable.Units.fset(self, value)

        # Set the Units on the bounds
        if self._hasbounds:
            self.bounds.Units = value

        # Set the Units on the period
        if self._period is not None:
            period = self._period.copy()
            period.Units = value
            self._period = period

        self._direction = None
    #--- End: def
    
    @Units.deleter
    def Units(self):
        Variable.Units.fdel(self)
        
        if self._hasbounds:
            # Delete the bounds' Units
            del self.bounds.Units

        if self._period is not None:
            # Delete the period's Units
            period = self._period.copy()
            del period.Units
            self._period = period

        self._direction = None
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def upper_bounds(self):
        '''The upper cell bounds.

The upper cell bounds are returned in a `cf.Data` object.

Note that ``c.upper_bounds`` is equivalent to
``c.bounds.data.max(axes=-1)``.

.. versionadded:: 2.0 

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
        if not self._hasbounds:
            raise ValueError("Can't get upper bounds when there are no bounds")

        return self.bounds.upper_bounds
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: calendar
    # ----------------------------------------------------------------
    @property
    def calendar(self):
        '''

The calendar CF property.

This property is a mirror of the calendar stored in the `Units`
attribute.

.. versionadded:: 2.0 

:Examples:

>>> c.calendar = 'noleap'
>>> c.calendar
'noleap'
>>> del c.calendar

>>> c.setprop('calendar', 'proleptic_gregorian')
>>> c.getprop('calendar')
'proleptic_gregorian'
>>> c.delprop('calendar')

'''
        return Variable.calendar.fget(self)
    #--- End: def

    @calendar.setter
    def calendar(self, value):
        Variable.calendar.fset(self, value)
        # Set the calendar of the bounds
        if self._hasbounds:
            self.bounds.setprop('calendar', value)
    #--- End: def

    @calendar.deleter
    def calendar(self):
        Variable.calendar.fdel(self)
        # Delete the calendar of the bounds
        if self._hasbounds:
            try:
                self.bounds.delprop('calendar')
            except AttributeError:
                pass
    #--- End: def
#    # ----------------------------------------------------------------
#    # CF property
#    # ----------------------------------------------------------------
#    @property
#    def leap_month(self):
#        '''
#
#The leap_month CF property.
#
#.. versionadded:: 2.0 
#
#:Examples:
#
#>>> c.leap_month = 2
#>>> c.leap_month
#2
#>>> del c.leap_month
#
#>>> c.setprop('leap_month', 11)
#>>> c.getprop('leap_month')
#11
#>>> c.delprop('leap_month')
#
#'''
#        return self.getprop('leap_month')
#    #--- End: def
#    @leap_month.setter
#    def leap_month(self, value):
#        self.setprop('leap_month', value)
#    @leap_month.deleter
#    def leap_month(self):        
#        self.delprop('leap_month')
#
#    # ----------------------------------------------------------------
#    # CF property
#    # ----------------------------------------------------------------
#    @property
#    def leap_year(self):
#        '''
#
#The leap_year CF property.
#
#.. versionadded:: 2.0 
#
#:Examples:
#
#>>> c.leap_year = 1984
#>>> c.leap_year
#1984
#>>> del c.leap_year
#
#>>> c.setprop('leap_year', 1984)
#>>> c.getprop('leap_year')
#1984
#>>> c.delprop('leap_year')
#
#'''
#        return self.getprop('leap_year')
#    #--- End: def
#    @leap_year.setter
#    def leap_year(self, value):
#        self.setprop('leap_year', value)
#    @leap_year.deleter
#    def leap_year(self):
#        self.delprop('leap_year')
#
#    # ----------------------------------------------------------------
#    # CF property
#    # ----------------------------------------------------------------
#    @property
#    def month_lengths(self):
#        '''
#
#The month_lengths CF property.
#
#Stored as a tuple but may be set as any array-like object.
#
#.. versionadded:: 2.0 
#
#:Examples:
#
#>>> c.month_lengths = numpy.array([34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34])
#>>> c.month_lengths
#(34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34)
#>>> del c.month_lengths
#
#>>> c.setprop('month_lengths', [34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34])
#>>> c.getprop('month_lengths')
#(34, 31, 32, 30, 29, 27, 28, 28, 28, 32, 32, 34)
#>>> c.delprop('month_lengths')
#
#'''
#        return self.getprop('month_lengths')
#    #--- End: def
#
#    @month_lengths.setter
#    def month_lengths(self, value):
#        value = tuple(value)
#        self.setprop('month_lengths', value)
#    #--- End: def
#    @month_lengths.deleter
#    def month_lengths(self):        
#        self.delprop('month_lengths')
#
    # ----------------------------------------------------------------
    # CF property
    # ----------------------------------------------------------------
    @property
    def standard_name(self):
        '''

The standard_name CF property.

.. versionadded:: 2.0 

:Examples:

>>> c.standard_name = 'time'
>>> c.standard_name
'time'
>>> del c.standard_name

>>> c.setprop('standard_name', 'time')
>>> c.getprop('standard_name')
'time'
>>> c.delprop('standard_name')

'''
        return self.getprop('standard_name')
    #--- End: def
    @standard_name.setter
    def standard_name(self, value): 
        self.setprop('standard_name', value)
    @standard_name.deleter
    def standard_name(self):       
        self.delprop('standard_name')

    # ----------------------------------------------------------------
    # CF property: units
    # ----------------------------------------------------------------
    # DCH possible inconsistency when setting self.Units.units ??
    @property
    def units(self):
        '''

The units CF property.

This property is a mirror of the units stored in the `Units`
attribute.

.. versionadded:: 2.0 

:Examples:

>>> c.units = 'degrees_east'
>>> c.units
'degree_east'
>>> del c.units

>>> c.setprop('units', 'days since 2004-06-01')
>>> c.getprop('units')
'days since 2004-06-01'
>>> c.delprop('units')

'''
        return Variable.units.fget(self)
    #--- End: def

    @units.setter
    def units(self, value):
        Variable.units.fset(self, value)

        if self._hasbounds:
            # Set the units on the bounds        
            self.bounds.setprop('units', value)

        self._direction = None
    #--- End: def
    
    @units.deleter
    def units(self):
        Variable.units.fdel(self)
                
        self._direction = None
        
        if self._hasbounds:
            # Delete the units from the bounds
            try:                
                self.bounds.delprop('units')
            except AttributeError:
                pass
    #--- End: def

    def chunk(self, chunksize=None):
        '''

Partition the data array.

.. versionadded:: 2.0 

'''         
        if not chunksize:
            # Set the default chunk size
            chunksize = CHUNKSIZE()
            
        # Partition the variable's data
        super(BoundedVariable, self).chunk(chunksize)

        # Partition the data of the bounds, if they exist.
        if self._hasbounds:
            self.bounds.chunk(chunksize)
    #--- End: def

#    def clip(self, a_min, a_max, units=None, i=False):
#        '''
#
#Clip (limit) the values in the data array and its bounds in place.
#
#Given an interval, values outside the interval are clipped to the
#interval edges.
#
#.. versionadded:: 2.0 
#
#Parameters :
# 
#    a_min : scalar
#
#    a_max : scalar
#
#    units : str or Units
#
#    {+i}
#
#:Returns: 
#
#    None
#
#:Examples:
#
#'''
#        c = super(BoundedVariable, self).clip(a_min, a_max, units=units, i=i)
#        
#        if c._hasbounds:
#            # Clip the bounds
#            c.bounds.clip(a_min, a_max, units=units, i=True)
#            
#        return c
#    #--- End: def
  
#    def close(self):
#        '''
#
#Close all files referenced by the bounded variable.
#
#Note that a closed file will be automatically reopened if its contents
#are subsequently required.
#
#.. versionadded:: 2.0 
#
#:Returns:
#
#    None
#
#:Examples:
#
#>>> c.close()
#
#'''
#        new = super(BoundedVariable, self).close()
#        
#        if self._hasbounds:
#            self.bounds.close()
#    #--- End: def

    @classmethod
#    def concatenate(cls, variables, axis=0, _preserve=True):
#        '''
#Join a sequence of bounded variables together.
#
#.. versionadded:: 2.0 
#
#:Returns:
#
#    out : cf.{+Variable}
#
#'''      
#        variable0 = variables[0]
#
#        if len(variables) == 1:
#            return variables.copy()
#
#        out = Variable.concatenate(variables, axis=axis,
#                                   _preserve=_preserve)
#        
#        if variable0._hasbounds:
#            bounds = Variable.concatenate(
#                [v.bounds for v in variables],
#                axis=axis, _preserve=_preserve)
#
#            out.insert_bounds(bounds, copy=False)
#        
#        return out
#    #--- End: def

    def contiguous(self, overlap=True):
        '''Return True if a {+variable} has contiguous cells.

A {+variable} is contiguous if its cell boundaries match up, or
overlap, with the boundaries of adjacent cells.

In general, it is only possible for a zero, 1 or 2 dimensional
{+variable} with bounds to be contiguous. A size 1 {+variable} with
any number of dimensions is always contiguous.

An exception occurs if the {+variable} is multdimensional and has more
than one element.

.. versionadded:: 2.0 

:Parameters:

    overlap : bool, optional    
        If False then overlapping cell boundaries are not considered
        contiguous. By default cell boundaries are considered
        contiguous.

:Returns:

    out: `bool`
        Whether or not the {+variable} is contiguous.

:Raises:

    ValueError:
        If the {+variable} has more than one dimension.

:Examples:

>>> c.hasbounds
False
>>> c.contiguous()
False

>>> print c.bounds[:, 0]
[  0.5   1.5   2.5   3.5 ]
>>> print c.bounds[:, 1]
[  1.5   2.5   3.5   4.5 ]
>>> c.contiuous()
True

>>> print c.bounds[:, 0]
[  0.5   1.5   2.5   3.5 ]
>>> print c.bounds[:, 1]
[  2.5   3.5   4.5   5.5 ]
>>> c.contiuous()
True
>>> c.contiuous(overlap=False)
False

        '''
        if not self._hasbounds:
            return False

        return self.bounds.contiguous(overlap=overlap, direction=self.direction)

#        if monoyine:
#            return self.monit()#
#
#        return False
    #--- End: def

    def convert_reference_time(self, units=None,
                               calendar_months=False,
                               calendar_years=False, i=False):
        '''Convert reference time data values to have new units.

Conversion is done by decoding the reference times to date-time
objects and then re-encoding them for the new units.

Any conversions are possible, but this method is primarily for
conversions which require a change in the date-times originally
encoded. For example, use this method to reinterpret data values in
units of "months" since a reference time to data values in "calendar
months" since a reference time. This is often necessary when when
units of "calendar months" were intended but encoded as "months",
which have special definition. See the note and examples below for
more details.

For conversions which do not require a change in the date-times
implied by the data values, this method will be considerably slower
than a simple reassignment of the units. For example, if the original
units are ``'days since 2000-12-1'`` then ``c.Units = cf.Units('days
since 1901-1-1')`` will give the same result and be considerably
faster than ``c.convert_reference_time(cf.Units('days since
1901-1-1'))``

.. note::
   It is recommended that the units "year" and "month" be used
   with caution, as explained in the following excerpt from the CF
   conventions: "The Udunits package defines a year to be exactly
   365.242198781 days (the interval between 2 successive passages of
   the sun through vernal equinox). It is not a calendar year. Udunits
   includes the following definitions for years: a common_year is 365
   days, a leap_year is 366 days, a Julian_year is 365.25 days, and a
   Gregorian_year is 365.2425 days. For similar reasons the unit
   ``month``, which is defined to be exactly year/12, should also be
   used with caution.

:Examples 1:

>>> d = c.convert_reference_time()
    
:Parameters:

    units: `cf.Units`, optional
        The reference time units to convert to. By default the units
        are "days since the original reference time in the original
        calendar".

          *Example:*
            If the original units are ``'months since 2000-1-1'`` in
            the Gregorian calendar then the default units to convert
            to are ``'days since 2000-1-1'`` in the Gregorian
            calendar.

    calendar_months: `bool`, optional
        If True then treat units of ``'months'`` as if they were
        calendar months (in whichever calendar is originally
        specified), rather than a 12th of the interval between 2
        successive passages of the sun through vernal equinox
        (i.e. 365.242198781/12 days).

    calendar_years: `bool`, optional
        If True then treat units of ``'years'`` as if they were
        calendar years (in whichever calendar is originally
        specified), rather than the interval between 2 successive
        passages of the sun through vernal equinox (i.e. 365.242198781
        days).
        
    {+i}

:Returns: 
 
    out: `cf.{+Variable}` 
        The {+variable} with converted reference time data values.

:Examples 2:

>>> print c.Units
months since 2000-1-1
>>> print c.array
[1 3]
>>> print c.dtarray
[datetime.datetime(2000, 1, 31, 10, 29, 3, 831197)
 datetime.datetime(2000, 4, 1, 7, 27, 11, 493645)]
>>> print c.bounds.array
[[ 0  2]
 [ 2  4]]
>>> print c.bounds.dtarray
[[datetime.datetime(2000, 1, 1, 0, 0) datetime.datetime(2000, 3, 1, 20, 58, 7, 662441)]
 [datetime.datetime(2000, 3, 1, 20, 58, 7, 662441) datetime.datetime(2000, 5, 1, 17, 56, 15, 324889)]]
>>> c.convert_reference_time(calendar_months=True, i=True)
>>> print c.Units
days since 2000-1-1
>>> print c.array
[  31.,  91.]
>>> print c.dtarray
[datetime.datetime(2000, 2, 1, 0, 0)
 datetime.datetime(2000, 4, 1, 0, 0)]
>>> print c.bounds.dtarray
[[datetime.datetime(2000, 1, 1, 0, 0) datetime.datetime(2000, 3, 1, 0, 0)]
 [datetime.datetime(2000, 3, 1, 0, 0) datetime.datetime(2000, 5, 1, 0, 0)]]

        '''

        if i:
            c = self
        else:
            c = self.copy()

        super(BoundedVariable, c).convert_reference_time(
            units=units,
            calendar_months=calendar_months,
            calendar_years=calendar_years,
            i=True)

        if c._hasbounds:
            c.bounds.convert_reference_time(units=units,
                                            calendar_months=calendar_months,
                                            calendar_years=calendar_years,
                                            i=True)

        return c
    #--- End: def

#    def cos(self, i=False):
#        '''
#
#Take the trigonometric cosine of the data array and bounds in place.
#
#Units are accounted for in the calcualtion, so that the the cosine of
#90 degrees_east is 0.0, as is the sine of 1.57079632 radians. If the
#units are not equivalent to radians (such as Kelvin) then they are
#treated as if they were radians.
#
#The Units are changed to '1' (nondimensionsal).
#
#.. versionadded:: 2.0 
#
#:Parameters:
#
#    {+i}
#
#:Returns:
#
#    out : cf.{+Variable}
#
#:Examples:
#
#>>> c.Units
#<CF Units: degrees_east>
#>>> print c.array
#[[-90 0 90 --]]
#>>> c.cos()
#>>> c.Units
#<CF Units: 1>
#>>> print c.array
#[[0.0 1.0 0.0 --]]
#
#>>> c.Units
#<CF Units: m s-1>
#>>> print c.array
#[[1 2 3 --]]
#>>> c.cos()
#>>> c.Units
#<CF Units: 1>
#>>> print c.array
#[[0.540302305868 -0.416146836547 -0.9899924966 --]]
#
#'''
#        if i:
#            c = self
#        else:
#            c = self.copy()
#
#        super(BoundedVariable, c).cos(i=True)
#
#        if c._hasbounds:
#            c.bounds.cos(i=True)
#
#        return c
#    #--- End: def
#
#    def cyclic(self, axes=None, iscyclic=True):
#        '''
#
#Set the cyclicity of axes of the data array and bounds.
#
#.. versionadded:: 2.0 
#
#.. seealso:: `cf.DimensionCoordinate.period`
#
#:Parameters:
#
#    axes : (sequence of) int
#        The axes to be set. Each axis is identified by its integer
#        position. By default no axes are set.
#        
#    iscyclic: bool, optional
#
#:Returns:
#
#    out : list
#
#:Examples:
#
#'''
#        old = super(BoundedVariable, self).cyclic(axes, iscyclic)
#
#        if axes is not None and self._hasbounds:
#            axes = self._parse_axes(axes)
#            self.bounds.cyclic(axes, iscyclic)
#
#        return old
#    #--- End: def

    def direction(self):
        '''
    
Return None, indicating that it is not specified whether the
values are increasing or decreasing.

.. versionadded:: 2.0 

:Returns:

    None
        
:Examples:

>>> print c.direction()
None

''' 
        return
    #--- End: def

#    def tan(self, i=False):
#        '''
#
#Take the trigonometric tangent of the data array and bounds in place.
#
#Units are accounted for in the calculation, so that the the tangent of
#180 degrees_east is 0.0, as is the sine of 3.141592653589793
#radians. If the units are not equivalent to radians (such as Kelvin)
#then they are treated as if they were radians.
#
#The Units are changed to '1' (nondimensionsal).
#
#.. versionadded:: 2.0 
#
#:Parameters:
#
#    {+i}
#
#:Returns:
#
#    out : cf.{+Variable}
#
#:Examples:
#
#'''
#        if i:
#            c = self
#        else:
#            c = self.copy()
#
#        super(BoundedVariable, c).tan(i=True)
#
#        if c._hasbounds:
#            c.bounds.tan(i=True)
#
#        return c
#    #--- End: def

#    def copy(self, _omit_Data=False, _only_Data=False):
#        '''
#        
#Return a deep copy.
#
#Equivalent to ``copy.deepcopy(c)``.
#
#.. versionadded:: 2.0 
#
#:Returns:
#
#    out :
#        The deep copy.
#
#:Examples:
#
#>>> d = c.copy()
#
#'''
#        new = super(BoundedVariable, self).copy(_omit_Data=_omit_Data,
#                                                _only_Data=_only_Data,
#                                                _omit_special=('bounds',))
#
#        if self._hasbounds:
#            bounds = self.bounds.copy(_omit_Data=_omit_Data,
#                                      _only_Data=_only_Data)
#            new._set_special_attr('bounds', bounds)        
#
#        return new
#    #--- End: def

    def delprop(self, prop):
        '''

Delete a CF property.

.. versionadded:: 2.0 

.. seealso:: `getprop`, `hasprop`, `setprop`

:Parameters:

    prop : str
        The name of the CF property.

:Returns:

     None

:Examples:

>>> c.delprop('standard_name')
>>> c.delprop('foo')
AttributeError: {+Variable} doesn't have CF property 'foo'

'''
        # Delete a special attribute
        if prop in self._special_properties:
            delattr(self, prop)
            return

        # Still here? Then delete a simple attribute

        # Delete selected simple properties from the bounds
        if self._hasbounds and prop in ('standard_name', 'axis', 'positive',
                                        'leap_month', 'leap_year',
                                        'month_lengths'):
            try:
                self.bounds.delprop(prop)
            except AttributeError:
                pass
        #--- End: if

        d = self._private['simple_properties']
        if prop in d:
            del d[prop]
        else:
            raise AttributeError("Can't delete non-existent %s CF property %r" %
                                 (self.__class__.__name__, prop))
    #--- End: def

    def dump(self, display=True, omit=(), field=None, key=None,
             _level=0, _title=None): 
        '''

Return a string containing a full description of the variable.

.. versionadded:: 2.0 

:Parameters:

    display: `bool`, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``c.dump()`` is equivalent to
        ``print c.dump(display=False)``.

    omit: sequence of `str`
        Omit the given CF properties from the description.

:Returns:

    out : None or str
        A string containing the description.

:Examples:

'''
        indent0 = '    ' * _level
        indent1 = '    ' * (_level+1)

        if _title is None:
            string = ['{0}Bounded Variable: {1}'.format(indent0, self.name(''))]
        else:
            string = [indent0 + _title]

        if self._simple_properties():
            string.append(self._dump_simple_properties(_level=_level+1))

        if self._hasData:
            if field and key:
                x = ['{0}({1})'.format(field.axis_name(axis), field.axis_size(axis))
                     for axis in field.item_axes(key)]
            else:
                x = [str(s) for s in self.shape]

            string.append('{0}Data({1}) = {2}'.format(indent1,
                                                      ', '.join(x),
                                                      str(self.Data)))
        #--- End: if

        if self._hasbounds:
            x.append(str(self.bounds.shape[-1]))
            string.append('{0}Bounds({1}) = {2}'.format(indent1,
                                                        ', '.join(x),
                                                        str(self.bounds.Data)))
        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

#    def expand_dims(self, position=0, i=False):
#        '''Insert a size 1 axis.
#
#.. versionadded:: 2.0 
#
#.. seealso:: `flip`, `squeeze`, `transpose`
#
#:Parameters:
#
#    position : int, optional
#        Specify the position amongst the data array axes where the new
#        axis is to be inserted. By default the new axis is inserted at
#        position 0, the slowest varying position.
#
#    {+i}
#
#:Returns:
#
#    out : cf.{+Variable}
#
#        '''
#        if (not self._hasData and
#            (not self._hasbounds or not self.bounds._hasData)):
#            raise ValueError(
#                "Can't insert axis into {!r}".format(self.__class__.__name__))
#
#        if self._hasData:
#            c = super(BoundedVariable, self).expand_dims(position, i=i)
#        elif i:
#            c = self
#        else:
#            c = self.copy()
#
#        if c._hasbounds and c.bounds._hasData:
#            # Expand the bounds
#            position = self._parse_axes([position])[0]
#            c.bounds.expand_dims(position, i=True)
#
##        if i:
##            c = self
##        else:
##            c = self.copy()
##
##        # Expand the coordinate's data, if it has any.
##        if c._hasData:
###            super(Coordinate, self).expand_dims(position, i=True)
##            c.Data.expand_dims(position, i=True)
##
##        # Expand the coordinate's bounds, if it has any.
##        if c._hasbounds and c.bounds._hasData:
###            c.bounds.expand_dims(position, i=True)
##            c.bounds.Data.expand_dims(position, i=True)
#
#        return c
#    #--- End: def

    def flip(self, axes=None, i=False):
        '''Flip dimensions of the data array and bounds in place.

The trailing dimension of the bounds is flipped if and only if the
{+variable} is 1 or 0 dimensional.

.. versionadded:: 2.0 

:Parameters:

    axes : (sequence of) int, optional
        Flip the dimensions whose positions are given. By default all
        dimensions are flipped.

    {+i}

:Returns:

    out : cf.{+Variable}

:Examples:

>>> c.flip()
>>> c.flip(1)

>>> d = c[::-1, :, ::-1, :]
>>> c.flip([2, 0]).equals(d)
True

        '''
        c = super(BoundedVariable, self).flip(axes, i=i)

        # ------------------------------------------------------------
        # Flip the requested dimensions in the bounds, if it has any.
        #
        # As per section 7.1 in the CF conventions: i) if the variable
        # is 0 or 1 dimensional then flip all dimensions (including
        # the the trailing size 2 dimension); ii) if the variable has
        # 2 or more dimensions then do not flip the trailing
        # dimension.
        # ------------------------------------------------------------
        if c._hasbounds and c.bounds._hasData:
            # Flip the bounds
            if not c.ndim:
                # Flip the bounds of a 0-d variable
                axes = (-1,)
            elif c.ndim == 1:
                # Flip the bounds of a 1-d variable
                if axes in (0, -1):
                    axes = (0, -1)
                elif axes is not None:
                    axes = self._parse_axes(axes) + [-1]
            else:
                # Do not flip the bounds of an N-d variable (N >= 2)
                axes = self._parse_axes(axes)

            c.bounds.flip(axes, i=True)            
        #--- End if

        direction = c._direction
        if direction is not None:
            c._direction = not direction

        return c
    #--- End: def

#    def HDF_chunks(self, *chunksizes):
#        '''
#        '''
#        old_chunks = super(BoundedVariable, self).HDF_chunks(*chunksizes)
# 
#        if self._hasbounds:
#            self.bounds.HDF_chunks(*chunksizes)
#        
#        return old_chunks
#    #--- End: def
    
    def insert_bounds(self, bounds, copy=True):
        '''

Insert cell bounds.

.. versionadded:: 2.0

:Parameters:

    bounds:  data-like

        {+data-like}

    copy: `bool`, optional

:Returns:

    `None`

'''
        # Check dimensionality
        if bounds.ndim != self.ndim + 1:
            raise ValueError(
"Can't set bounds: Incorrect number of dimemsions: {0} (expected {1})".format(
    bounds.ndim, self.ndim+1))

        # Check shape
        if bounds.shape[:-1] != self.shape:
            raise ValueError(
                "Can't set bounds: Incorrect shape: {0} (expected {1})".format(
                    bounds.shape, self.shape+(bounds.shape[-1],)))

        if copy:            
            bounds = bounds.copy()

        # Check units
        units      = bounds.Units
        self_units = self.Units
        if units and not units.equivalent(self_units):
            raise ValueError(
"Can't set bounds: Incompatible units: Bounds units {0!r} are not equivalent to {1!r}".format(
    bounds.Units, self.Units))
            
        bounds.Units = self_units

        if not isinstance(bounds, Bounds):
            bounds = Bounds(source=bounds, copy=False)  

        # Copy selected properties to the bounds
        for prop in ('standard_name', 'axis', 'positive',
                     'leap_months', 'leap_years', 'month_lengths'):
            value = self.getprop(prop, None)
            if value is not None:
                bounds.setprop(prop, value)

        self._set_special_attr('bounds', bounds)        

        self._hasbounds = True
        self._direction = None
    #--- End: def

    def insert_data(self, data, bounds=None, copy=True):
        '''Insert a new data array.

A bounds data array may also inserted if given with the *bounds*
keyword. Bounds may also be inserted independently with the
`insert_bounds` method.

.. versionadded:: 2.0 

:Parameters:

    data : cf.Data

    bounds : cf.Data, optional

    copy : bool, optional

:Returns:

    None

        '''
        if data is not None:
            super(BoundedVariable, self).insert_data(data, copy=copy)

        if bounds is not None:
            self.insert_bounds(bounds, copy=copy)
#DCH
        self._direction = None
    #--- End: def

    def override_units(self, new_units, i=False):
        '''

.. versionadded:: 2.0 

    {+i}

'''
        if i:
            c = self
        else:
            c = self.copy()

        super(BoundedVariable, c).override_units(new_units, i=True)

        if c._hasbounds:
            c.bounds.override_units(new_units, i=True)

        if c._period is not None:
            # Never change _period in place
            c._period.override_units(new_units, i=False)

        return c
    #--- End: def

#    def roll(self, axis, shift, i=False):
#        '''
#
#.. versionadded:: 2.0 
#
#    {+i}
#'''      
#        if self.size <= 1:
#            if i:
#                return self
#            else:
#                return self.copy()
#
#        c = super(BoundedVariable, self).roll(axis, shift, i=i)
#
#        # Roll the bounds, if there are any
#        if c._hasbounds:
#            b = c.bounds
#            if b._hasData:
#                b.roll(axis, shift, i=True)
#        #--- End: if
#
#        return c
#    #--- End: def

    def setprop(self, prop, value):
        '''

Set a CF property.

.. versionadded:: 2.0 

.. seealso:: `delprop`, `getprop`, `hasprop`

:Parameters:

    prop : str
        The name of the CF property.

    value :
        The value for the property.

:Returns:

     None

:Examples:

>>> c.setprop('standard_name', 'time')
>>> c.setprop('foo', 12.5)

'''
        # Set a special attribute
        if prop in self._special_properties:
            setattr(self, prop, value)
            return

        # Still here? Then set a simple property
        self._private['simple_properties'][prop] = value

        # Set selected simple properties on the bounds
        if self._hasbounds and prop in ('standard_name', 'axis', 'positive', 
                                        'leap_month', 'leap_year',
                                        'month_lengths'):
#            if self.bounds.hasprop(prop):
            self.bounds.setprop(prop, value)
    #--- End: def

#    def sin(self, i=False):
#        '''
#
#Take the trigonometric sine of the data array and bounds in place.
#
#Units are accounted for in the calculation. For example, the the sine
#of 90 degrees_east is 1.0, as is the sine of 1.57079632 radians. If
#the units are not equivalent to radians (such as Kelvin) then they are
#treated as if they were radians.
#
#The Units are changed to '1' (nondimensionsal).
#
#.. versionadded:: 2.0 
#
#:Parameters:
#
#    {+i}
#
#:Returns:
#
#    out : cf.{+Variable}
#
#:Examples:
#
#>>> c.Units
#<CF Units: degrees_north>
#>>> print c.array
#[[-90 0 90 --]]
#>>> c.sin()
#>>> c.Units
#<CF Units: 1>
#>>> print c.array
#[[-1.0 0.0 1.0 --]]
#
#>>> c.Units
#<CF Units: m s-1>
#>>> print c.array
#[[1 2 3 --]]
#>>> c.sin()
#>>> c.Units
#<CF Units: 1>
#>>> print c.array
#[[0.841470984808 0.909297426826 0.14112000806 --]]
#
#'''
#        if i:
#            c = self
#        else:
#            c = self.copy()
#
#        super(BoundedVariable, c).sin(i=True)
#
#        if c._hasbounds:
#            c.bounds.sin(i=True)
#
#        return c
#    #--- End: def

#    def log(self, base=10, i=False):
#        '''
#
#Take the logarithm the data array and bounds element-wise.
#
#.. versionadded:: 2.0 
#
#:Parameters:
#
#    base : number, optional
#    
#    {+i}
#
#:Returns:
#
#    out : cf.{+Variable}
#
#'''
#        if i:
#            c = self
#        else:
#            c = self.copy()
#
#        super(BoundedVariable, c).log(base, i=True)
#
#        if c._hasbounds:
#            c.bounds.log(base, i=True)
#
#        return c
#    #--- End: def
#
#    def squeeze(self, axes=None, i=False):
#        '''
#
#Remove size 1 dimensions from the data array and bounds in place.
#
#.. versionadded:: 2.0 
#
#.. seealso:: `expand_dims`, `flip`, `transpose`
#
#:Parameters:
#
#    axes : (sequence of) int, optional
#        The size 1 axes to remove. By default, all size 1 axes are
#        removed. Size 1 axes for removal may be identified by the
#        integer positions of dimensions in the data array.
#
#    {+i}
#
#:Returns:
#
#    out : cf.{+Variable}
#
#:Examples:
#
#>>> c.squeeze()
#>>> c.squeeze(1)
#>>> c.squeeze([1, 2])
#
#'''
#        c = super(BoundedVariable, self).squeeze(axes, i=i)
#
#        if c._hasbounds and c.bounds._hasData:
#            # Squeeze the bounds
#            axes = self._parse_axes(axes)
#            c.bounds.squeeze(axes, i=True)
#
#        return c
#    #--- End: def

    def transpose(self, axes=None, i=False):
        '''Permute the dimensions of the data.

.. versionadded:: 2.0 

.. seealso:: `expand_dims`, `flip`, `squeeze`

:Parameters:

    axes : (sequence of) int, optional
        The new order of the data array. By default, reverse the
        dimensions' order, otherwise the axes are permuted according
        to the values given. The values of the sequence comprise the
        integer positions of the dimensions in the data array in the
        desired order.

    {+i}

:Returns:

    out : cf.{+Variable}

:Examples:

>>> c.ndim
3
>>> c.{+name}()
>>> c.{+name}([1, 2, 0])

        '''
        c = super(BoundedVariable, self).transpose(axes, i=i)

        ndim = c.ndim
        if c._hasbounds and ndim > 1 and c.bounds._hasData:
            # Transpose the bounds
            if axes is None:
                axes = range(ndim-1, -1, -1) + [-1]
            else:
                axes = self._parse_axes(axes) + [-1]
                
            bounds = c.bounds
            bounds.transpose(axes, i=True)

            if (ndim == 2 and
                bounds.shape[-1] == 4 and 
                axes[0] == 1 and 
                (c.Units.islongitude or c.Units.islatitude or
                 c.getprop('standard_name', None) in ('grid_longitude' or
                                                      'grid_latitude'))):
                # Swap columns 1 and 3 so that the values are still
                # contiguous (if they ever were). See section 7.1 of
                # the CF conventions.
                bounds[..., [1, 3]] = bounds[..., [3, 1]]
        #--- End: if

        return c
    #--- End: def

#--- End: class

class Bounds(Variable):
    '''

'''
    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def lower_bounds(self):
        '''The lower bounds in a `cf.Data` object.

``b.lower_bounds`` is equivalent to ``b.data.min(axes=-1)``.

.. versionadded:: 2.0 

.. seealso:: `upper_bounds`

:Examples:

>>> print b.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> b.lower_bounds
<CF Data: [3, ..., -1]>
>>> print b.lower_bounds.array
[ 3  1 -1]

        '''
        if not self._hasData:
            raise ValueError("Can't get lower bounds when there are no bounds")

        return self.data.min(-1).squeeze(-1, i=True)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def upper_bounds(self):
        '''

The upper bounds in a `cf.Data` object.

``b.upper_bounds`` is equivalent to ``b.data.max(axes=-1)``.

.. versionadded:: 2.0

.. seealso:: `lower_bounds`

:Examples:

>>> print b.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> b.upper_bounds      
<CF Data: [5, ..., 1]>
>>> b.upper_bounds.array     
array([5, 3, 1])

'''
        if not self._hasData:
            raise ValueError("Can't get upper bounds when there are no bounds")

        return self.data.max(-1).squeeze(-1, i=True)
    #--- End: def

    def contiguous(self, overlap=True, direction=None):
        '''Return True if the bounds are contiguous.

Bounds are contiguous if the cell boundaries match up, or
overlap, with the boundaries of adjacent cells.

In general, it is only possible for 1 or 0 variable dimensional
variables with bounds to be contiguous, but size 1 variables with any
number of dimensions are always contiguous.

An exception is raised if the variable is multdimensional and has more
than one element.

.. versionadded:: 2.0

        '''
        if not self._hasData:
            return False    

        nbounds = self.shape[-1]

        if self.size == nbounds:
            return True

        if nbounds == 4 and self.ndim ==3:
            if overlap == True:
                raise ValueError(
                    "overlap=True and can't tell if 2-d bounds are contiguous")
            bnd = self.array
            for j in xrange(self.shape[0] - 1):
                for i in xrange(self.shape[1] - 1):
                    # check cells (j, i) and cells (j, i+1) are contiguous
                    if bnd[j,i,1] != bnd[j,i+1,0] or \
                       bnd[j,i,2] != bnd[j,i+1,3]:
                        return False
                    # check cells (j, i) and (j+1, i) are contiguous
                    if bnd[j,i,3] != bnd[j+1,i,0] or \
                       bnd[j,i,2] != bnd[j+1,i,1]:
                        return False
            return True

        if nbounds > 2 or self.ndim > 2:
            raise ValueError(
"Can't tell if multidimensional bounds are contiguous")

        data = self.Data
        
        if not overlap: 
            return data[1:, 0].equals(data[:-1, 1])
        else:
            if direction is None:
                b = data[(0,)*(data.ndim-1)].array
                direction =  b.item(0,) < b.item(1,)
        
            if direction:
                return (data[1:, 0] <= data[:-1, 1]).all()
            else:
                return (data[1:, 0] >= data[:-1, 1]).all()
    #--- End: def

#--- End: class


# ====================================================================
#
# SubspaceBoundedVariable object
#
# ====================================================================

class SubspaceBoundedVariable(SubspaceVariable):

    __slots__ = []

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

'''
        variable = self.variable

        if indices is Ellipsis:
            return variable.copy()

        # Parse the index
        if not isinstance(indices, tuple):
            indices = (indices,)

        arg0 = indices[0]
        if isinstance(arg0, basestring) and arg0 == 'mask':
            auxiliary_mask = indices[:2]
            indices2       = indices[2:]
        else:
            auxiliary_mask = None
            indices2       = indices
          
        indices, roll = parse_indices(variable.shape, indices2, cyclic=True)

        if roll:
            data = variable.Data
            axes = data._axes
            cyclic_axes = data._cyclic
            for iaxis, shift in roll.iteritems():
                if axes[iaxis] not in cyclic_axes:
                    raise IndexError(
                        "Can't do a cyclic slice on a non-cyclic axis")

                variable = variable.roll(iaxis, shift)
            #--- End: for
            new = variable
        else:
            new = variable.copy(_omit_Data=True)

        variable_data = variable.Data

        if auxiliary_mask:
            findices = tuple(auxiliary_mask) + tuple(indices)
        else:
            findices = tuple(indices)

        if _debug:
            cname = self.__class__.__name__
            print '{}.__getitem__: shape    = {}'.format(cname, variable.shape)
            print '{}.__getitem__: indices2 = {}'.format(cname, indices2)
            print '{}.__getitem__: indices  = {}'.format(cname, indices)
            print '{}.__getitem__: findices = {}'.format(cname, findices)

        new.Data = variable_data[findices]

        # Subspace the bounds, if there are any
        if not new._hasbounds:
            bounds = None
        else:
            bounds = variable.bounds
            if bounds._hasData:
                findices = list(findices)
                if variable_data.ndim <= 1:
                    index = indices[0]
                    if isinstance(index, slice):
                        if index.step < 0:
                            # This scalar or 1-d variable has been
                            # reversed so reverse its bounds (as per
                            # 7.1 of the conventions)
                            findices.append(slice(None, None, -1))
                    elif variable_data.size > 1 and index[-1] < index[0]:
                        # This 1-d variable has been reversed so
                        # reverse its bounds (as per 7.1 of the
                        # conventions)
                        findices.append(slice(None, None, -1))                    
                #--- End: if

                if auxiliary_mask:
                    findices[1] = [mask.expand_dims(-1) for mask in findices[1]]

                if _debug:
                    print '{}.__getitem__: findices for bounds ='.format(self.__class__.__name__, findices)
                
                new.bounds.Data = bounds.Data[tuple(findices)]
        #--- End: if

        new._direction = None

        # Return the new bounded variable
        return new
    #--- End: def

#--- End: class
