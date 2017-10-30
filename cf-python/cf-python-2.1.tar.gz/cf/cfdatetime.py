from datetime  import datetime
from functools import partial as functools_partial

import netCDF4
if netCDF4.__version__ >= '1.2.5':
    from netCDF4 import netcdftime
    _netCDF4_netcdftime_parse_date = netcdftime._parse_date
    
from numpy import around     as numpy_around
from numpy import array      as numpy_array
from numpy import asanyarray as numpy_asanyarray
from numpy import ndarray    as numpy_ndarray
from numpy import ndim       as numpy_ndim
from numpy import vectorize  as numpy_vectorize

from numpy.ma import array        as numpy_ma_array
from numpy.ma import isMA         as numpy_ma_isMA
from numpy.ma import is_masked    as numpy_ma_is_masked
from numpy.ma import masked       as numpy_ma_masked
from numpy.ma import masked_all   as numpy_ma_masked_all
from numpy.ma import masked_where as numpy_ma_masked_where
from numpy.ma import nomask       as numpy_ma_nomask

from .functions import inspect as cf_inspect
from .units     import Units

if netCDF4.__version__ <= '1.1.1':
    _netCDF4_netcdftime_parse_date = netCDF4.netcdftime._parse_date
#    _netCDF4_netcdftime_strftime   = netCDF4.netcdftime._strftime
elif netCDF4.__version__ <= '1.2.4':
    _netCDF4_netcdftime_parse_date = netCDF4.netcdftime.netcdftime._parse_date
#    _netCDF4_netcdftime_strftime   = netCDF4.netcdftime._datetime._strftime
    

# Define some useful units
_calendar_years  = Units('calendar_years')
_calendar_months = Units('calendar_months')

# ====================================================================
#
# Datetime object
#
# ====================================================================

class Datetime(netCDF4.netcdftime.datetime):
    '''A date-time object which supports CF calendars.

Any date-time in any CF calendar is allowed.

**Comparion operations**

Comparison operations are defined for `cf.Datetime` and
`datetime.datetime` objects:

>>> cf.Datetime(2004, 2, 1) < cf.Datetime(2004, 2, 30)
True
>>> cf.Datetime(2004, 2, 1) <= cf.Datetime(2004, 2, 30)
True
>>> cf.Datetime(2004, 2, 1) > cf.Datetime(2004, 2, 30)
False
>>> cf.Datetime(2004, 2, 1) >= cf.Datetime(2004, 2, 30)
False
>>> cf.Datetime(2004, 2, 1) == cf.Datetime(2004, 2, 30)
False
>>> cf.Datetime(2004, 2, 1) != cf.Datetime(2004, 2, 30)
True
>>> cf.Datetime(2004, 2, 1, microsecond=1) > cf.Datetime(2004, 2, 1)
True

>>> import datetime
>>> cf.Datetime(2004, 2, 30) > datetime.datetime(2004, 2, 1)
True
>>> datetime.datetime(2004, 2, 1) > cf.Datetime(2004, 2, 30)
False


**Arithmetic operations**

Addition and subtraction operations are defined for `cf.Datetime` and
`cf.TimeDuration` objects:

>>> cf.Datetime(2003, 2, 1) + cf.D(30)
<CF Datetime: 2003-03-03T00:00:00Z>
>>> cf.M(30) + cf.Datetime(2003, 2, 1)
<CF Datetime: 2003-03-03T00:00:00Z>
>>> cf.Datetime(2003, 2, 1, calendar='360_day') + cf.D(30)
<CF Datetime: 2003-03-01T00:00:00Z 360_day>
>>> cf.Datetime(2003, 2, 1, calendar='360_day') - cf.D(30)
<CF Datetime: 2003-01-01T00:00:00Z 360_day>

>>> cf.Datetime(2003, 2, 1) - cf.h(30)
<CF Datetime: 2003-01-30T18:00:00Z>
>>> cf.s(456) + cf.Datetime(2003, 2, 1)
<CF Datetime: 2003-02-01T00:07:36Z>

>>> cf.Datetime(2003, 2, 1) + cf.M(1)
<CF Datetime: 2003-03-01T00:00:00Z>
>>> cf.M(1) + cf.Datetime(2003, 2, 1, calendar='360_day') 
<CF Datetime: 2003-03-01T00:00:00Z 360_day>
>>> cf.Datetime(2003, 2, 1, calendar='noleap') + cf.M(245)
<CF Datetime: 2023-07-01T00:00:00Z noleap>
>>> cf.Datetime(2003, 2, 1) - cf.Y(2)
<CF Datetime: 2001-02-01T00:00:00Z>
>>> cf.Datetime(2003, 2, 1) - cf.Y(2) + cf.D(10)
<CF Datetime: 2001-02-11T00:00:00Z>

>>> d = cf.Datetime(2003, 2, 1)
>>> d += cf.s(34567689)
>>> d
<CF Datetime: 2004-03-07T02:08:09Z>

**Attributes**

==============  ======================================================
Attribute       Description
==============  ======================================================
`!year`         The year of the date
`!month`        The month of the year of the date
`!day`          The day of the month of the date
`!hour`         The hour of the day of the date
`!minute`       The minute of the hour of the date
`!second`       The second of the minute of the date
`!microsecond`  The microsecond of the second of the date
==============  ======================================================


**Constructors**

For convenience, the following functions may also be used to create
`cf.Datetime` objects:

========  ============================================================
Function  Description
========  ============================================================
`cf.dt`   Create a date-time object.
========  ============================================================

For example:

>>> cf.dt(2001, 12, 3) == cf.dt('2001-12-3') == cf.Datetime(2001, 12, 3)
True
>>> cf.dt(cf.Datetime(2001, 12, 3)) == cf.Datetime(2001, 12, 3)
True
>>> import datetime
>>> cf.dt(datetime.datetime(2001, 12, 3)) == cf.Datetime(2001, 12, 3)
True

.. seealso:: `cf.D`, `cf.dt`, `cf.h`, `cf.m`, `cf.M`, `cf.s`,
             `cf.TimeDuration`, `cf.Y`
    '''

    def __init__(self, year, month=1, day=1, hour=0, minute=0, second=0,
                 microsecond=0, dayofwk=-1, dayofyr=1, calendar=None):
        '''
        '''
        if netCDF4.__version__ > '1.1.1':
            super(Datetime, self).__init__(year, month, day, hour, minute,
                                           second, microsecond, dayofwk,
                                           dayofyr)
        else:
            super(Datetime, self).__init__(year, month, day, hour, minute,
                                           second, dayofwk,
                                           dayofyr)
            self.microsecond = 0

            #        if netCDF4.__version__ <= '1.2.4':
        self._calendar = calendar
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if `copy.deepcopy` is called

