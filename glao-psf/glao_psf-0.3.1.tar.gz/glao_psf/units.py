"""
Common units.
Defines a set of commonly used units for use
in physical modeling and display

Typical usage::

    >>> from common_units import *
    
Then for example, access the 'micron' unit conversion with::

    >>> units['micron']
    1.e-06
    >>> units.micron
    1.e-06
    >>> micron
    1.e-06
    
which are all= 1.e-6

The import * adds a lot of variable names to the local
environment, but these are only the unit names
such as 'mm', 'cm', etc. (those listed by
units.list_all()) and the name 'units'.
If you don't want this, you can::

    >>> from common_units import units
    
Then::

    >>> units['micron'] # <-- works okay
    1e-06
    >>> units.micron  # <-- works okay
    1e-06
    >>> micron  # <-- doesnt work
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    NameError: name 'micron' is not defined

You can always load them into the local environment later with a call to
:py:meth:`put_into <common_units.Units.put_into>`.
"""
import sys
from numpy import pi

class Units(object):
    """The Units class defines an object with
    unit conversion factors
    """
    def __init__(self):
        self.arcsec = pi/(180.*3600.)
        self.arcmin = pi/(180.*60.)
        self.meters = 1.
        self.degree = pi/180.
        self.degrees = self.degree
        self.centimeters = 1.e-2
        self.centimeter = self.centimeters
        self.cm = self.centimeter
        self.millimeters = 1.e-3
        self.millimeter = self.millimeters
        self.mm = self.millimeters
        self.microns = 1.e-6
        self.micron = self.microns
        self.nanometers = 1.e-9
        self.nanometer = self.nanometers
        self.nm = self.nanometers
        self.kilometers = 1.e3
        self.kilometer = self.kilometers
        self.km = self.kilometers
        self.second = 1.
        self.seconds = self.second
        self.millisecond = 0.001
        self.milliseconds = self.millisecond
        self.microsecond = 1.e-6
        self.microseconds = self.microsecond
        self.ms = self.millisecond
        self._load()
        
    def list_all(self):
        """List all the unit conversion factors
        and their values.
        
        The current set of units is:
        
            >>> units.list_all()
            arcsec 4.8481368111e-06
            centimeter 0.01
            centimeters 0.01
            cm 0.01
            kilometer 1000.0
            kilometers 1000.0
            meters 1.0
            micron 1e-06
            microns 1e-06
            microsecond 1e-06
            microseconds 1e-06
            millimeter 0.001
            millimeters 0.001
            millisecond 0.001
            milliseconds 0.001
            mm 0.001
            ms 0.001
            nanometer 1e-09
            nanometers 1e-09
            nm 1e-09
            second 1.0
            seconds 1.0
        
        """
        keys = sorted(self.__dict__.keys())
        for key in keys:
            print key,self[key]
    
    def get_dict(self):
        """returns a dictionary with all the
        defined unit conversion factors
        """
        return self.__dict__
    
    def keys(self):
        """returns the list of unit names
        """
        return self.__dict__.keys()
    
    def __getitem__(self,key):
        return self.__dict__[key]
    
    def _load(self,module=None):
        if module is None:
            module = sys.modules[__name__]
        elif isinstance(module,str):
            module = sys.modules[module]
        for name,val in self.get_dict().iteritems():
            setattr(module,name,val)
        setattr(module,'units',self)
    
    def put_into(self,local_dict):
        """update a dictionary with the units.
        For example, to import them into the top-level (globals)::
        
            >>> from common_units import units
            >>> units.put_into(globals())
            
        """
        local_dict.update(self.get_dict())
        local_dict.update({'units':units})

units = Units()

def test():
    print units.get_dict()
    print units['mm']
    print units.mm
    print mm
