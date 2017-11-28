from copy import deepcopy
from re   import match as re_match
from itertools import izip
from operator import __and__ as operator_and
from operator import __or__  as operator_or

from numpy import ndarray   as numpy_ndarray
from numpy import vectorize as numpy_vectorize

from .cfdatetime import Datetime, dt
from .functions  import inspect    as cf_inspect
from .functions  import equals     as cf_equals
from .functions  import equivalent as cf_equivalent

from .data.data import Data

# ====================================================================
#
# Query object
#
# ====================================================================

class Query(object):
    '''Store a query operation.

The query operation is an operator with a right hand side operand. For
example, an operator could be "strictly less than" and a right hand
side operand could 3.

Such a query (such as "is strictly less than 3?") may be evaluated for
an arbitrary left hand side operand, *x* (such as "is *x* strictly
less than 3?").

The result of the query is dependent on the object type of left hand
side operand, *x*. For example, if *x* is an integer then evaluating
"is *x* strictly less than 3?" will result in a boolean; but if *x* is
a `numpy` array then "is *x* strictly less than 3?" will likely
produce a numpy array of booleans.

The query is evaluated with its `evaluate` method or equivalently with
the ``==`` operator:

>>> q = cf.Query('lt', 3)
>>> q.evaluate(2)
True
>>> 2 == q
True
>>> q == 2
True
>>> 4 == q
False

The inverse of the query may be evaluated with the ``!=`` operator:

>>> q = cf.Query('wi', [3, 5])
>>> q.evaluate(4)
True
>>> 4 == q
True
>>> 4 != q
False
>>> q != 6
True

The following operators are supported:

=============  =========================================================  ============
operator       Description                                                Constructor
=============  =========================================================  ============
``'lt'``       Is *x* strictly less than a value?                         `cf.lt`
               
``'le'``       Is *x* less than or equal to a value?                      `cf.le`
               
``'gt'``       Is *x* strictly greater than a value?                      `cf.gt`
               
``'ge'``       Is *x* greater than or equal to a value?                   `cf.ge`
               
``'eq'``       Is *x* equal to a value?                                   `cf.eq`
               
``'ne'``       Is *x* not equal to a value?                               `cf.ne`
               
``'wi'``       Is *x* within a given range of values (range bounds        `cf.wi`
               included)?
               
``'wo'``       Is *x* without a given range of values (range bounds       `cf.wo`
               excluded)?       
               
``'set'``      Is *x* equal to any member of a collection?                `cf.set`

``'contain'``  If cells are defined, is value contained in a cell of      `cf.contain`
               *x*? otherwise is *x* equal to a value?
=============  =========================================================  ============

For the ``'wi'``, ``'wo '`` and ``'set'`` operators, if the left hand
side operand supports broadcasting over its elements (such as a
`numpy` array or a `cf.Field` object) then each element is tested
independently. For example:

>>> q = cf.Query('wi', [3, 4])
>>> q == [2, 3, 4]
False
>>> print q == numpy.array([2, 3, 4])
[ False  True  True]

As a convenience, for each operator there is an identically named
constructor function which returns the appropriate `cf.Query`
object. For example:

>>> cf.lt(3)
<CF Query: lt 3>


**Compound queries**

Multiple queries may be logically combined with the bitwise ``&`` and
``|`` operators to form a new `cf.Query` object. For example:

>>> q = cf.ge(3)
>>> r = cf.lt(5)
>>> s = q & r
>>> s 
>>> <CF Query: [(ge 3) & (lt 5)]>
>>> 4 == s
True
>>> t = q | r
>>> t
<CF Query: [(ge 3) | (lt 5)]>
>>> 2 == t
True

Compound queries may be combined further:

>>> u = s | cf.wi(1.5, 2.5)
>>> u
<CF Query: [[(ge 3) & (lt 5)] | (wi (1.5, 2.5))]>
>>> 2 == u
True
>>> u & t
<CF Query: [[[(ge 3) & (lt 5)] | (wi (1.5, 2.5))] & [(ge 3) | (lt 5)]]>

If any of the component queries are for left hand side operand
attributes, then these are retained in a compound query. For example:

>>> q = cf.ge(3)
>>> r = cf.lt(5, attr='bar')
>>> s = q & r
>>> s = e.addattr('foo')
>>> s
<CF Query: foo[(ge 3) & bar(lt 5)]>

In this example,

>>> x == s

is equivalent to 

>>> (x.foo == cf.ge(3)) & (x.foo.bar == cf.lt(5))


**Attributes**

===============  ======================================================
Attribute        Description
===============  ======================================================
`!attr`          An attribute name such that this attribute of the
                 left hand side operand is compared, rather than the
                 operand itself. If there is more than one attribute
                 name then each is interpreted as an attribute of the
                 previous attribute.

`!operator`      The query operation (such as ``'lt'``, for
                 example). Always `None` for compound queries.

`exact`          If False then string values are treated as a regular
                 expressions as understood by the :py:obj:`re` module
                 and are evaluated using the :py:obj:`re.match`
                 method. Ignored for all operators except ``'eq'``,
                 ``'ne'`` and ``'set'``.
===============  ======================================================

    '''

    def __init__(self, operator, value, units=None, exact=True, attr=None):
        '''**Initialization**

:Parameters:

    operator: `str`
        The query operator.

    value:
        The right hand side of the query operation.

    units: `str` or `cf.Units`, optional
        The units of *value*. By default, the same units, if any, as
        the left hand side of the query operation are assumed.

    exact: `bool`, optional
        If False then string values are treated as a regular
        expressions as understood by the :py:obj:`re` module and are
        evaluated using the :py:obj:`re.match` method. Ignored for
        all operators except ``'eq'``, ``'ne'`` and ``'set'``.

    attr: `str`, optional
        Specify an attribute (or an attribute of an attribute, etc.)
        of a left hand side operand which is compared, rather than the
        operand itself.

          *Example:*
            ``cf.Query('ge', 2, attr='ndim')`` will return True when
            evaluated for a numpy array with two or more dimensions.

          *Example:* 
            ``q=cf.Query('ge', 2, attr='lower_bounds.month')`` will
            compare the `month` attribute of the `lower_bounds`
            attribute. I.e. ``q==x`` is equivalent to ``cf.Query('ge',
            2)==x.lower_bounds.month``.

:Examples:

>>> cf.Query('le', 5.6)
<CF Query: (le 5.6)>
>>> cf.Query('gt', 5.6, 'metres')
<CF Query: (gt <CF Data: 5.6 metres>)>
>>> cf.Query('gt', cf.Data(5.6, 'metres'))
<CF Query: (gt <CF Data: 5.6 metres>)>
>>> cf.Query('wi', [2, 56])
<CF Query: (wi [2, 56])>
>>> cf.Query('set', [2, 56], 'seconds')
<CF Query: (set <CF Data: [2, 56] seconds>)>
>>> cf.Query('set', cf.Data([2, 56], 'seconds'))
<CF Query: (set <CF Data: [2, 56] seconds>)>
>>> cf.Query('eq', 'air_temperature')
<CF Query: (eq 'air_temperature')>
>>> cf.Query('eq', 'temperature', exact=False)
<CF Query: (eq 'temperature')>
>>> cf.Query('gt', 1, attr='ndim')
<CF Query: ndim(gt 1)>

        '''
        if units is not None:
            value_units = getattr(value, 'Units', None)
            if value_units is None:
                value = Data(value, units)
            elif not value_units.equivalent(units):
                raise ValueError("sdfsdfsd99885109^^^^")
        #--- End: if

        self._operator = operator
        self._value    = value
        self._exact    = exact
        self._compound = False