'''        
        return self.copy()
    #--- End: def

    def __hash__(self):
        '''
The built-in function `hash`

x.__hash__() <==> hash(x)

        '''
        return hash((self.__class__, self.year, self.month, self.day, self.hour,
                     self.minute, self.second, self.microsecond,
                     self._calendar))
    #--- End: def

    def __repr__(self):
        '''

x__repr__() <==> repr(x)

'''   
        out = '<CF {0}: {1}>'.format(self.__class__.__name__, self)
        calendar = self._calendar
        if calendar is not None:
            out = out.replace('>', ' '+calendar+'>')
        return out
    #--- End: def

    def __str__(self):
        '''

x__str__() <==> str(x)

'''   
        args = self.timetuple()[:6]
        out = '{0: >4}-{1:0>2}-{2:0>2}T{3:0>2}:{4:0>2}:{5:0>2}Z'.format(*args)
        if self.microsecond:
            out = out.replace('Z', '.{0:0>6}Z'.format(self.microsecond))      
        return out
    #--- End: def

    def __eq__(self, other):
        '''

x__eq__(y) <==> x==y

'''
        try:
            out = super(Datetime, self).__eq__(other)
            if out:
                # Check the microseconds
                out = self.microsecond == other.microsecond
            return out
        except:
            return NotImplemented
    #--- End: def

    def __ne__(self, other):
        '''

x__ne__(y) <==> x!=y

'''
        return not (self == other)
    #--- End: def

    def __ge__(self, other):
        '''

x__ge__(y) <==> x>=y

'''
        try:
            out = super(Datetime, self).__ge__(other)
            if out and super(Datetime, self).__eq__(other):
                # Check the microseconds
                out = self.microsecond >= other.microsecond
            return out
        except:
            return NotImplemented
    #--- End: def

    def __gt__(self, other):
        '''

x__gt__(y) <==> x>y

'''
        try:
            out = super(Datetime, self).__ge__(other)
            if out and super(Datetime, self).__eq__(other):
                # Check the microseconds
                out = self.microsecond > other.microsecond
            return out
        except:
            return NotImplemented
    #--- End: def

    def __le__(self, other):
        '''

x__le__(y) <==> x<=y

'''
        try:
            out = super(Datetime, self).__le__(other)
            if out and super(Datetime, self).__eq__(other):
                # Check the microseconds
                out = self.microsecond <= other.microsecond
            return out
        except:
            return NotImplemented
    #--- End: def

    def __lt__(self, other):
        '''

x__lt__(y) <==> x<y

