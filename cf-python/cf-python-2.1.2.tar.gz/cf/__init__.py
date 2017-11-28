'''

`CF <http://cfconventions.org/>`_ is a `netCDF
<http://www.unidata.ucar.edu/software/netcdf>`_ convention which is in
wide and growing use for the storage of model-generated and
observational data relating to the atmosphere, ocean and Earth system.

This package is an implementation of the `CF data model
<http://cf-trac.llnl.gov/trac/ticket/95>`_, and as such it is an API
allows for the full scope of data and metadata interactions described
by the CF conventions.

With this package you can:

  * Read `CF-netCDF <http://cfconventions.org/>`_ files,
    `CFA-netCDF <http://www.met.reading.ac.uk/~david/cfa/0.4>`_ files
    and UK Met Office fields files and PP files.
  
  * Create CF fields.

  * Write fields to CF-netCDF and CFA-netCDF files on disk.

  * Aggregate collections of fields into as few multidimensional
    fields as possible using the `CF aggregation rules
    <http://cf-trac.llnl.gov/trac/ticket/78>`_.

  * Create, delete and modify a field's data and metadata.

  * Select and subspace fields according to their metadata.

  * Perform broadcastable, metadata-aware arithmetic, comparison and
    trigonometric operation with fields.

  * Collapse fields by statistical operations.

  * Sensibly deal with date-time data.

  * Allow for cyclic axes.

  * Read discrete sampling geometry ragged arrays.

  * Read variables that have been compressed by gathering.

  * Visualize fields the `cfplot package
    <http://climate.ncas.ac.uk/~andy/cfplot_sphinx/_build/html/>`_.

All of the above use :ref:`LAMA` functionality, which allows multiple
fields larger than the available memory to exist and be manipulated.

See the `cf-python home page <http://cfpython.bitbucket.org/>`_ for
downloads, installation and source code.

'''

__Conventions__  = 'CF-1.6'
__author__       = 'David Hassell'
__date__         = '2017-11-24'
__version__      = '2.1.2'

from distutils.version import StrictVersion
import imp
import platform

# Check the version of python
if not (StrictVersion('2.7.0')
        <= StrictVersion(platform.python_version())
        < StrictVersion('3.0.0')):
    raise ValueError(
        "Bad python version: cf2 requires 2.7 <= python < 3.0. Got {}".format(
        platform.python_version()))

try:
    imp.find_module('ESMF')
except ImportError:
    _found_ESMF = False
    
else:
    _found_ESMF = True

from .variable             import Variable
from .boundedvariable      import BoundedVariable, Bounds
from .coordinate           import Coordinate, DimensionCoordinate, AuxiliaryCoordinate
from .coordinatereference  import CoordinateReference
from .cellmeasure          import CellMeasure
from .domainancillary      import DomainAncillary
from .domainaxis           import DomainAxis
from .field                import Field, FieldList
from .fieldancillary       import FieldAncillary
from .read                 import read, read1, read_field
from .write                import write
from .units                import Units
from .cfdatetime           import Datetime, dt
from .timeduration         import TimeDuration, Y, M, D, h, m, s
from .data.data            import Data
from .aggregate            import aggregate
from .query                import (Query, lt, le, gt, ge, eq, ne, contain,
                                   wi, wo, set, year, month, day, hour, minute,
                                   second, dtlt, dtle, dtgt, dtge, dteq, dtne,
                                   cellsize, cellge, cellgt, cellle, celllt,
                                   cellwi, cellwo, djf, mam, jja, son, seasons)
from .flags                import Flags
from .cellmethods          import CellMethod, CellMethods
from .constants            import *
from .functions            import *
from .maths                import *


'''Version 2 todo list

* [NOT DONE] Check auxiliary mask in Data.concatenate
* [NOT DONE] Check what's going with the ppps in Field._binary_operation
* [done] Add to_disk flags to Partition.close parallel
* [NOT DONE]
  import numpy, cf2 as cf; f=cf.read('DSG_timeSeriesProfile_indexed_contiguous.nc')[0]
  print f
  <snip> 
  Aux coords     : time(ncdim%station(1), ncdim%element(1)) = [[None]]
* [NOT DONE] check data.collapse fit in (chunk) memory
* [NOT DONE] order of axes in um/read.py
* [NOT DONE] CFA in general - write.py: fits in one chunk?
* [NOT DONE] test_Regrid is failing and currently turned off
* [NOT DONE] Consider reinstating my own Datetime which has optional
  calendar (and becomes one of the others if needs be
* [NOT DONE] Check cell methods for climatological time collapse

'''