#        self._attr     = () if not attr else (attr,)
        if attr:
            self._attr = tuple(attr.split('.'))
        else:
            self._attr = ()

        self._bitwise_operator = None

        self._NotImplemented_RHS_Data_op = True
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __eq__(self, x):
        '''

x.__eq__(y) <==> x==y <==> x.evaluate(y)

'''
        return self._evaluate(x, ())
    #--- End: def

    def __ne__(self, x):
        '''

x.__ne__(y) <==> x!=y <==> (x==y)==False

'''
        return self._evaluate(x, ()) == False
    #--- End: def

    def __ge__(self, x):
        raise TypeError("Unsupported operand type(s) for >=: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __gt__(self, x):
        raise TypeError("Unsupported operand type(s) for >: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __le__(self, x):
        raise TypeError("Unsupported operand type(s) for <=: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __lt__(self, x):
        raise TypeError("Unsupported operand type(s) for <: '%s' and '%s'" %
                        (self.__class__.__name__, x.__class__.__name__))
    #--- End: def

    def __and__(self, other):
        '''

x.__and__(y) <==> x&y

'''        

        Q = type(self)
        new = Q.__new__(Q)
        
        new._operator         = None
        new._exact            = True
        new._compound         = (self, other)
        new._bitwise_operator = operator_and
        new._attr             = ()

        new._NotImplemented_RHS_Data_op = True
       
        return new
    #--- End: def

    def __iand__(self, other):
        '''

x.__iand__(y) <==> x&=y

'''        
        return self & other
    #--- End: def

    def __or__(self, other):
        '''

x.__or__(y) <==> x|y

'''                
        Q = type(self)
        new = Q.__new__(Q)
        
        new._operator         = None
        new._exact            = True
        new._compound         = (self, other)
        new._bitwise_operator = operator_or
        new._attr             = ()

        new._NotImplemented_RHS_Data_op = True

        return new
    #--- End: def

    def __ior__(self, other):
        '''

x.__ior__(y) <==> x|=y

'''    
        return self | other            
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return '<CF %s: %s>' % (self.__class__.__name__, self)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        attr = '.'.join(self._attr)

        if not self._compound:
            if not self._exact:
                out = '%s(%s match(%r))' % (attr, self._operator, self._value)
            else:
                out = '%s(%s %r)' % (attr, self._operator, self._value) 
        else:
            bitwise_operator = repr(self._bitwise_operator)
            if '__and__' in bitwise_operator:
                bitwise_operator = '&'
            elif '__or__' in bitwise_operator:
                bitwise_operator = '|'

            out = '%s[%s %s %s]' % (attr, self._compound[0], bitwise_operator,
                                    self._compound[1])
        #--- End: if

        return out
    #--- End: def

    @property
    def attr(self):
        '''



:Examples:

>>> q = cf.Query('ge', 4)
>>> print q.attr
None
>>> q = cf.Query('le', 6, attr='year')
>>> q.attr
'year'
>>> q.addattr('foo')
>>> q.attr
'year'asdasdas

'''
        return self._attr
    #--- End: def

    @property
    def operator(self):
        '''

:Examples:

>>> q = cf.Query('ge', 4)
>>> q.operator
'ge'
>>> q |= cf.Query('le', 6)
>>> print q.operator
None

'''
        return self._operator
    #--- End: def

    @property
    def exact(self):
        '''

:Examples:

>>> q = cf.Query('eq', 'foo')
>>> q.exact
True
>>> q = cf.Query('eq', '.*foo', exact=False)
>>> q.exact
False
>>> q |= cf.Query('eq', 'bar')
>>> print q.exact
False
'''
        return self._exact
    #--- End: def

    @property
    def value(self):
        '''

:Examples:

>>> q = cf.Query('ge', 4)
>>> q.value
4
>>> q |= cf.Query('le', 6)
>>> q.value
AttributeError: Compound query doesn't have attribute 'value'

'''
        if not self._compound:
            return self._value

        raise AttributeError("Compound query doesn't have attribute 'value'")
    #--- End: def

    def addattr(self, attr):
        '''Return a `cf.Query` object with a new left hand side operand
attribute to be used during evaluation.

If another attribute has previously been specified, then the new
attribute is considered to be an attribute of the existing attribute.

:Parameters:

    attr: str
        The attribute name.

:Returns:

    out: cf.Query
        The new query object.

:Examples:

>>> q = cf.eq(2001)
>>> q
<CF Query: (eq 2001)>
>>> q = q.addattr('year')
>>> q
<CF Query: year(eq 2001)>

>>> q = cf.lt(2)
>>> q = q.addattr('A')
>>> q = q.addattr('B')
>>> q
<CF Query: A.B(lt 2)>
>>> q = q.addattr('C')
>>> q
<CF Query: A.B.C(lt 2)>

        '''
        Q = type(self)
        new = Q.__new__(Q)

        new.__dict__ = self.__dict__.copy()
        new._attr += (attr,)

        new._NotImplemented_RHS_Data_op = True

        return new
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``q.copy()`` is equivalent to ``copy.deepcopy(q)``.

:Returns:

    out :
        The deep copy.

:Examples:

>>> r = q.copy()

'''
        return self
    #--- End: def

    def dump(self, display=True):
        '''
        
Return a string containing a full description of the instance.

:Parameters:

    display: bool, optional
        If False then return the description as a string. By default
        the description is printed, i.e. ``q.dump()`` is equivalent to
        ``print q.dump(display=False)``.

:Returns:

    out: None or str
        A string containing the description.

:Examples:

'''      
        string = str(self)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def equals(self, other, traceback=False):
        '''
'''        
        if self._compound:
            if not other._compound:
                return False

            if self._bitwise_operator != other._bitwise_operator:
                return False
                
            if not self._compound[0].equals(other._compound[0]):
                if not self._compound[0].equals(other._compound[1]):
                    return False
                if not self._compound[1].equals(other._compound[0]):
                    return False
            elif not self._compound[1].equals(other._compound[1]):
                return False        
   
        elif other._compound:
            return False
                
        for attr in ('_NotImplemented_RHS_Data_op',
                     '_attr',
                     '_value',
                     '_operator',
                     '_exact'):
            if not cf_equals(getattr(self, attr, None),
                             getattr(other, attr, None),
                             traceback=traceback):
                return False
        #--- End: for

        return True
    #--- End: def

    def equivalent(self, other, traceback=False):
        '''
'''
        for attr, value in self.__dict__.iteritems():
            if not cf_equivalent(value, getattr(other, attr),
                                 traceback=traceback):
                return False
        #--- End: for

        return True
    #--- End: def

    def evaluate(self, x):
        '''

Evaluate the query operation for a given left hand side operand.

Note that for the query object ``q`` and any object, ``x``, ``x==q``
is equivalent to ``q.evaluate(x)`` and ``x!=q`` is equivalent to
``q.evaluate(x)==False``.

:Parameters:

    x: 
        The object for the left hand side operand of the query.

:Returns:

    out: 
        The result of the query. The nature of the result is dependent
        on the object type of *x*.
    
:Examples:

>>> q = cf.Query('lt', 5.5)
>>> q.evaluate(6)
False

>>> q = cf.Query('wi', (1,2))
>>> array = numpy.arange(4)
>>> array
array([0, 1, 2, 3])
>>> q.evaluate(array)
array([False,  True,  True, False], dtype=bool)

'''
        return self._evaluate(x, ())
    #--- End: def

    def _evaluate(self, x, parent_attr):
        '''

Evaluate the query operation for a given object.

.. seealso:: `evaluate`

:Parameters:

    x:
        See `evaluate`.

    parent_attr: `tuple`
       

:Returns:

    out: 
        See `evaluate`.
    
:Examples:

'''        
        compound = self._compound
        attr     = parent_attr + self._attr

        if compound:
            c = compound[0]._evaluate(x, attr)
            d = compound[1]._evaluate(x, attr)
            return self._bitwise_operator(c, d)
        #--- End: if

        # Still here?

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        for a in attr:
            x = getattr(x, a)
            
        operator = self._operator
        value    = self._value
        if operator == 'eq':
            if not self._exact:
                if not isinstance(x, basestring):
                    raise ValueError("Can't re.match on non-string")

                return bool(re_match(value, x))
            else:
                return x == value
        #--- End: if           
        
        if operator == 'ne':
            if not self._exact:
                if not isinstance(x, basestring):
                    raise ValueError("Can't re.match on non-string")

                return not re_match(value, x)
            else:
                return x != value
        #--- End: if
        
        if operator == 'lt':  
            _lt = getattr(x, '_query_lt', None)
            if _lt is not None:
                return _lt(value)

            return x < value
        #--- End: if
        
        if operator == 'le':
            _le = getattr(x, '_query_le', None)
            if _le is not None:
                return _le(value)

            return x <= value
        #--- End: if
        
        if operator == 'gt':            
            _gt = getattr(x, '_query_gt', None)
            if _gt is not None:
                return _gt(value)

            return x > value
        #--- End: if
        
        if operator == 'ge':            
            _ge = getattr(x, '_query_ge', None)
            if _ge is not None:
                return _ge(value)

            return x >= value
        #--- End: if

        if operator == 'wi':
            _wi = getattr(x, '_query_wi', None)
            if _wi is not None:
                return _wi(value[0], value[1])
            
            return (x >= value[0]) & (x <= value[1])
        #--- End: if

        if operator == 'wo':
            _wo = getattr(x, '_query_wo', None)
            if _wo is not None:
                return _wo(value[0], value[1])
            
            return (x < value[0]) | (x > value[1])
        #--- End: if

        if operator == 'contain':
            _contain = getattr(x, '_query_contain', None)
            if _contain is not None:
                return _contain(value)
            else:
                return x == value
        #--- End: if           

        if operator == 'set':
            _set = getattr(x, '_query_set', None)
            if _set is not None:
                return _set(value, self._exact)

            i = iter(value)
            v = i.next()
            if not self._exact:
                if not isinstance(x, basestring):
                    raise ValueError("Can't, as yet, regex on non string")
                
                if re_match(v, x):
                    return True
                
                for v in i:
                    if re_match(v, x):
                        return True
                    
                return False
            else:
                out = (x == v)
                for v in i:
                    out |= (x == v)

                return out
        #--- End: if    
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

#--- End: class


def lt(value, units=None, attr=None):
    '''Return a `cf.Query` object for a variable for being strictly less
than a value.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`,
             `cf.le`, `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value: object
        The value which a variable is to be compared with.

    units: str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr: str, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: cf.Query
        The query object.

:Examples:

>>> q = cf.lt(5)
>>> q
<CF Query: x lt 5>
>>> q.evaluate(4)
True
>>> q.evaluate(5)
False

    '''
    return Query('lt', value, units=units, attr=attr)
#--- End: def
    
def le(value, units=None, attr=None):
    '''Return a `cf.Query` object for a variable for being less than or equal
to a value.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`,
             `cf.lt`, `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value: object
        The value which a variable is to be compared with.

    units: str or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr: str, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: cf.Query
        The query object.

:Examples:

>>> q = cf.le(5)
>>> q
<CF Query: x le 5>
>>> q.evaluate(5)
True
>>> q.evaluate(6)
False

    '''
    return Query('le', value, units=units, attr=attr)
#--- End: def
    
def gt(value, units=None, attr=None):
    '''Return a `cf.Query` object for a variable for being strictly greater
than a value.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.ne`, `cf.le`,
             `cf.lt`, `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value: `object`
        The value which a variable is to be compared with.

    units: `str` or `cf.Units`, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: `cf.Query`
        The query object.

:Examples:

>>> q = cf.gt(5)
>>> q
<CF Query: x gt 5>
>>> q.evaluate(6)
True
>>> q.evaluate(5)
False

    '''
    return Query('gt', value, units=units, attr=attr)
#--- End: def
    
def ge(value, units=None, attr=None):
    '''Return a `cf.Query` object for a variable for being greater than or
equal to a value.

.. seealso:: `cf.contain`, `cf.eq`, `cf.gt`, `cf.ne`, `cf.le`,
             `cf.lt`, `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value:
        The value which a variable is to be compared with.

    units: `str` or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> q = cf.ge(5)
>>> q
<CF Query: x ge 5>
>>> q.evaluate(5)
True
>>> q.evaluate(4)
False

>>> cf.ge(10, 'm')
<CF Query: (ge <CF Data: 10 m>)>
>>> cf.ge(100, cf.Units('kg'))
<CF Query: (ge <CF Data: 100 kg>)>

>>> cf.ge(2, attr='month')
<CF Query: month(ge 2)>

    '''
    return Query('ge', value, units=units, attr=attr)
#--- End: def

def eq(value, units=None, exact=True, attr=None):
    '''Return a `cf.Query` object for a variable for being equal to a value.

.. seealso:: `cf.contain`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`,
             `cf.lt`, `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value 
        The value which a variable is to be compared with.

    units: `str` or `cf.Units`, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    exact: `bool`, optional
        If False then string values are to be treated as regular
        expressions understood by the :py:obj:`re` module and are
        evaluated using the :py:obj:`re.match` method.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns:

    out: `cf.Query`
        The query object.
 
:Examples:

>>> q = cf.eq(5)
>>> q
<CF Query: x eq 5>
>>> q.evaluate(5)
True
>>> q == 4
False

>>> q = cf.eq('air', exact=False)
>>> q == 'air_temperature'
True

>>> q = cf.eq('.*temp', exact=False)
>>> q == 'air_temperature'
True
   '''
    return Query('eq', value, units=units, exact=exact, attr=attr)
#--- End: def
    
def ne(value, units=None, exact=True, attr=None):
    '''Return a `cf.Query` object for a variable for being equal to a value.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.gt`, `cf.le`,
             `cf.lt`, `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value: `object`
        The value which a variable is to be compared with.

    units: `str` or cf.Units, optional
        The units of *value*. By default, the same units as the
        variable being tested are assumed, if applicable.

    exact: `bool`, optional
        If False then string values are to be treated as regular
        expressions understood by the :py:obj:`re` module and are
        evaluated using the :py:obj:`re.match` method.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: `cf.Query`
        The query object.

:Examples:

>>> q = cf.ne(5)
>>> q
<CF Query: x ne 5>
>>> q.evaluate(4)
True
>>> q.evaluate(5)
False

    '''
    return Query('ne', value, units=units, exact=exact, attr=attr)
#--- End: def
    
def wi(value0, value1, units=None, attr=None):
    '''Return a `cf.Query` object for a variable being within a range.

``x == cf.wi(a, b)`` is equivalent to ``x == cf.ge(a) & cf.le(b)``.

``x == cf.wi(a, b, attr='foo')`` is equivalent to ``x.foo == cf.wi(a,
b)``.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`,
             `cf.le`, `cf.lt`, `cf.set`, `cf.wo`

:Parameters:

    value0: scalar object
         The lower bound of the range which a variable is to be
         compared with.

    value1: scalar object
         The upper bound of the range which a variable is to be
         compared with.

    units: `str` or cf.Units, optional
        If applicable, the units of *value0* and *value1*. By default,
        the same units as the variable being tested are assumed.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: `cf.Query`
        The query object.

:Examples:

>>> q = cf.wi(5, 7)
>>> q
<CF Query: wi (5, 7)>
>>> q.evaluate(6)
True
>>> q.evaluate(4)
False

    '''
    return Query('wi', [value0, value1], units=units, attr=attr)
#--- End: def

def wo(value0, value1, units=None, attr=None):
    '''Return a `cf.Query` object for a variable for being without a
range.

``x == cf.wo(a, b)`` is equivalent to ``x == cf.lt(a) | cf.gt(b)``.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`,
             `cf.le`, `cf.lt`, `cf.set`, `cf.wi`

:Parameters:

    value0: object
         The lower bound of the range which a variable is to be
         compared with.

    value1: object
         The upper bound of the range which a variable is to be
         compared with.

    units: `str` or cf.Units, optional
        If applicable, the units of *value0* and *value1*. By default,
        the same units as the variable being tested are assumed.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: `cf.Query`
        The query object.

:Examples:

>>> q = cf.wo(5)
>>> q
<CF Query: x wo (5, 7)>
>>> q.evaluate(4)
True
>>> q.evaluate(6)
False

    '''
    return Query('wo', [value0, value1], units=units, attr=attr)
#--- End: def

def set(values, units=None, exact=True, attr=None):
    '''Return a `cf.Query` object for a variable for being equal to any
member of a collection.

.. seealso:: `cf.contain`, `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`,
             `cf.le`, `cf.lt`, `cf.wi`, `cf.wo`

:Parameters:

    values: sequence
    
    units: `str` or cf.Units, optional
        The units of each element of *values*. By default, the same
        units as the variable being tested are assumed, if applicable.

    exact: `bool`, optional
        If False then string values are to be treated as regular
        expressions understood by the :py:obj:`re` module and are
        evaluated using the :py:obj:`re.match` method.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: `cf.Query`
        The query object.

:Examples:

>>> c = cf.set([3, 5])
>>> c
<CF Query: set [3, 5]>
>>> c == 4
False
>>> c == 5
True
>>> print c == numpy.array([2, 3, 4, 5])
[False  True False  True]

    '''
    return Query('set', values, units=units, exact=exact, attr=attr)
#--- End: def

def contain(value, units=None, attr=None):
    '''Return a `cf.Query` object for cells of a variable for containing a
value.

If cells are not defined then return a `cf.Query` object for a
variable for being equal to a value, i.e. this case is equivalent to
`cf.eq`.

.. versionadded:: 1.0

.. seealso:: `cf.eq`, `cf.ge`, `cf.gt`, `cf.ne`, `cf.le`, `cf.lt`,
             `cf.set`, `cf.wi`, `cf.wo`

:Parameters:

    value: 
        The value which a variable is to be compared with.
    
    units: `str` or cf.Units, optional
        The units of each element of *values*. By default, the same
        units as the variable being tested are assumed, if applicable.

    attr: `str`, optional
        Return a query object for a variable's *attr* attribute.

:Returns: 

    out: `cf.Query`
        The query object.

:Examples:

>>>  cf.contain(30, 'degrees_east')
<CF Query: (contain <CF Data: 30 degrees_east>)>
>>>  cf.contain(cf.Data(10, 'km'))
<CF Query: (contain <CF Data: 10 km>)>

>>> c
<CF DimensionCoordinate: longitude(4) degrees_east>
>>> print c.bounds.array
[[  0   90]
 [ 90  180]
 [180  270]
 [270  360]]
>>> print (cf.contain(100) == c).array
[False True False False]
>>> print (cf.contain(9999) == c).array
[False False False False]

    '''
    return Query('contain', value, units=units, attr=attr)
#--- End: def

def year(value):
    '''Return a `cf.Query` object for date-time years.

In this context, any object which has a `!year` attribute is
considered to be a date-time variable.

If *value* is a `cf.Query` object then ``cf.year(value)`` is
equivalent to ``value.addattr('year')``. Otherwise ``cf.year(value)``
is equivalent to ``cf.eq(value, attr='year')``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`, `cf.dtlt`

:Parameters:

    value:   
       Either the value that the year is to be compared with, or a
       `cf.Query` object for testing the year.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.year(2002)
True
>>> d == cf.year(cf.le(2003))
True
>>> d == cf.year(2001)
False
>>> d == cf.year(cf.wi(2003, 2006))
False

    '''
    if isinstance(value, Query):
        return value.addattr('year')
    else:
        return Query('eq', value, attr='year')
#--- End: def

def month(value):
    '''Return a `cf.Query` object for date-time months.

In this context, any object which has a `!month` attribute is
considered to be a date-time variable.

If *value* is a `cf.Query` object then ``cf.month(value)`` is
equivalent to ``value.addattr('month')``. Otherwise
``cf.month(value)`` is equivalent to ``cf.eq(value, attr='month')``.

.. seealso:: `cf.year`, `cf.day`, `cf.hour`, `cf.minute`, `cf.second`,
             `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    value:   
       Either the value that the month is to be compared with, or a
       `cf.Query` object for testing the month.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.month(6)
True
>>> d == cf.month(cf.le(7))
True
>>> d == cf.month(7)
False
>>> d == cf.month(cf.wi(1, 6))
True

    '''
    if isinstance(value, Query):
        return value.addattr('month')
    else:
        return Query('eq', value, attr='month')
#--- End: def

def day(value):
    '''Return a `cf.Query` object for date-time days.

In this context, any object which has a `!day` attribute is considered
to be a date-time variable.

If *value* is a `cf.Query` object then ``cf.day(value)`` is
equivalent to ``value.addattr('day')``. Otherwise ``cf.day(value)`` is
equivalent to ``cf.eq(value, attr='day')``.

.. seealso:: `cf.year`, `cf.month`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`, `cf.dtlt`

:Parameters:

    value:   
       Either the value that the day is to be compared with, or a
       `cf.Query` object for testing the day.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.day(16)
True
>>> d == cf.day(cf.le(19))
True
>>> d == cf.day(7)
False
>>> d == cf.day(cf.wi(1, 21))
True

    '''
    if isinstance(value, Query):
        return value.addattr('day')
    else:
        return Query('eq', value, attr='day')
#--- End: def

def hour(value):
    '''Return a `cf.Query` object for date-time hours.

In this context, any object which has a `!hour` attribute is
considered to be a date-time variable.

If *value* is a `cf.Query` object then ``cf.hour(value)`` is
equivalent to ``value.addattr('hour')``. Otherwise ``cf.hour(value)``
is equivalent to ``cf.eq(value, attr='hour')``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`, `cf.dtlt`

:Parameters:

    value:   
       Either the value that the hour is to be compared with, or a
       `cf.Query` object for testing the hour.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16, 18)
>>> d == cf.hour(18)
True
>>> d == cf.hour(cf.le(19))
True
>>> d == cf.hour(7)
False
>>> d == cf.hour(cf.wi(6, 23))
True

    '''
    if isinstance(value, Query):
        return value.addattr('hour')
    else:
        return Query('eq', value, attr='hour')
#--- End: def

def minute(value):
    '''

Return a `cf.Query` object for date-time minutes.

In this context, any object which has a `!minute` attribute is
considered to be a date-time variable.

If *value* is a `cf.Query` object then ``cf.minute(value)`` is
equivalent to ``value.addattr('minute')``. Otherwise
``cf.minute(value)`` is equivalent to ``cf.eq(value, attr='minute')``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.second`,
             `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    value:   
       Either the value that the minute is to be compared with, or a
       `cf.Query` object for testing the minute.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16, 18, 30, 0)
>>> d == cf.minute(30)
True
>>> d == cf.minute(cf.le(45))
True
>>> d == cf.minute(7)
False
>>> d == cf.minute(cf.wi(15, 45))
True

'''
    if isinstance(value, Query):
        return value.addattr('minute')
    else:
        return Query('eq', value, attr='minute')
#--- End: def

def second(value):
    '''

Return a `cf.Query` object for date-time seconds.
    
In this context, any object which has a `!second` attribute is
considered to be a date-time variable.

If *value* is a `cf.Query` object then ``cf.second(value)`` is
equivalent to ``value.addattr('second')``. Otherwise
``cf.second(value)`` is equivalent to ``cf.eq(value, attr='second')``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    value:   
       Either the value that the second is to be compared with, or a
       `cf.Query` object for testing the second.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16, 18, 30, 0)
>>> d == cf.second(0)
True
>>> d == cf.second(cf.le(30))
True
>>> d == cf.second(30)
False
>>> d == cf.second(cf.wi(0, 30))
True

'''
    if isinstance(value, Query):
        return value.addattr('second')
    else:
        return Query('eq', value, attr='second')
#--- End: def

def cellsize(value, units=None):
    '''Return a `cf.Query` object for the cell size of a coordinate object.

In this context, a coordinate is any object which has a `!cellsize`
attribute.

If *value* is a `cf.Query` object then ``cf.cellsize(value)`` is
equivalent to ``value.addattr('cellsize')`` (see
`cf.Query.addattr`). Otherwise ``cf.cellsize(value)`` is equivalent to
``cf.eq(value, attr='cellsize')``.

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.celllt`, `cf.cellle`,
             `cf.cellwi`, `cf.cellwo`, `cf.eq`

:Parameters:

    value:   
       Either the value that the cell size is to be compared with, or a
       `cf.Query` object for testing the cell size.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> cf.cellsize(cf.lt(5, 'km'))
<CF Query: cellsize(lt <CF Data: 5 km>)>
>>> cf.cellsize(5) 
<CF Query: cellsize(eq 5)>
>>> cf.cellsize(cf.Data(5, 'km'))
<CF Query: cellsize(eq <CF Data: 5 km>)>
>>> cf.cellsize(cf.Data(5, 'km'))  
<CF Query: cellsize(eq <CF Data: 5 km>)>
>>> cf.cellsize(5, units='km')   
<CF Query: cellsize(eq <CF Data: 5 km>)>

    '''
    if isinstance(value, Query):
        return value.addattr('cellsize')
    else:
        return Query('eq', value, units=units, attr='cellsize')
#--- End: def

def dtge(*args, **kwargs):
    '''

Return a `cf.Query` object for a variable being not earlier
than a date-time.

``cf.dtge(*args, **kwargs)`` is equivalent to ``cf.ge(cf.dt(*args,
**kwargs))``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtge(1990, 1, 1)
True
>>> d == cf.dtge(2002, 6, 16)
True
>>> d == cf.dtge('2100-1-1')
False
>>> d == cf.dtge('2001-1-1') & cf.dtle(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Query('ge', dt(*args, **kwargs))
#--- End: def

def dtgt(*args, **kwargs):
    '''

Return a `cf.Query` object for a variable being later than a
date-time.

``cf.dtgt(*args, **kwargs)`` is equivalent to ``cf.gt(cf.dt(*args,
**kwargs))``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtgt(1990, 1, 1)
True
>>> d == cf.dtgt(2002, 6, 16)
False
>>> d == cf.dtgt('2100-1-1')
False
>>> d == cf.dtgt('2001-1-1') & cf.dtle(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Query('gt', dt(*args, **kwargs))
#--- End: def

def dtle(*args, **kwargs):
    '''

Return a `cf.Query` object for a variable being not later than a
date-time.

``cf.dtle(*args, **kwargs)`` is equivalent to ``cf.le(cf.dt(*args,
**kwargs))``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtlt`

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtle(1990, 1, 1)
True
>>> d == cf.dtle(2002, 6, 16)
True
>>> d == cf.dtle('2100-1-1')
False
>>> d == cf.dtle('2001-1-1') & cf.dtle(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Query('le', dt(*args, **kwargs))
#--- End: def

def dtlt(*args, **kwargs):
    '''

Return a `cf.Query` object for a variable being earlier than a
date-time.

``cf.dtlt(*args, **kwargs)`` is equivalent to ``cf.lt(cf.dt(*args,
**kwargs))``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtne`,
             `cf.dtle`

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtlt(1990, 1, 1)
True
>>> d == cf.dtlt(2002, 6, 16)
True
>>> d == cf.dtlt('2100-1-1')
False
>>> d == cf.dtlt('2001-1-1') & cf.dtlt(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Query('lt', dt(*args, **kwargs))
#--- End: def

def dteq(*args, **kwargs):
    '''

Return a `cf.Query` object for a variable being equal to a
date-time.

``cf.dteq(*args, **kwargs)`` is equivalent to ``cf.eq(cf.dt(*args,
**kwargs))``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dtge`, `cf.dtgt`, `cf.dtne`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dteq(1990, 1, 1)
True
>>> d == cf.dteq(2002, 6, 16)
True
>>> d == cf.dteq('2100-1-1')
False
>>> d == cf.dteq('2001-1-1') & cf.dteq(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Query('eq', dt(*args, **kwargs))
#--- End: def

def dtne(*args, **kwargs):
    '''

Return a `cf.Query` object for a variable being not equal to a
date-time.

``cf.dtne(*args, **kwargs)`` is equivalent to ``cf.ne(cf.dt(*args,
**kwargs))``.

.. seealso:: `cf.year`, `cf.month`, `cf.day`, `cf.hour`, `cf.minute`,
             `cf.second`, `cf.dteq`, `cf.dtge`, `cf.dtgt`, `cf.dtle`,
             `cf.dtlt`

:Parameters:

    args, kwargs :
        Positional and keyword arguments for defining a date-time. See
        `cf.dt` for details.

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> d = cf.dt(2002, 6, 16)
>>> d == cf.dtne(1990, 1, 1)
True
>>> d == cf.dtne(2002, 6, 16)
True
>>> d == cf.dtne('2100-1-1')
False
>>> d == cf.dtne('2001-1-1') & cf.dtne(2010, 12, 31)
True

The last example is equivalent to:

>>> d == cf.wi(cf.dt(2001, 1, 1), cf.dt('2010-12-31'))
True

    ''' 
    return Query('ne', dt(*args, **kwargs))
#--- End: def

def cellwi(value0, value1, units=None):
    '''Return a `cf.Query` object for coordinate cell bounds being within
a range.

In this context, a coordinate is any object which has `!lower_bounds`
and `!upper_bounds` attributes.

``cf.cellwi(value0, value1)`` is equivalent to ``cf.ge(value0,
attr='lower_bounds') & cf.le(value1, attr='upper_bounds')``.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.cellle`, `cf.celllt`,
             `cf.cellsize`, `cf.cellwo`, `cf.wi`

:Parameters:

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

    ''' 
    return (Query('ge', value0, units=units, attr='lower_bounds') &
            Query('le', value1, units=units, attr='upper_bounds'))
#--- End: def

def cellwo(value0, value1, units=None):
    '''Return a `cf.Query` object for coordinate cell bounds being
outside a range.

In this context, a coordinate is any object which has `!lower_bounds`
and `!upper_bounds` attributes.

``cf.cellwo(value0, value1)`` is equivalent to ``cf.lt(value0,
attr='lower_bounds') & cf.gt(value1, attr='upper_bounds')``.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.cellle`, `cf.celllt`,
             `cf.cellsize`, `cf.cellwi`, `cf.wo`

:Parameters:

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

    ''' 
    return (Query('lt', value0, units=units, attr='lower_bounds') &
            Query('gt', value1, units=units, attr='upper_bounds'))
#--- End: def

def cellgt(value, units=None):
    '''Return a `cf.Query` object for coordinate cell bounds being
strictly greater than a value.

In this context, a coordinate is any object which has a
`!lower_bounds` attribute.

``cf.cellgt(value)`` is equivalent to ``cf.gt(value,
attr='lower_bounds')``.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellle`, `cf.celllt`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.gt`

:Parameters:

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

    ''' 
    return Query('gt', value, units=units, attr='lower_bounds')
#--- End: def

def cellge(value, units=None):
    '''Return a `cf.Query` object for coordinate cell bounds being
greater than or equal to a value.

In this context, a coordinate is any object which has a
`!lower_bounds` attribute.

``cf.cellge(value)`` is equivalent to ``cf.ge(value,
attr='lower_bounds')``.

.. versionadded:: 1.0

.. seealso:: `cf.cellgt`, `cf.cellle`, `cf.celllt`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.gt`

:Parameters:

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

    ''' 
    return Query('ge', value, units=units, attr='lower_bounds')
#--- End: def

def celllt(value, units=None):
    '''Return a `cf.Query` object for coordinate cell bounds being
strictly less than a value.

In this context, a coordinate is any object which has a
`!upper_bounds` attribute.

``cf.celllt(value)`` is equivalent to ``cf.lt(value,
attr='upper_bounds')``.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.cellle`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.le`

:Parameters:

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

    ''' 
    return Query('lt', value, units=units, attr='upper_bounds')
#--- End: def

def cellle(value, units=None):
    '''Return a `cf.Query` object for coordinate cell bounds being
less than or equal to a value.

In this context, a coordinate is any object which has a
`!upper_bounds` attribute.

``cf.cellle(value)`` is equivalent to ``cf.le(value,
attr='upper_bounds')``.

.. versionadded:: 1.0

.. seealso:: `cf.cellge`, `cf.cellgt`, `cf.celllt`, `cf.cellsize`,
             `cf.cellwi`,`cf.cellwo`, `cf.lt`

:Parameters:

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

    ''' 
    return Query('le', value, units=units, attr='upper_bounds')
#--- End: def

def jja():
    '''Return a `cf.Query` object for season June, July, August.

``cf.jja()`` is equivalent to ``cf.month(cf.wi(6, 8))``.

.. versionadded:: 1.0

.. seealso:: `cf.djf`, `cf.mam`, `cf.son`, `cf.seasons`, `cf.month`,
             `cf.wi`

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.jja())
<CF Field: air_temperature(time(92), latitude(64), longitude(128)) K>

    '''
    return Query('wi', (6, 8), attr='month')
#--- End: def

def son():
    '''Return a `cf.Query` object for season September, October,
November.

``cf.son()`` is equivalent to ``cf.month(cf.wi(9, 11))``.

.. versionadded:: 1.0

.. seealso:: `cf.djf`, `cf.mam`, `cf.jja`, `cf.seasons`, `cf.month`,
             `cf.wi`

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.son())
<CF Field: air_temperature(time(91), latitude(64), longitude(128)) K>

    '''
    return Query('wi', (9, 11), attr='month')
#--- End: def

def djf():
    '''Return a `cf.Query` object for season December, January, February.

``cf.djf()`` is equivalent to ``cf.month(cf.ge(12) | cf.le(2))``.

.. versionadded:: 1.0

.. seealso:: `cf.mam`, `cf.jja`, `cf.son`, `cf.seasons`, `cf.month`,
             `cf.ge`, `cf.le`

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.djf())
<CF Field: air_temperature(time(90), latitude(64), longitude(128)) K>

    '''
    q = Query('ge', 12) | Query('le', 2)
    return q.addattr('month')
#--- End: def

def mam():
    '''Return a `cf.Query` object for the season March, April, May.

``cf.mam()`` is equivalent to ``cf.month(cf.wi(3, 5))``.

.. versionadded:: 1.0

.. seealso:: `cf.djf`, `cf.jja`, `cf.son`, `cf.seasons`, `cf.month`,
             `cf.wi`

:Returns:

    out: `cf.Query`
        The query object.

:Examples:

>>> f
<CF Field: air_temperature(time(365), latitude(64), longitude(128)) K>
>>> f.subspace(time=cf.mam())
<CF Field: air_temperature(time(92), latitude(64), longitude(128)) K>

    '''
    return Query('wi', (3, 5), attr='month')

#--- End: def

def seasons(n=4, start=12):
    '''Return a list `cf.Query` objects for all seasons in a year.

.. versionadded:: 1.0

.. seealso:: `cf.mam`, `cf.jja`, `cf.son`, `cf.djf`

:Parameters:

    n: `int`, optional
        The number of seasons in the year. By default there are four
        seasons.

    start: `int`, optional
        The start month of the first season of the year. By default
        this is 12 (December).

:Returns:

    out: `list` of `cf.Query`
        The query objects.

:Examples:

>>> cf.seasons()
[<CF Query: month[(ge 12) | (le 2)]>,
 <CF Query: month(wi (3, 5))>,
 <CF Query: month(wi (6, 8))>,
 <CF Query: month(wi (9, 11))>]

>>> cf.seasons(4, 1)
[<CF Query: month(wi (1, 3))>,
 <CF Query: month(wi (4, 6))>,
 <CF Query: month(wi (7, 9))>,
 <CF Query: month(wi (10, 12))>]

>>> cf.seasons(3, 6)
[<CF Query: month(wi (6, 9))>,
 <CF Query: month[(ge 10) | (le 1)]>,
 <CF Query: month(wi (2, 5))>]

>>> cf.seasons(3)
[<CF Query: month[(ge 12) | (le 3)]>,
 <CF Query: month(wi (4, 7))>,
 <CF Query: month(wi (8, 11))>]

>>> cf.seasons(3, 6)
[<CF Query: month(wi (6, 9))>,
 <CF Query: month[(ge 10) | (le 1)]>,
 <CF Query: month(wi (2, 5))>]

>>> cf.seasons(12)
[<CF Query: month(eq 12)>,
 <CF Query: month(eq 1)>,
 <CF Query: month(eq 2)>,
 <CF Query: month(eq 3)>,
 <CF Query: month(eq 4)>,
 <CF Query: month(eq 5)>,
 <CF Query: month(eq 6)>,
 <CF Query: month(eq 7)>,
 <CF Query: month(eq 8)>,
 <CF Query: month(eq 9)>,
 <CF Query: month(eq 10)>,
 <CF Query: month(eq 11)>]

>>> cf.seasons(1, 4)
[<CF Query: month[(ge 4) | (le 3)]>]

    '''
    if 12 % n:
        raise ValueError(
            "Number of seasons must divide into 12. Got %s" % n)

    if not 1 <= start <= 12 or int(start) != start:
        raise ValueError(
            "Start month must be integer between 1 and 12. Got %s" % start)

    out = []

    inc = int(12 / n)

    start = int(start)

    m0 = start
    for i in range(int(n)):
        m1 = ((m0 + inc) % 12) - 1
        if not m1:
            m1 = 12
        elif m1 == -1:
            m1 = 11

        if m0 < m1: 
            q = Query('wi', (m0, m1))
        elif m0 > m1: 
            q = Query('ge', m0) | Query('le', m1)
        else:
            q = Query('eq', m0)

        out.append(q.addattr('month'))
    
        m0 = m1 + 1
        if m0 > 12:
            m0 = 1
    #--- End: for

    return out
#--- End: def

# --------------------------------------------------------------------
# Vectorized 
# --------------------------------------------------------------------
def _match(regex, x):
    return bool(re_match(regex, x))

_array_match = numpy_vectorize(_match, otypes=[bool])