'''
        try:
            out = super(Datetime2, self).__le__(other)
            if out and super(Datetime, self).__eq__(other):
                # Check the microseconds
                out = self.microsecond < other.microsecond
            return out
        except:
            return NotImplemented
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``d.copy()`` is equivalent to ``copy.deepcopy(d)``.

:Returns:

    out: `cf.Datetime`
        The deep copy.

:Examples:

>>> e = d.copy()

'''
        return type(self)(*self.timetuple()[:6], microsecond=self.microsecond,
                          calendar=self._calendar)
    #--- End: def

    def elements(self):
        '''Return a tuple of the first seven date-time attributes.

``d.elements`` is equivalent to ``(d.year, d.month, d.day, d.hour,
d.minute, d.second, d.microsecond)``.

:Returns:

    out: `tuple`
        The first seven date-time attributes.

:Examples:

>>> d = cf.Datetime(2005, 6, 7, 23, 45, 57, 45678)
>>> d.elements()
(2005, 6, 7, 23, 45, 57, 45678)

        '''
        return self.timetuple()[:6] # + (self.microsecond,)
    #--- End: def

    def equals(self, other):
        try:
            self == other
        except:
            return False
            
        return self._calendar == getattr(other, '_calendar', None)
    #--- End: def

    def inspect(self):
        '''Inspect the attributes.

.. seealso:: `cf.inspect`

:Returns: 

    None

        '''
        print cf_inspect(self)
    #--- End: def

    def replace(self, year=None, month=None, day=None, hour=None,
                minute=None, second=None, microsecond=None,
                calendar=None):
        '''Return datetime with new specified fields.'''

        return type(self)(
            *[(i if i is not None else j)
              for i, j in zip((year, month, day, hour,
                               minute, second, microsecond),
                              self.elements())],
            calendar=(calendar if calendar is not None else self._calendar)
        )
    #--- End: def

    def strftime(self, format=None):
        '''Return a string representing the date-time.

The string is an ISO 8601 string of the form Y-MM-DDThh:mm:ssZ, for
example ``2000-01-02T03:04:05Z``, or Y-MM-DDThh:mm:ss.sZ where the
final "s" refers to any sized decimal fraction added to the seconds,
for example ``2000-01-02T03:04:05.000786Z``.

:Examples 1:

>>> cf.Datetime(2004, 1, 30).strftime()
'2004-01-30T00:00:00Z'

:Parameters:

    format: `str`, optional
        Ignored.

:Returns:

    out: `str`
        The date-time string.

:Examples 2:

>>> cf.Datetime(2004, 2, 30).strftime()
'2004-02-30T00:00:00Z'

>>> cf.Datetime(2004, 2, 30, calendar='360_day').strftime()
'2004-02-30T00:00:00Z'

>>> cf.Datetime(2004, 7, 4, 12, 45, 56, 7456).strftime()
'2004-07-04T12:45:56.007456Z'

>>> cf.Datetime(2004, 12, 34).strftime()
'2004-12-34T00:00:00Z'

        '''
        return '{0: >4}-{1:0>2}-{2:0>2} {3:0>2}:{4:0>2}:{5:0>2}'.format(
            *self.timetuple()[:6])
    #--- End: def

    @classmethod
    def utcnow(cls):
        '''

Return the current Gregorian calendar UTC date and time.

:Examples 1:

>>> cf.Datetime.utcnow()
<CF Datetime: 2016-10-10T12:15:24.002376Z>

:Returns:

    out: `cf.Datetime`
        The current UTC date and time.

:Examples 2:

>>> cf.Datetime.utcnow()
<CF Datetime: 2016-10-10T12:15:25.422179Z>
>>> d = cf.Datetime(2005, 6, 7)
>>> d.utcnow()
<CF Datetime: 2016-10-10T12:15:50.375309Z>
>>> d
<CF Datetime: 2005-06-07T00:00:00Z>

'''
        return cls(*elements(datetime.utcnow()))
    #--- End: def

#--- End: class

#def _strftime(x):
#    try:
#        out = x.strftime('%Y-%m-%d %H:%M:%S')
#    except ValueError:
#        out = '{0}-{1:0>2}-{2:0>2} {3:0>2}:{4:0>2}:{5:0>2}'.format(
#            *self.timetuple()[:6])
#        
#    if self.microsecond:
#        out = out.replace('Z', '.{0:0>6}Z'.format(self.microsecond))
#        
#    return out


#class Datetime2(object):
#
#    # ----------------------------------------------------------------
#    # Adapted from Jeff Whitaker's netCDF4.netcdftime.datetime
#    # ----------------------------------------------------------------
#
#    '''A date-time object which supports CF calendars.
#
#Any date and time valid in any CF calendar is allowed.
#
#**Comparion operations**
#
#Comparison operations are defined for `cf.Datetime` and
#`datetime.datetime` objects:
#
#>>> cf.Datetime(2004, 2, 1) < cf.Datetime(2004, 2, 30)
#True
#>>> cf.Datetime(2004, 2, 1) <= cf.Datetime(2004, 2, 30)
#True
#>>> cf.Datetime(2004, 2, 1) > cf.Datetime(2004, 2, 30)
#False
#>>> cf.Datetime(2004, 2, 1) >= cf.Datetime(2004, 2, 30)
#False
#>>> cf.Datetime(2004, 2, 1) == cf.Datetime(2004, 2, 30)
#False
#>>> cf.Datetime(2004, 2, 1) != cf.Datetime(2004, 2, 30)
#True
#
#>>> import datetime
#>>> cf.Datetime(2004, 2, 30) > datetime.datetime(2004, 2, 1)
#True
#>>> datetime.datetime(2004, 2, 1) > cf.Datetime(2004, 2, 30)
#False
#
#
#**Arithmetic operations**
#
#Addition and subtraction operations are defined for `cf.Datetime` and
#`cf.TimeDuration` objects:
#
#>>> cf.Datetime(2003, 2, 1) + cf.D(30)
#<CF Datetime: 2003-03-03T00:00:00Z>
#>>> cf.M(30) + cf.Datetime(2003, 2, 1)
#<CF Datetime: 2003-03-03T00:00:00Z>
#>>> cf.Datetime(2003, 2, 1, calendar='360_day') + cf.D(30)
#<CF Datetime: 2003-03-01T00:00:00Z 360_day>
#>>> cf.Datetime(2003, 2, 1, calendar='360_day') - cf.D(30)
#<CF Datetime: 2003-01-01T00:00:00Z 360_day>
#
#>>> cf.Datetime(2003, 2, 1) - cf.h(30)
#<CF Datetime: 2003-01-30T18:00:00Z>
#>>> cf.s(456) + cf.Datetime(2003, 2, 1)
#<CF Datetime: 2003-02-01T00:07:36Z>
#
#>>> cf.Datetime(2003, 2, 1) + cf.M(1)
#<CF Datetime: 2003-03-01T00:00:00Z>
#>>> cf.M(1) + cf.Datetime(2003, 2, 1, calendar='360_day') 
#<CF Datetime: 2003-03-01T00:00:00Z 360_day>
#>>> cf.Datetime(2003, 2, 1, calendar='noleap') + cf.M(245)
#<CF Datetime: 2023-07-01T00:00:00Z noleap>
#>>> cf.Datetime(2003, 2, 1) - cf.Y(2)
#<CF Datetime: 2001-02-01T00:00:00Z>
#>>> cf.Datetime(2003, 2, 1) - cf.Y(2) + cf.D(10)
#<CF Datetime: 2001-02-11T00:00:00Z>
#
#>>> d = cf.Datetime(2003, 2, 1)
#>>> d += cf.s(34567689)
#>>> d
#<CF Datetime: 2004-03-07T02:08:09Z>
#
#
#**Attributes**
#
#==============  ======================================================
#Attribute       Description
#==============  ======================================================
#`!year`         The year of the date
#`!month`        The month of the year of the date
#`!day`          The day of the month of the date
#`!hour`         The hour of the day of the date
#`!minute`       The minute of the hour of the date
#`!second`       The second of the minute of the date
#`!microsecond`  The microsecond of the second of the date
#==============  ======================================================
#
#
#**Constructors**
#
#For convenience, the following functions may also be used to create
#`cf.Datetime` objects:
#
#========  ============================================================
#Function  Description
#========  ============================================================
#`cf.dt`   Create a date-time object.
#========  ============================================================
#
#For example:
#
#>>> cf.dt(2001, 12, 3) == cf.dt('2001-12-3') == cf.Datetime(2001, 12, 3)
#True
#>>> cf.dt(cf.Datetime(2001, 12, 3)) == cf.Datetime(2001, 12, 3)
#True
#>>> import datetime
#>>> cf.dt(datetime.datetime(2001, 12, 3)) == cf.Datetime(2001, 12, 3)
#True
#
#.. seealso:: `cf.D`, `cf.dt`, `cf.h`, `cf.m`, `cf.M`, `cf.s`,
#             `cf.TimeDuration`, `cf.Y`
#
#    '''
#    def __init__(self, year, month=1, day=1, hour=0, minute=0, second=0,
#                 microsecond=0, dayofwk=-1, dayofyr=1, calendar=None):
#        '''**Initialization**
#
#:Parameters:
#
#    year: `int`
#        The year.
#
#    month, day, hour, minute, second, microsecond: `int`, optional
#        The month of the year, the day of the month and time of the
#        day. *month* and *day* default to 1 and *hour*; *minute*,
#        *second* and *microsecond* default to 0.
#
#    calendar: `str`, optional
#        Define the default CF calendar for the date-time.
#
#          *Example:*
#             To set a calendar without leap years: ``calendar='noleap'``.
# 
#:Examples:
#
#>>> cf.Datetime(2003)
#<CF Datetime: 2003-01-01 00:00:00>
#>>> d = cf.Datetime(2003, 2, 30)
#>>> d = cf.Datetime(2003, 2, 30, 0)
#>>> d = cf.Datetime(2003, 2, 30, 0, 0)
#>>> d = cf.Datetime(2003, 2, 30, 0, 0, 0)
#>>> d = cf.Datetime(2003, 4, 5, 12, 30, 15)
#>>> d = cf.Datetime(year=2003, month=4, day=5, hour=12, minute=30, second=15)
#>>> d.year, d.month, d.day, d.hour, d.minute, d.second
#(2003, 4, 5, 12, 30, 15)
#>>> d.timetuple()
#(2003, 4, 5, 12, 30, 15, -1, 1)
#
#        '''
#        # ------------------------------------------------------------
#        # NOTE: dayofyr is set to 1 by default, otherwise
#        # time.strftime will complain.
#        # ------------------------------------------------------------
#        self.year        = year
#        self.month       = month
#        self.day         = day
#        self.hour        = hour
#        self.minute      = minute
#        self.second      = second
#        self.microsecond = microsecond
#        self.dayofwk     = dayofwk
#        self.dayofyr     = dayofyr
#        self.calendar    = calendar
#
#        self.fmt = '%Y-%m-%d %H:%M:%S'
#    #--- End: def
#
#    def __deepcopy__(self, memo):
#        '''
#
#Used if `copy.deepcopy` is called
#
#'''        
#        return self.copy()
#    #--- End: def
#
#    def __hash__(self):
#        '''
#
#The built-in function `hash`
#
#
#x.__hash__() <==> hash(x)
#
#        '''
#        return hash((self.__class__, self.year, self.month, self.day, self.hour,
#                     self.minute, self.second, self.microsecond,
#                     self.calendar))
#    #--- End: def
#
#    def __repr__(self):
#        '''
#
#x__repr__() <==> repr(x)
#
#'''   
#        out = '<CF {0}: {1}>'.format(self.__class__.__name__, str(self))
#        calendar = self.calendar
#        if calendar is not None:
#            out = out.replace('>', ' ('+calendar+')>')
#        return out
#    #--- End: def
#
#    def __str__(self):
#        '''
#
#x__str__() <==> str(x)
#
#'''
#        args = self.timetuple()[:6]
#        if self.microsecond:
#            args = list(args)
#            args[-1] += self.microsecond/1e6            
#        return '{0: >4}-{1:0>2}-{2:0>2}T{3:0>2}:{4:0>2}:{5:0>2}Z'.format(*args)
#    #--- End: def
#
#    def __eq__(self, other):
#        '''
#
#x__eq__(y) <==> x==y
#
#'''
#        try:
#            out = super(Datetime, self).__eq__(other)
#            if out and self.second == other.second:
#                out = self.microsecond == other.microsecond
#            return out
#        except:
#            return NotImplemented
#    #--- End: def
#
#    def __ne__(self, other):
#        '''
#
#x__ne__(y) <==> x!=y
#
#'''
#        return not (self == other)
#    #--- End: def
#
#    def __ge__(self, other):
#        '''
#
#x__ge__(y) <==> x>=y
#
#'''
#        try:
#            out = super(Datetime, self).__ge__(other)
#            if out and self.second == other.second:
#                out = self.microsecond >= other.microsecond
#            return out
#        except:
#            return NotImplemented
#    #--- End: def
#
#    def __gt__(self, other):
#        '''
#
#x__gt__(y) <==> x>y
#
#'''
#        try:
#            out = super(Datetime, self).__ge__(other)
#            if out and self.second == other.second:
#                out = self.microsecond > other.microsecond
#            return out
#        except:
#            return NotImplemented
#    #--- End: def
#
#    def __le__(self, other):
#        '''
#
#x__le__(y) <==> x<=y
#
#'''
#        try:
#            out = super(Datetime, self).__le__(other)
#            if out and self.second == other.second:
#                out = self.microsecond <= other.microsecond
#            return out
#        except:
#            return NotImplemented
#    #--- End: def
#
#    def __lt__(self, other):
#        '''
#
#x__lt__(y) <==> x<y
#
#'''
#        try:
#            out = super(Datetime, self).__le__(other)
#            if out and self.second == other.second:
#                out = self.microsecond < other.microsecond
#            return out
#        except:
#            return NotImplemented
##        try:
##            return self._timetuple7() < _timetuple7(other)
##        except AttributeError:
##            return NotImplemented
#    #--- End: def
#
##    def __add__(self, other):
##        '''
##        
##The binary arithmetic operation ``+``
##
##x.__add__(y) <==> x+y
##
##'''
##        if hasattr(other, 'interval'):
##            # other is a TimeDuration object
##            try:
##                return other.interval(self, end=False, iso=False)[1]
##            except TypeError:
##                return NotImplemented
##
##        return NotImplemented
##    #--- End: def
##
##    def __sub__(self, other):
##        '''
##        
##The binary arithmetic operation ``-``
##
##x.__sub__(y) <==> x-y
##
##'''
##        if hasattr(other, 'interval'):
##            # other is a TimeDuration object
##            try:
##                return other.interval(self, end=True, iso=False)[0]
##            except TypeError:
##                return NotImplemented
##
##        return NotImplemented
##    #--- End: def
#
##    def __iadd__(self, other):
##        '''
##
##The augmented arithmetic assignment ``+=``
##
##x.__iadd__(y) <==> x+=y
##
##'''
##        return self + other
##    #--- End: def
##
##    def __isub__(self, other):
##        '''
##
##The augmented arithmetic assignment ``-=``
##
##x.__isub__(y) <==> x-=y
##
##'''
##        return self - other
##    #--- End: def
#
##    def __radd__(self, other):
##        '''
##
##The binary arithmetic operation ``+`` with reflected operands
##
##x.__radd__(y) <==> y+x
##
##'''
##        return self + other
##    #--- End: def
#
##    @property
##    def year(self): return self._year
##
##    @property
##    def month(self): return self._month 
##        
##    @property
##    def day(self): return self._day         
##        
##    @property
##    def hour(self):return  self._hour       
##        
##    @property
##    def minute(self): return self._minute   
##        
##    @property
##    def second(self): return self._second   
##        
##    @property
##    def microsecond(self): return self._microsecond 
##        
##    @property
##    def dayofwk(self): return self._dayofwk    
##        
##    @property
##    def dayofyr(self): return self._dayofyr     
#    
#    def _to_real_datetime(self):
#        return datetime(self.year, self.month, self.day,
#                        self.hour, self.minute, self.second,
#                        self.microsecond)
#    #--- End: def
#
#    def _timetuple6(self):
#        '''
#
#Return a tuple of the first six date-time attributes.
#
#``d._timetuple6()`` is equivalent to ``(d.year, d.month, d.day,
#d.hour, d.minute, d.second)``.
#
#:Returns:
#
#    out: `tuple`
#        The first six date-time attributes.
#
#:Examples:
#
#>>> d = cf.Datetime(2005, 6, 7, 23, 45, 57)
#>>> d._timetuple6()
#(2005, 6, 7, 23, 45, 57)
#
#'''
#        return (self.year, self.month, self.day,
#                self.hour, self.minute, self.second)
#    #--- End: def
#
#    def copy(self):
#        '''
#
#Return a deep copy.
#
#``d.copy()`` is equivalent to ``copy.deepcopy(d)``.
#
#:Returns:	
#
#    out: `cf.Datetime`
#        The deep copy.
#
#:Examples:
#
#->>> e = d.copy()
#
#'''
#        new = Datetime.__new__(Datetime)
#        new.__dict__ = self.__dict__.copy()
#        return new
#    #--- End: def
#
#    def elements(self):
#        '''Return a tuple of the first seven date-time attributes.
#
#``d.elements`` is equivalent to ``(d.year, d.month, d.day, d.hour,
#d.minute, d.second, d.microsecond)``.
#
#:Returns:
#
#    out: `tuple`
#        The first seven date-time attributes.
#
#:Examples:
#
#>>> d = cf.Datetime(2005, 6, 7, 23, 45, 57, 45678)
#>>> d.elements()
#(2005, 6, 7, 23, 45, 57, 45678)
#
#        '''
#        return self.timetuple()[:6] + (self.microsecond,)
#    #--- End: def
#
#    def inspect(self):
#        '''
#
#Inspect the attributes.
#
#.. seealso:: `cf.inspect`
#
#:Returns: 
#
#    None
#
#'''
#        print cf_inspect(self)
#    #--- End: def
#
#    def strftime(self, *fmt):
#        return '{0: >4}-{1:0>2}-{2:0>2} {3:0>2}:{4:0>2}:{5:0>2}'.format(
#            *self._timetuple6())
#    #--- End: def
#
#    def timetuple(self):
#        '''Return a tuple of the date-time attributes such as returned by
#`datetime.datetime.timetuple`.
#
#``d.timetuple()`` is equivalent to ``(d.year, d.month, d.day, d.hour,
#d.minute, d.second, d.dayofwk, d.dayofyr, -1)``.
#
#:Returns:
#
#    out: `tuple`
#        The date-time attributes.
#
#:Examples:
#
#>>> d = cf.Datetime(2005, 6, 7, 23, 45, 57, 999888)
#>>> d.timetuple()
#(2005, 6, 7, 23, 45, 57, -1, 1, -1)
#
#        '''
#        return (self.year, self.month, self.day,
#                self.hour, self.minute, self.second,
#                self.dayofwk, self.dayofyr, -1)
#    #--- End: def
#
#    @classmethod
#    def utcnow(cls):
#        '''
#
#Return the current Gregorian calendar UTC date and time.
#
#:Returns:
#
#    out: `cf.Datetime`
#        The current UTC date and time.
#
#:Examples:
#
#>>> cf.Datetime.utcnow()
#<CF Datetime: 2013-11-19 17:55:59>
#>>> d = cf.Datetime(2005, 6, 7)
#>>> d.utcnow()
#<CF Datetime: 2013-11-19 17:56:07>
#>>> d
#<CF Datetime: 2005-06-07 00:00:00>
#
#'''
#        return cls(*datetime.utcnow().timetuple()[:-1])
#    #--- End: def
#
##--- End: class
##netCDF4.netcdftime.datetime = Datetime

def elements(x):
     return x.timetuple()[:6] # + (getattr(x, 'microsecond', 0),)
#--- End: def

def dt(*args, **kwargs):
    '''Return a date-time variable for a given date and time.

The date and time may be specified with an ISO 8601-like date-time
string (in which non-Gregorian calendar dates are allowed) or by
providing a value for the year and, optionally, the month, day, hour,
minute, second and microsecond.

.. seealso:: `cf.Datetime`

:Parameters:

    args, kwargs:
        If the first positional argument is a string, then it must be
        an ISO 8601-like date-time string from which a `cf.Datetime`
        object is initialized. Otherwise, the positional and keyword
        arguments are used to explicitly initialize a `cf.Datetime`
        object, so see `cf.Datetime` for details.

:Returns:

    out: `cf.Datetime`
        The new date-time object.

:Examples:

>>> d = cf.dt(2003)
>>> print d
'2003-2-30T00:00:00Z'
>>> d = cf.dt(2003, 2, 30)
>>> d = cf.dt(2003, 2, 30, 0, 0, 0)
>>> d = cf.dt('2003-2-30')
>>> d = cf.dt('2003-2-30 0:0:0')

>>> d = cf.dt(2003, 4, 5, 12, 30, 15)
>>> d = cf.dt(year=2003, month=4, day=5, hour=12, minute=30, second=15)
>>> d = cf.dt('2003-04-05 12:30:15')
>>> d.year, d.month, d.day, d.hour, d.minute, d.second
(2003, 4, 5, 12, 30, 15)

    '''
    calendar = kwargs.pop('calendar', None)

    if kwargs:
        # cf.dt(2001, 3, day=4)
        # cf.dt(2001, 3, day=4, calendar='noleap')
        # cf.dt(year=2001, month=3, day=4)
        # cf.dt(year=2001, month=3, day=4, calendar='noleap')
        kwargs['calendar'] = calendar
        return Datetime(*args, **kwargs)
    elif not args:
        raise ValueError("34 woah!")

    arg0 = args[0]
    if isinstance(arg0, basestring):
        # cf.dt('2001-3-4')
        # cf.dt('2001-3-4', calendar='noleap')
        out = st2Datetime(arg0)
        out._calendar = calendar
        return out
        
    if isinstance(arg0, Datetime):
        # cf.dt(cf.Datetime(2001, 3, 4))
        # cf.dt(cf.Datetime(2001, 3, 4, calendar='noleap')
        # cf.dt(cf.Datetime(2001, 3, 4), calendar='noleap')
        # cf.dt(cf.Datetime(2001, 3, 4, calendar='360_day'), calendar='noleap')
        out = arg0.copy()
        if out._calendar is None or calendar is not None:
            out._calendar = calendar
        return out

    if hasattr(arg0, 'timetuple'):
        # cf.dt(datetime.datetime(2001, 3, 4))
        # cf.dt(datetime.datetime(2001, 3, 4), calendar='noleap')
        params = arg0.timetuple()[:6] + (getattr(arg0, 'microsecond', 0),)
        return Datetime(*params, calendar=calendar)

    # cf.dt(2001, 3, 4)
    # cf.dt(2001, 3, 4, calendar='noleap')
    return Datetime(*args, calendar=calendar)
#--- End: def

def st2dt(array, units_in=None, dummy0=None, dummy1=None):
    '''
    
The returned array is always independent.

:Parameters:

    array: numpy array-like

    units_in: `cf.Units`, optional

    dummy0: optional
        Ignored.

    dummy1: optional
        Ignored.

:Returns:

    out: `numpy.ndarray`
        An array of `cf.Datetime` or `datetime.datetime` objects with
        the same shape as *array*.

:Examples:

'''
#    if getattr(units_in, '_calendar', None) in ('gregorian' 'standard', 'none'):
#        return array_st2datetime(array)
#    else:
    return array_st2Datetime(array)
#--- End: def

#def st2datetime(date_string):
#    '''
#
#Parse an ISO 8601 date-time string into a datetime.datetime object.
#
#:Parameters:
#
#    date_string: `str`
#
#:Returns:
#
#    out: `datetime.datetime`
#
#'''
#    if date_string.count('-') != 2:
#        raise ValueError("A string must contain a year, a month and a day")
#
#    year,month,day,hour,minute,second,utc_offset = _netCDF4_netcdftime_parse_date(date_string)
#    if utc_offset:
#        raise ValueError("Can't specify a time offset from UTC")
#            
#    return datetime(year, month, day, hour, minute, second)
##--- End: def
#
#array_st2datetime = numpy_vectorize(st2datetime, otypes=[object])

def st2Datetime(date_string):
    '''

Parse an ISO 8601 date-time string into a `cf.Datetime` object.

:Parameters:

    date_string: `str`

:Returns:

    out: `cf.Datetime`

'''
    if date_string.count('-') != 2:
        raise ValueError("Input date-time string must contain at least a year, a month and a day")

    year,month,day,hour,minute,second,utc_offset = _netCDF4_netcdftime_parse_date(date_string)
    if utc_offset:
        raise ValueError("Can't specify a time offset from UTC")

    return Datetime(year, month, day, hour, minute, second)
#--- End: def

array_st2Datetime = numpy_vectorize(st2Datetime, otypes=[object])

def rt2dt(array, units_in, units_out=None, dummy1=None):
    '''Convert reference times  to date-time objects

The returned array is always independent.

:Parameters:

    array: numpy array-like

    units_in: `cf.Units`

    units_out: *optional*
        Ignored.

    dummy1:
        Ignored.

:Returns:

    out: `numpy.ndarray`
        An array of `cf.Datetime` objects with the same shape as
        *array*.

    '''
    mask = None
    if numpy_ma_isMA(array):
        # num2date has issues if the mask is nomask
        mask = array.mask
        if mask is numpy_ma_nomask or not numpy_ma_is_masked(array):
            array = array.view(numpy_ndarray)

    array = units_in._utime.num2date(array)

    if mask is not None:
        array = numpy_ma_masked_where(mask, array)

    ndim = numpy_ndim(array)

    if mask is None:
        # There is no missing data
        array = numpy_array(array, dtype=object)
        return numpy_vectorize(
            functools_partial(dt2Dt, calendar=units_in._calendar),
            otypes=[object])(array)
    else:
        # There is missing data
        if not ndim:
            return numpy_ma_masked_all((), dtype=object)
        else:
            array = numpy_array(array)
            array = numpy_vectorize(
                functools_partial(dt2Dt, calendar=units_in._calendar),
                otypes=[object])(array)
            return numpy_ma_masked_where(mask, array)
#--- End: def

def dt2Dt(x, calendar=None):
    '''Convert a datetime.datetime object to a cf.Datetime object'''
    if not x:
        return False
    return Datetime(*elements(x), calendar=calendar)
#--- End: def

def dt2rt(array, units_in, units_out, dummy1=None):
    '''Round to the nearest millisecond. This is only necessary whilst
netCDF4 time functions have an accuracy of no better than 1
millisecond (which is still the case at version 1.2.2).
    
The returned array is always independent.

:Parameters:

    array: numpy array-like of date-time objects

    units_in:
        Ignored.

    units_out: `cf.Units`

    dummy1:
        Ignored.

:Returns:

    out: `numpy.ndarray`
        An array of numbers with the same shape as *array*.

    '''
    ndim = numpy_ndim(array)
    
    if not ndim and isinstance(array, numpy_ndarray):
        # This necessary because date2num gets upset if you pass
        # it a scalar numpy array
        array = array.item()

    array = units_out._utime.date2num(array)

    if not ndim:
        array = numpy_array(array)

    # Round to the nearest millisecond. This is only necessary whilst
    # netCDF4 time functions have an accuracy of no better than 1
    # millisecond (which is still the case at version 1.2.2).
    units = units_out._utime.units
    decimals = 3
    month = False
    year = False

    # Can just use netCDF4.netcdftime.*_units when I stop supporting 1.1.1

    day = units in getattr('netCDF4.netcdftime', 'day_units', ['day', 'days', 'd'])
    if day:
        array *= 86400.0        
    else:
        sec = units in getattr('netCDF4.netcdftime', 'sec_units', ['second', 'seconds', 'sec', 'secs', 's'])
        if not sec:
            hr = units in getattr('netCDF4.netcdftime', 'hr_units', ['hour', 'hours', 'hr', 'hrs', 'h'])
            if hr:
                array *= 3600.0
            else:
                m = units in getattr('netCDF4.netcdftime', 'min_units', ['minute', 'minutes', 'min', 'mins'])
                if m:
                    array *= 60.0
                else:
                    millisec = units in getattr('netCDF4.netcdftime', 'millisec_units', ['milliseconds', 'millisecond', 'millisec', 'millisecs'])
                    if millisec:
                        decimals = 0
                    else:
                        microsec = units in getattr('netCDF4.netcdftime', 'microsec_units', ['microseconds','microsecond', 'microsec', 'microsecs'])
                        if microsec:
                            decimals = -3
                        else:
                            month = units in ('month', 'months')
                            if month:
                                array *= (365.242198781 / 12.0) * 86400.0
                            else:
                                year = units in ('year', 'years', 'yr')
                                if year:
                                    array *= 365.242198781 * 86400.0
    #--- End: if
    array = numpy_around(array, decimals, array)

    if day:
        array /= 86400.0
    elif sec:
        pass
    elif hr:
        array /= 3600.0
    elif m:
        array /= 60.0
    elif month:
        array /= (365.242198781 / 12.0) * 86400.0
    elif year:
        array /= 365.242198781 * 86400.0

    if not ndim:
        array = numpy_asanyarray(array)
        
    return array
#--- End: def

def st2rt(array, units_in, units_out, dummy1=None):
    '''
    
The returned array is always independent.

:Parameters:

    array: numpy array-like of ISO 8601 date-time strings

    units_in: `cf.Units` or `None`

    units_out: `cf.Units`

    dummy1:
        Ignored.

:Returns:

    out: `numpy.ndarray`
        An array of floats with the same shape as *array*.

'''

    array = st2dt(array, units_in)

    ndim = numpy_ndim(array)
    
    if not ndim and isinstance(array, numpy_ndarray):
        # This necessary because date2num gets upset if you pass
        # it a scalar numpy array
        array = array.item()

    array = units_out._utime.date2num(array)
    
    if not ndim:
        array = numpy_array(array)

    return array
#--- End: def

#def _JulianDayFromDate(date, calendar='standard'):
#    '''
#
#Create a Julian Day from a 'datetime-like' object.  Returns the
#fractional Julian Day (resolution 1 second).
#
#if calendar='standard' or 'gregorian' (default), Julian day follows
#Julian Calendar on and before 1582-10-5, Gregorian calendar after
#1582-10-15.
#
#if calendar='proleptic_gregorian', Julian Day follows gregorian
#calendar.
#
#if calendar='julian', Julian Day follows julian calendar.
#
#Algorithm:
#
#Meeus, Jean (1998) Astronomical Algorithms (2nd
#Edition). Willmann-Bell, Virginia. p. 63
#
#This is taken from netCDF4.netcdftime.JulianDayFromDate, with an error
#check added.
#
#'''
#    # based on redate.py by David Finlayson.
#
#    year=date.year; month=date.month; day=date.day
#    hour=date.hour; minute=date.minute; second=date.second
#
#    try:
#        datetime(year, month, day, hour, minute, second)
#    except ValueError:
#        raise ValueError("Bad {0} calendar date: {1}".format(calendar, date))
#
#    # Convert time to fractions of a day
#    day = day + hour/24.0 + minute/1440.0 + second/86400.0
#
#    # Start Meeus algorithm (variables are in his notation)
#    if (month < 3):
#        month = month + 12
#        year = year - 1
#
#    A = int(year/100)
#
#    # MC
#    # jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + \
#    #      day - 1524.5
#    jd = 365.*year + int(0.25 * year + 2000.) + int(30.6001 * (month + 1)) + \
#         day + 1718994.5
#
#    # optionally adjust the jd for the switch from
#    # the Julian to Gregorian Calendar
#    # here assumed to have occurred the day after 1582 October 4
#    if calendar in ['standard','gregorian']:
#        if jd >= 2299170.5:
#            # 1582 October 15 (Gregorian Calendar)
#            B = 2 - A + int(A/4)
#        elif jd < 2299160.5:
#            # 1582 October 5 (Julian Calendar)
#            B = 0
#        else:
#            raise ValueError('impossible date (falls in gap between end of Julian calendar and beginning of Gregorian calendar')
#    elif calendar == 'proleptic_gregorian':
#        B = 2 - A + int(A/4)
#    elif calendar == 'julian':
#        B = 0
#    else:
#        raise ValueError('unknown calendar, must be one of julian,standard,gregorian,proleptic_gregorian, got %s' % calendar)
#
#    # adjust for Julian calendar if necessary
#    jd = jd + B
#
#    return jd
##--- End: def
#netCDF4.netcdftime.JulianDayFromDate = _JulianDayFromDate

#def _NoLeapDayFromDate(date):
#    '''
#
#Creates a Julian Day for a calendar with no leap years from a
#date-time instance.  Returns the fractional Julian Day (resolution 1
#second).
#
#'''
#    year = date.year
#    month = date.month
#    day = date.day
#    hour = date.hour
#    minute = date.minute
#    second = date.second
#    microsecond = date.microsecond
#
#    if month == 2 and day > 28:
#        raise ValueError("Bad 365_day calendar date: %s" % date)
#
#    if year != 0:
#        try:
#            datetime(year, month, day, hour, minute, second, microsecond)
#        except ValueError:
#            raise ValueError("Bad 365_day calendar date: %s" % date)
#        
#    if netCDF4.__version__ <= '1.1.1':
#        return netCDF4.netcdftime._NoLeapDayFromDate(date) = _NoLeapDayFromDate
#    else:
#        return netCDF4.netcdftime.netcdftime._NoLeapDayFromDate(date)
#
#    year=date.year; month=date.month; day=date.day
#    hour=date.hour; minute=date.minute; second=date.second
#
#    if month == 2 and day > 28:
#        raise ValueError("Bad 365_day calendar date: %s" % date)
#
#    if year != 0:
#        try:
#            datetime(year, month, day, hour, minute, second)
#        except ValueError:
#            raise ValueError("Bad 365_day calendar date: %s" % date)
#    
#    # Convert time to fractions of a day
#    day = day + hour/24.0 + minute/1440.0 + second/86400.0
#
#    # Start Meeus algorithm (variables are in his notation)
#    if (month < 3):
#        month = month + 12
#        year = year - 1
#
#    jd = int(365. * (year + 4716)) + int(30.6001 * (month + 1)) + \
#         day - 1524.5
#
#    return jd
#--- End: def
#if netCDF4.__version__ <= '1.1.1':
#    netCDF4.netcdftime._NoLeapDayFromDate = _NoLeapDayFromDate
#else:
#    netCDF4.netcdftime.netcdftime._NoLeapDayFromDate = _NoLeapDayFromDate

