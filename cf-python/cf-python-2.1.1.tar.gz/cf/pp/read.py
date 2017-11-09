import os
import netCDF4
import csv
import re
import textwrap
import numpy

from struct import unpack as struct_unpack

from numpy import arange       as numpy_arange
from numpy import array        as numpy_array
from numpy import column_stack as numpy_column_stack
from numpy import dtype        as numpy_dtype
from numpy import empty        as numpy_empty
from numpy import fromfile     as numpy_fromfile
from numpy import pi           as numpy_pi

from netCDF4 import date2num as netCDF4_date2num

from ..                    import __version__, __Conventions__, __file__
from ..coordinatereference import CoordinateReference
from ..domain              import Domain
from ..field               import Field
from ..fieldlist           import FieldList
from ..cellmethods         import CellMethods
from ..cfdatetime          import Datetime
from ..coordinate          import DimensionCoordinate, AuxiliaryCoordinate
from ..coordinatebounds    import CoordinateBounds
from ..functions           import RTOL, ATOL, equals, hash_array
from ..units               import Units
from ..functions           import abspath

from ..data.data import Data

from .filearray import PPFileArray #, PPFileArrayBounds

# Number of bytes per word in the input PP files
_word_size = 4

# PP missing data indicator
_pp_rmdi   = -1.0e+30 

# Reference surface pressure in Pa
_pstar     = 1.0e5

# --------------------------------------------------------------------
# Constants for converting creating unrotated lat/lon auxiliary
# coordinates
# --------------------------------------------------------------------
_pi          = numpy_pi
_pi_over_180 = _pi/180.0

# --------------------------------------------------------------------
# Number matching regular expression
# --------------------------------------------------------------------
_number_regex = '([-+]?\d*\.?\d+(e[-+]?\d+)?)'

# --------------------------------------------------------------------
# Date-time object that copes with non-standard calendars
# --------------------------------------------------------------------
netCDF4_netcdftime_datetime = netCDF4.netcdftime.datetime

# --------------------------------------------------------------------
# Caches for derived values
# --------------------------------------------------------------------
_cache = {'latlon': {}}

_cached_runid      = {}
_cached_latlon     = {}
_cached_time       = {}
_cached_ctime      = {}
_cached_coordinate = {}
_cached_units      = {'1'            : Units('1'),
                      'Pa'           : Units('Pa'),
                      'm'            : Units('m'),
                      'hPa'          : Units('hPa'),
                      'K'            : Units('K'),
                      'degrees'      : Units('degrees'),
                      'degrees_east' : Units('degrees_east'),
                      'degrees_north': Units('degrees_north'),
                      ''             : Units(''),
                      'days'         : Units('days'),
                      }

# --------------------------------------------------------------------
# Names of PP integer and real header items
# --------------------------------------------------------------------
_header_items = ('LBYR', 'LBMON', 'LBDAT', 'LBHR', 'LBMIN', 'LBDAY',
                 'LBYRD', 'LBMOND', 'LBDATD', 'LBHRD', 'LBMIND',
                 'LBDAYD', 'LBTIM', 'LBFT', 'LBLREC', 'LBCODE', 'LBHEM',
                 'LBROW', 'LBNPT', 'LBEXT', 'LBPACK', 'LBREL', 'LBFC',
                 'LBCFC', 'LBPROC', 'LBVC', 'LBRVC', 'LBEXP', 'LBEGIN', 
                 'LBNREC', 'LBPROJ', 'LBTYP', 'LBLEV', 'LBRSVD1',
                 'LBRSVD2', 'LBRSVD3', 'LBRSVD4', 'LBSRCE', 'LBUSER1',
                 'LBUSER2', 'LBUSER3', 'LBUSER4', 'LBUSER5', 'LBUSER6',
                 'LBUSER7',
                 'BRSVD1', 'BRSVD2', 'BRSVD3', 'BRSVD4', 
                 'BDATUM', 'BACC', 'BLEV', 'BRLEV', 'BHLEV', 'BHRLEV',
                 'BPLAT', 'BPLON', 'BGOR',
                 'BZY', 'BDY', 'BZX', 'BDX', 'BMDI', 'BMKS')

# --------------------------------------------------------------------
# Positions of PP header items in their arrays
# --------------------------------------------------------------------
#(lbyr, lbmon, lbdat, lbhr, lbmin, lbday,
# lbyrd, lbmond, lbdatd, lbhrd, lbmind,
# lbdayd, lbtim, lbft, lblrec, lbcode, lbhem,
# lbrow, lbnpt, lbext, lbpack, lbrel, lbfc,
# lbcfc, lbproc, lbvc, lbrvc, lbexp, lbegin, 
# lbnrec, lbproj, lbtyp, lblev, lbrsvd1,
# lbrsvd2, lbrsvd3, lbrsvd4, lbsrce, lbuser1,
# lbuser2, lbuser3, lbuser4, lbuser5, lbuser6,
# lbuser7
# ) = range(45)
#
#(brsvd1, brsvd2, brsvd3, brsvd4, 
# bdatum, bacc, blev, brlev, bhlev, bhrlev,
# bplat, bplon, bgor,
# bzy, bdy, bzx, bdx, bmdi, bmks
# ) = range(19)

(lbyr, lbmon, lbdat, lbhr, lbmin, lbday,
 lbyrd, lbmond, lbdatd, lbhrd, lbmind,
 lbdayd, lbtim, lbft, lblrec, lbcode, lbhem,
 lbrow, lbnpt, lbext, lbpack, lbrel, lbfc,
 lbcfc, lbproc, lbvc, lbrvc, lbexp, lbegin, 
 lbnrec, lbproj, lbtyp, lblev, lbrsvd1,
 lbrsvd2, lbrsvd3, lbrsvd4, lbsrce, lbuser1,
 lbuser2, lbuser3, lbuser4, lbuser5, lbuser6,
 lbuser7,
 brsvd1, brsvd2, brsvd3, brsvd4, 
 bdatum, bacc, blev, brlev, bhlev, bhrlev,
 bplat, bplon, bgor,
 bzy, bdy, bzx, bdx, bmdi, bmks,
 ) = range(64)

# --------------------------------------------------------------------
# Assign CF standard name attributes to PP axis codes. (The full list
# of field code keys may be found at
# http://cms.ncas.ac.uk/html_umdocs/wave/@header.)
# --------------------------------------------------------------------
_coord_standard_name = {
    1   : 'air_pressure', 
    2   : 'altitude',
    3   : 'atmosphere_hybrid_sigma_pressure_coordinate',
    4   : 'depth',
    5   : 'model_level_number',        
    6   : 'air_potential_temperature',
    7   : 'atmosphere_sigma_coordinate',
    10  : 'latitude',
    11  : 'longitude',
    13  : 'region',
    14  : 'atmosphere_hybrid_height_coordinate',
    15  : 'height',
    20  : 'time',      # time (gregorian)
    23  : 'time',      # time (360_day)
    40  : 'pseudolevel',        # pseudolevel. THIS IS NOT A STANDARD NAME!!    #dch should this be None?
    }

# --------------------------------------------------------------------
# Assign CF long names attributes to PP axis codes.
# --------------------------------------------------------------------
_coord_long_name = {
    40 : 'pseudolevel',
    }

# --------------------------------------------------------------------
# Assign CF units attributes to PP axis codes.
# --------------------------------------------------------------------
_coord_units = {
    1   : 'hPa',           # air_pressure                      
    2   : 'm',             # altitude         
    3   : '1',             # atmosphere_hybrid_sigma_pressure_coordinate
    4   : 'm',             # depth                                  
    5   : '1',             # model_level_number                         
    6   : 'K',             # air_potential_temperature
    7   : '1',             # atmosphere_sigma_coordinate               
    10  : 'degrees_north', # latitude                               
    11  : 'degrees_east',  # longitude                                
    13  : '',              # region                                     
    14  : '1',             # atmosphere_hybrid_height_coordinate          
    15  : 'm',             # height                                      
    20  : 'days',          # time (gregorian)                    
    23  : 'days',          # time (360_day)
    40  : '1',             # pseudolevel
    }
_coord_Units = {
    1   : _cached_units['hPa'],           # air_pressure                      
    2   : _cached_units['m'],             # altitude         
    3   : _cached_units['1'],             # atmosphere_hybrid_sigma_pressure_coordinate
    4   : _cached_units['m'],             # depth                                  
    5   : _cached_units['1'],             # model_level_number    
    6   : _cached_units['K'],             # air_potential_temperature
    7   : _cached_units['1'],             # atmosphere_sigma_coordinate  
    10  : _cached_units['degrees_north'], # latitude             
    11  : _cached_units['degrees_east'],  # longitude            
    13  : _cached_units[''],              # region               
    14  : _cached_units['1'],             # atmosphere_hybrid_height_coordinate
    15  : _cached_units['m'],             # height             
    20  : _cached_units['days'],          # time (gregorian)                    
    23  : _cached_units['days'],          # time (360_day)
    40  : _cached_units['1'],             # pseudolevel
    }

# --------------------------------------------------------------------
# Assign CF axis attributes to PP axis codes.
# --------------------------------------------------------------------
_coord_axis = {
    1   : 'Z',   # air_pressure                       
    2   : 'Z',   # altitude                                     
    3   : 'Z',   # atmosphere_hybrid_sigma_pressure_coordinate  
    4   : 'Z',   # depth                                        
    5   : 'Z',   # model_level_number                          
    6   : 'Z',   # air_potential_temperature
    7   : 'Z',   # atmosphere_sigma_coordinate                
    10  : 'Y',   # latitude                                     
    11  : 'X',   # longitude                                    
    13  : None,  # region                                       
    14  : 'Z',   # atmosphere_hybrid_height_coordinate          
    15  : 'Z',   # height                                       
    20  : 'T',   # time (gregorian)                                         
    23  : 'T',   # time (360_day)                                         
    40  : None,  # pseudolevel                                    
    }

# --------------------------------------------------------------------
# Assign CF positive attributes to PP axis codes.
# --------------------------------------------------------------------
_coord_positive = {
    1   : 'down',  # air_pressure                     
    2   : 'up',    # altitude                                  
    3   : 'down',  # atmosphere_hybrid_sigma_pressure_coordinate 
    4   : 'down',  # depth                                     
    5   : None,    # model_level_number                         
    6   : 'up',    # air_potential_temperature
    7   : 'down',  # atmosphere_sigma_coordinate               
    10  : None,    # latitude                                   
    11  : None,    # longitude                                   
    13  : None,    # region                                     
    14  : 'up',    # atmosphere_hybrid_height_coordinate         
    15  : 'up',    # height                                      
    20  : None,    # time (gregorian)                                          
    23  : None,    # time (360_day)                                        
    40  : None,    # pseudolevel                                    
    }

# --------------------------------------------------------------------
# Translate LBVC codes to PP axis codes. (The full list of field code
# keys may be found at
# http://cms.ncas.ac.uk/html_umdocs/wave/@fcodes.)
# --------------------------------------------------------------------
_lbvc_codes = {
    1   :  2,   # altitude (Height) 
    2   :  4,   # depth (Depth)
    3   : None, # (Geopotential (= g*height))
    4   : None, # (ICAO height)
    6   :  5,   # model_level_number  
    7   : None, # (Exner pressure)
    8   :  1,   # air_pressure  (Pressure)
    9   :  3,   # atmosphere_hybrid_sigma_pressure_coordinate (Hybrid pressure)
    10  :  7,   # atmosphere_sigma_coordinate (Sigma (= p/surface p))   ## dch check
    16  : None, # (Temperature T)
    19  :  6,   # air_potential_temperature (Potential temperature)
    27  : None, # (Atmospheric) density
    28  : None, # (d(p*)/dt .  p* = surface pressure)
    44  : None, # (Time in seconds)
    65  : 14,   # atmosphere_hybrid_height_coordinate (Hybrid height)
    129 : None, # Surface
    176 : 10,   # latitude    (Latitude)
    177 : 11,   # longitude   (Longitude)
    }

# --------------------------------------------------------------------
# Characters used in decoding LBEXP into a runid
# --------------------------------------------------------------------
_characters = ('a','b','c','d','e','f','g','h','i','j','k','l','m',
               'n','o','p','q','r','s','t','u','v','w','x','y','z', 
               '0','1','2','3','4','5','6','7','8','9'
               )   
_n_characters = len(_characters)

# --------------------------------------------------------------------
# Names of PP extra data codes
# --------------------------------------------------------------------
_extra_data_name = {
    1  : 'x',
    2  : 'y',
    3  : 'y_domain_lower_bound',
    4  : 'x_domain_lower_bound',
    5  : 'y_domain_upper_bound',
    6  : 'x_domain_upper_bound',
    7  : 'z_domain_lower_bound',
    8  : 'x_domain_upper_bound',
    10 : 'title',
    11 : 'domain_title',
    12 : 'x_lower_bound',
    13 : 'x_upper_bound',
    14 : 'y_lower_bound',
    15 : 'y_upper_bound',
    }

# --------------------------------------------------------------------
# Model identifier codes. These are the the last four digits of
# LBSRCE.
# --------------------------------------------------------------------
_lbsrce_model_codes = {
    1111 : 'UM',
    }

class PP(object):
    '''

'''
    def __init__(self, ppfile, umversion):
        '''

**Initialization**

:Parameters:

    ppfile : file

'''

        self.file_offset = ppfile.tell()

#        # Set attributes giving the default data type for reals and
#        # integers. The basic assumption is that data are native
#        # endian.
#        self.float32 = numpy_dtype('<f4').newbyteorder('=')
#        self.int32   = numpy_dtype('<i4').newbyteorder('=')
#        self.str32   = numpy_dtype('<S4').newbyteorder('=')
#
#        # The data types of floats, integers and strings in the PP
#        # file.
#        self.file_float32 = self.float32
#        self.file_int32   = self.int32
#        self.file_str32   = self.str32

        # ------------------------------------------------------------
        # Read the first block control word
        # ------------------------------------------------------------
        bcw1 = ppfile.read(_word_size)

        # Stop now if we have reached the end of the file
        if not bcw1:
            self._nonzero = False
            return

        bcw1 = struct_unpack('>i', bcw1)[0]

        if bcw1 == 256:
            # File is big endian
            endian = '>'
        elif bcw1 == 65536: 
            # File is little endian
            endian = '<'
        else:
            raise IOError(
                "Can't read PP field from %s: Magic number = %s" % 
                (ppfile.name, bcw1))

        self.endian = endian

        # ------------------------------------------------------------
        # Read the integer and real headers and the 2nd and 3rd block
        # control words. Note that 66 = 45+19+2
        # ------------------------------------------------------------
        header = struct_unpack(endian+'45i21f', ppfile.read(66*_word_size))

        self.header = header

#        # ------------------------------------------------------------
#        # Read 1st block control word
#        # ------------------------------------------------------------
#        bcw1 = numpy_fromfile(ppfile, dtype=self.file_int32, count=1)
#   
#        # Stop now if we have reached the end of the file
#        if not bcw1:
#            self._nonzero = False
#            return
#
#        # Change data types if we have a wrong endian PP
#        # file. ('Wrong' simply means different to that assumed by a
#        # PP instance.)
#        bcw1 = bcw1.item()
#        if bcw1 == 65536:        
#            self.file_float32 = self.float32.newbyteorder('S')
#            self.file_int32   = self.int32.newbyteorder('S')
#            self.file_str32   = self.str32.newbyteorder('S')
#        elif bcw1 != 256:
#            raise RuntimeError("Not a PP field: Magic number = %s" % bcw1)
#        
#        # ------------------------------------------------------------
#        # Read the integer and real headers (and the 2nd and 3rd block
#        # control words).
#        # ------------------------------------------------------------
#        lhd = numpy_fromfile(ppfile, dtype=self.file_int32  , count=45)
#        bhd = numpy_fromfile(ppfile, dtype=self.file_float32, count=21)
        
        # ------------------------------------------------------------
        # Set some derived metadata quantities
        # ------------------------------------------------------------
#        self.lbtim_ia, ib            = divmod(lhd.item(lbtim,), 100)
        self.lbtim_ia, ib            = divmod(header[lbtim], 100)
        self.lbtim_ib, self.lbtim_ic = divmod(ib, 10)

        if self.lbtim_ic == 1:
            calendar = 'gregorian'
        elif self.lbtim_ic == 4:
            calendar = '365_day'
        else:
            calendar = '360_day'
              
    #   LBYR   = lhd.item(lbyr,)
    #   LBMON  = lhd.item(lbmon,) 
    #   LBDAT  = lhd.item(lbdat,) 
    #   LBHR   = lhd.item(lbhr,) 
    #   LBMIN  = lhd.item(lbmin,) 
    #   LBYRD  = lhd.item(lbyrd,) 
    #   LBMOND = lhd.item(lbmond,) 
    #   LBDATD = lhd.item(lbdatd,) 
    #   LBHRD  = lhd.item(lbhrd,) 
    #   LBMIND = lhd.item(lbmind,) 
    
#        lbvtime = tuple(lhd[lbyr :lbmin+1].tolist())
#        lbdtime = tuple(lhd[lbyrd:lbmind+1].tolist())
        lbvtime = header[lbyr :lbmin+1]
        lbdtime = header[lbyrd:lbmind+1]
        self.lbvtime = lbvtime
        self.lbdtime = lbdtime

        time_units = 'days since %d-1-1' %  lbvtime[0]

        cache_key = (time_units, calendar)
        reftime = _cached_units.get(cache_key, None)
        if reftime is None:
            reftime = Units(time_units, calendar)
            _cached_units[cache_key] = reftime
        #--- End: if
        self.reftime = reftime    

#       if cache_key in _cached_units:
#            self.reftime = _cached_units[cache_key]
#        else:
#            units = Units(time_units, calendar)
#            _cached_units[cache_key] = units
#            self.reftime = units    

        cache_key = (time_units, calendar, lbvtime)
        vtime = _cached_time.get(cache_key, None)
        if vtime is None:
            # It is important to use the same time_units as dtime
            vtime =  netCDF4_date2num(
                netCDF4_netcdftime_datetime(*lbvtime), time_units, calendar)
            _cached_time[cache_key] = vtime
        #--- End: if
        self.vtime = vtime

#        if cache_key in _cached_time:
#            self.vtime = _cached_time[cache_key]
#        else:
#            # It is important to use the same time_units as dtime
#            vtime =  netCDF4_date2num(
#                netCDF4_netcdftime_datetime(*lbvtime), time_units, calendar)
#            _cached_time[cache_key] = vtime
#            self.vtime = vtime
#        #--- End: if

        cache_key = (time_units, calendar, lbdtime)
        dtime = _cached_time.get(cache_key, None)
        if dtime is None:
            # It is important to use the same time_units as vtime
            dtime =  netCDF4_date2num(
                netCDF4_netcdftime_datetime(*lbdtime), time_units, calendar)
            _cached_time[cache_key] = dtime
        #--- End: if
        self.dtime = dtime

#        if cache_key in _cached_time:
#            self.dtime = _cached_time[cache_key]
#        else:
#            # It is important to use the same time_units as vtime
#            dtime =  netCDF4_date2num(
#                netCDF4_netcdftime_datetime(*lbdtime), time_units, calendar)
#            _cached_time[cache_key] = dtime
#            self.dtime = dtime
# #       #--- End: if

        # Infer model name and version from the PP header
        header_umversion, source = divmod(header[lbsrce], 10000)

        if header_umversion > 0 and len(umversion) <= 3:
            header_umversion = str(header_umversion)
            model_umversion = header_umversion
            self.umversion  = header_umversion
        else:
            model_umversion = None
            self.umversion  = umversion

        # Set source
        source = _lbsrce_model_codes.get(source, None)
        if source is not None and model_umversion is not None:
            source += ' vn%s' % model_umversion

        self.source = source

        # ------------------------------------------------------------
        # Set the T, Z, Y and X axis codes
        # ------------------------------------------------------------
        self.site_time_cross_section = False
        self.timeseries              = False

        LBCODE = header[lbcode]
        if LBCODE in (1, 101, 2, 102):
            self.ix = 11
            self.iy = 10
        elif LBCODE >= 10000:
            temp, ix = divmod(LBCODE, 10000)
            ix, iy = divmod(ix, 100)
            # Determine if we have a site-time cross section and, if
            # so, if it is a timeseries
            if ix == 13 and iy == 23:
                self.site_time_cross_section = True
#                self.timeseries = (lhd.item(lbuser3,) == lhd.item(lbrow,))
                self.timeseries = (header[lbuser3] == header[lbrow])

            self.ix = ix
            self.iy = iy               
        else:
            self.ix = None
            self.iy = None
        
        # Set iv from LBVC
#        self.iv = _lbvc_codes.get(lhd.item(lbvc,), None)
        self.iv = _lbvc_codes.get(header[lbvc], None)
        
        # Set it
        if calendar == 'gregorian':
            self.it = 20
        else:
            self.it = 23
        
#        self.lhd = lhd
#        self.bhd = bhd  

        self.ppfile = ppfile
        self.file   = abspath(ppfile.name)

        # ------------------------------------------------------------
        # Set the data and extra data
        # ------------------------------------------------------------
        self.data()

        self._nonzero = True
    #--- End: def

    def __nonzero__(self):
        '''

x.__nonzero__() <==> bool(x)

'''
        return self._nonzero
    #--- End: if

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return self.fdr()
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        out = [self.fdr()]        
        
        attrs = ('endian',
                 'reftime', 'vtime', 'dtime',
                 'umversion', 'source',
                 'it', 'iv', 'ix', 'iy', 
                 'site_time_cross_section', 'timeseries',
                 'file')

        for attr in attrs:
            out.append('%s=%s' % (attr, getattr(self, attr, None)))
            
        out.append('')

        return '\n'.join(out)   
    #--- End: def

    def fdr(self):
        '''
        '''
        fdr = []

        for name, value in zip(_header_items, self.header):
            fdr.append('%s::%s' % (name, value))

        fdr = textwrap.fill(' '.join(fdr), width=79)
        fdr = [fdr.replace('::', ': ')]

        if self.extra:
            fdr.append('EXTRA DATA:')
            for key in sorted(self.extra):
                fdr.append('%s: %s' % (key, str(self.extra[key])))
        #--- End: if

        fdr.append('')

        return '\n'.join(fdr)
    #--- End: def

    def printfdr(self):
        '''
        '''
        print self.fdr()
    #--- End: def

    def extra_data(self):
        '''
        
Read the extra data (if any) of the PP field at the current position
in the given PP file, decode it and store it in the field's metadata
object.

**Excerpt from UMDP F3 vn7.8**

The data record may include 'extra data' in addition to the usual
grid-point values. Cross-section fields must always be followed by
extra data giving the x- and y-coordinate values of each column and
row of the grid. (This is to allow irregular grid). It is also
possible to use extra data in conjunction with other types of field,
eg. a character string description of the field. The header variable
LBEXT shows the length of extra data associated with a field. Thus the
total length (in words) of the data record (LBLREC) equals the number
of grid-point values plus LBEXT. Extra data is arranged in vectors,
each of which is made up of an integer code followed by data
values. The integer code is (1000xIA + IB), where IA is the length of
the vector in words (i.e. usually the number of data values) and IB is
a standard code. A zero integer code indicates no (more) extra data.
For cross-sections the extra data MUST start with an x-vector followed
by a y-vector; optionally other extra data may follow.

:Returns:

    None

**Examples**

'''
        ppfile = self.ppfile

        # Still here? The parse the extra data
        extra = {}
    
        domain_titles = []

        endian = self.endian
        integer = endian + 'i'

        n_words_read = 0        
        while n_words_read < self.header[lbext]:
    
            intcode = struct_unpack(integer, ppfile.read(_word_size))

            # Stop if we have run out of extra data
            if not (intcode or intcode[0]):
                break
    
            # Find ia = size of this extra data variable, 
            #      ib = type of this extra data variable
            ia, ib = divmod(intcode[0], 1000)
          
            if ib in (10, 11):
                datatype = 's'
            else:
                datatype = 'f'
                            
            fmt = "%s%d%s" % (endian, ia, datatype)
            ext_data = struct_unpack(fmt, ppfile.read(ia*_word_size))

            if datatype == 's':
                title = ''.join(ext_data)
                if ib == 11:
                    domain_titles.append(title)
                else:
                    extra[_extra_data_name[ib]] = numpy_array((title,))
            else:
                extra[_extra_data_name[ib]] = numpy_array(ext_data)

            n_words_read += ia + 1
        #--- End: while    
    
        for bounds_type in ('', '_domain'):    
            for axis in ('x', 'y'):
                axis_bounds_type = axis + bounds_type
                lower  = axis_bounds_type + '_lower_bound'
                upper  = axis_bounds_type + '_upper_bound'
                bounds = axis_bounds_type + '_bounds'            
                if lower in extra and upper in extra:   
                    extra[bounds] = numpy_column_stack((extra[lower],
                                                        extra[upper]))
                #--- End: if
                extra.pop(lower, None)
                extra.pop(upper, None)
        #--- End: for
    
        # If we have domain titles then add them to the extra data
        # dictionary as a numpy array
        if domain_titles:
            extra[_extra_data_name[11]] = numpy_array(domain_titles)
    
        # Add the extra data to the metadata object
        self.extra = extra

        # Skip the 4th block control word so that we're ready to read the
        # next PP field
        ppfile.seek(_word_size, 1)
    #--- End: def

    def data(self):
        '''
    
:Parameters:
    
    None
        
:Returns:
    
    None
    
'''
#        lhd    = self.lhd
#        bhd    = self.bhd
        header = self.header

        ppfile = self.ppfile

#        LBEXT = lhd.item(lbext,)
#        filesize = lhd.item(lblrec,) - LBEXT
        LBEXT = header[lbext]
        arraysize = header[lblrec] - LBEXT
    
        if not arraysize:
            self.data = None
            return
    
        # Set the data type
#        binary_mask = False
        LBUSER1 = header[lbuser1]
        if LBUSER1 == 1:
            datatype = numpy_dtype('float32')
        elif LBUSER1 == 2:
            datatype = numpy_dtype('int32')
        elif LBUSER1 == 3:
            datatype = numpy_dtype(bool)
        else:
            # Unknown data type => assume real
            datatype = numpy_dtype('float32')
    
#        file_offset = ppfile.tell()

        # Create the data object by setting up a parameters dictionary to
        # initialize a PPFileArray object
#        LBROW = lhd.item(lbrow,)
#        LBNPT = lhd.item(lbnpt,)
        LBROW = header[lbrow]
        LBNPT = header[lbnpt]
        parameters = {'file'       : self.file,
                      'file_offset': self.file_offset,
                      'dtype'      : datatype,
                      'shape'      : (LBROW, LBNPT),
                      'size'       : LBROW*LBNPT,
                      'ndim'       : 2,
#                      'lbpack'     : lhd.item(lbpack,),
#                      'lblrec'     : arraysize,
#                      'binary_mask': binary_mask,
                      }
    
#        # Set the _FillValue from BMDI, unless it's -1.0e30, which is
#        # a flag for the field containing no missing data. Note that
#        # the _FillValue must be of the same type as the data values.
#        BMDI = bhd.item(bmdi,)
#        if BMDI == -1.0e30:
#            BMDI = None
#        elif datatype == self.file_int32:
#            BMDI = int(BMDI)        
#        parameters['_FillValue'] = BMDI
#        self.BMDI = BMDI
#    
#        # Treat BDATUM as an add_offset if it is not 0.0
#        BDATUM = bhd.item(bdatum,)
#        if abs(BDATUM) > ATOL():
#            parameters['add_offset'] = BDATUM
#        else:
#            parameters['add_offset'] = 0
#
#        # Treat BMKS as a scale_factor if it is not 0.0 or 1.0
#        BMKS = bhd.item(bmks,)
#        if abs(BMKS-1.0) > ATOL() + RTOL() and abs(BMKS) > ATOL():
#            parameters['scale_factor'] = BMKS
#        else:
#            parameters['scale_factor'] = 1
        
        self.data = PPFileArray(**parameters)

        # ------------------------------------------------------------
        # Set the extra data
        # ------------------------------------------------------------ 
        if LBEXT <= 0:
            # There is no extra data
            ppfile.seek((arraysize+1)*_word_size, 1) 
            self.extra = {}
        else:      
            # There is extra data
            ppfile.seek(arraysize*_word_size, 1)
            self.extra_data()
    #--- End: def

#--- End: class
        
        
def unrotated_latlon(rotated_lat, rotated_lon, pole_lat, pole_lon):
    '''

Create 2-d arrays of unrotated latitudes and longitudes.

'''
    # Make sure rotated_lon and pole_lon is in [0, 360)
    pole_lon = pole_lon % 360.0

    # Convert everything to radians
    pole_lon *= _pi_over_180
    pole_lat *= _pi_over_180

    cos_pole_lat = numpy.cos(pole_lat)
    sin_pole_lat = numpy.sin(pole_lat)

    # Create appropriate copies of the input rotated arrays
    rot_lon = rotated_lon.copy()
    rot_lat = rotated_lat.view()

    # Make sure rotated longitudes are between -180 and 180
    rot_lon %= 360.0
    rot_lon = numpy.where(rot_lon < 180.0, rot_lon, rot_lon-360)

    # Create 2-d arrays of rotated latitudes and longitudes in radians
    nlat = rot_lat.size
    nlon = rot_lon.size
    rot_lon = numpy.resize(numpy.deg2rad(rot_lon), (nlat, nlon))    
    rot_lat = numpy.resize(numpy.deg2rad(rot_lat), (nlon, nlat))
    rot_lat = numpy.transpose(rot_lat, axes=(1,0))

    # Find unrotated latitudes
    CPART = numpy.cos(rot_lon) * numpy.cos(rot_lat)
    sin_rot_lat = numpy.sin(rot_lat)
    x = cos_pole_lat * CPART + sin_pole_lat * sin_rot_lat
    x = numpy.clip(x, -1.0, 1.0)
    unrotated_lat = numpy.arcsin(x)
    
    # Find unrotated longitudes
    x = -cos_pole_lat*sin_rot_lat + sin_pole_lat*CPART
    x /= numpy.cos(unrotated_lat)   # dch /0 or overflow here? surely
                                    # lat could be ~+-pi/2? if so,
                                    # does x ~ cos(lat)?
    x = numpy.clip(x, -1.0, 1.0)
    unrotated_lon = -numpy.arccos(x)
    
    unrotated_lon = numpy.where(rot_lon > 0.0, 
                                -unrotated_lon, unrotated_lon)
    if pole_lon >= ATOL():
        SOCK = pole_lon - _pi
    else:
        SOCK = 0
    unrotated_lon += SOCK

    # Convert unrotated latitudes and longitudes to degrees
    unrotated_lat = numpy.rad2deg(unrotated_lat)
    unrotated_lon = numpy.rad2deg(unrotated_lon)

    # Return unrotated latitudes and longitudes
    return unrotated_lat, unrotated_lon
#--- End: def

def _insert_data(c, data=None, bounds=None, climatology=False):
    '''

:Parameters:

    c : cf.Coordinate

    data : array-like, optional

    bounds : array-like, optional

    climatology : bool, optional

:Returns:

    None

'''
    fill_value = c.fill_value()
    units = c.Units
    
    if data is not None:
        data = Data(data, units=units, fill_value=fill_value)
        
    if bounds is not None:
        bounds = Data(bounds, units=units, fill_value=fill_value)
        if climatology:
            c.climatology = True
    #--- End: if

    c.insert_data(data, bounds=bounds, copy=False)

    return c
#--- End: def

def _set_coordinate_data(c, p=None,
                         array=None, bounds_array=None, climatology=False, 
                         coord_type=None, extra_type=None,
                         parameters={}):
    '''
    
Set a coordinate's data in place.

:Parameters:

    c : Coordinate

    p : PP
        A complete PP field (metadata, data and extra data).

    array : array-like, optional

    bounds_array : array-like, optional

    climatology : bool, optional

    coord_type : str, optional

    extra_type: str, optional

    parameters : dict, optional

:Returns:

    None

'''
#    lhd = p.lhd
#    bhd = p.bhd
 
    header = p.header

    #-----------------------------------------------------------------
    # Set time data from vtime and dtime
    #-----------------------------------------------------------------
    if coord_type == 't':
        # This PP field's data array does not have time as one of its
        # two axes, so create a size 1 dimension coordinate for time
        ib = p.lbtim_ib
        vtime = p.vtime
        dtime = p.dtime
        if ib <= 1 or vtime >= dtime: 
            array = numpy_array([vtime], dtype=float)
        elif ib == 3:
            # The field is a time mean from T1 to T2 for each year
            # from LBYR to LBYRD
            climatology = True

            lbvtime = p.lbvtime
            lbdtime = p.lbdtime
            reftime = p.reftime
            cache_key = (reftime.units, reftime.calendar, lbvtime, lbdtime)
            ctime = _cached_ctime.get(cache_key, None)
            if ctime is None:
                ctime = Datetime(*lbdtime)
                ctime.year = lbvtime[0]
                if ctime < Datetime(*lbvtime):
                    ctime.year += 1
                ctime = Data(ctime, p.reftime).array.item()
                _cached_ctime[cache_key] = ctime
            #--- End: if

            array        = numpy_array([0.5*(vtime + ctime)])
            bounds_array = numpy_array([[vtime, dtime]], dtype=float)    
        else:
            array        = numpy_array([0.5*(vtime + dtime)])
            bounds_array = numpy_array([[vtime, dtime]], dtype=float)                
        #--- End: if            

        _insert_data(c, array, bounds_array, climatology)
        return c   
    #--- End: if

    origin        = None
    create_bounds = True

    # ----------------------------------------------------------------
    #
    # ----------------------------------------------------------------
    if coord_type == 'x':
        if abs(header[bdx]) <= ATOL() or p.timeseries: # DCH 
            # Create an X coordinate data object from the field's
            # extra data
            if coord_type in p.extra:
                array = p.extra[coord_type]
            
            coord_bounds = coord_type+'_bounds'
            if coord_bounds in p.extra:
                 bounds_array = p.extra[coord_bounds]
                
        else:
            # Find parameters for creating X coordinate data and
            # coordinate bounds data objects
            delta  = header[bdx]
            origin = header[bzx]
            size   = header[lbnpt]

            if (p.ix == 11 and origin + delta*size > 360.0):
                origin -= 360.0

            if p.ix in (13, 40, 99):
                # 13 = region, 40 = pseudolevel, 99 = ???
                create_bounds = False

    elif coord_type == 'y':
        if abs(header[bdy]) <= ATOL() or p.timeseries: # DCH Set a
            # Create a Y coordinate data object from the field's extra
            # data
            if coord_type in p.extra:
                array = p.extra[coord_type]
            
            coord_bounds = coord_type+'_bounds'
            if coord_bounds in p.extra:
                bounds_array = p.extra[coord_bounds]

        else:
            # Find parameters for creating Y coordinate data and
            # coordinate bounds data objects
            delta  = header[bdy]
            origin = header[bzy]
            size   = header[lbrow]

            if (p.iy == 11 and origin + delta*size > 360.0):
                origin -= 360.0

            if p.iy in (13, 40, 99):
                # 13 = region, 40 = pseudolevel, 99 = ???
                create_bounds = False       
    #--- End: if
        
    if extra_type in p.extra:
        if not extra_type.endswith('bounds'):
            # Create a coordinate data object from the field's extra
            # data
            array = p.extra[extra_type]
        else:
            # Create a coordinate bounds data object from the field's
            # extra data
            bounds_array = p.extra[extra_type]
    #--- End: if

    if origin is not None:
        # Create a 1-d coordinate data object from an origin, size and
        # delta
        array = numpy_arange(origin+delta, origin+delta*(size+1), delta, dtype='float32')

        # Create the 1-d coordinate's bounds array
        if create_bounds:
            bounds_array = numpy_empty((size, 2), dtype='float32')
            delta_by_2 = 0.5 * delta
            bounds_array[:, 0] = array - delta_by_2
            bounds_array[:, 1] = array + delta_by_2
    #--- End: if 

    # Set the coordinate's data array
    _insert_data(c, array, bounds_array, climatology)
   
    # Return coordinate
    return c
#--- End: def

def _create_Coordinate(domain, key, axis_code=None, p=None, pubattr={},
                       array=None, bounds_array=None, climatology=False, 
                       coord_type=None, extra_type=None,
                       parameters=None, dimensions=[], units=None,
                       cache_key=None, aux=False):
    '''
    
Create a coordinate variable.

:Parameters:

    domain : Domain

    key : str

    p : PP
        A complete PP field (metadata, data and extra data).

    array : array-like, optional

    bounds_array : array-like, optional

    climatology : bool, optional

    coord_type : str, optional

    extra_type: str, optional

    parameters : dict, optional

    dimensions : list, 

    units : Units, optional
        Override the default units with those given.
       
:Returns:

    out : Coordinate

'''
    if cache_key in _cached_coordinate:
        c = _cached_coordinate[cache_key]
        domain.insert_coord(c, key=key, axes=dimensions, copy=True)
    #--- End: if

        
    if not aux:
        c = DimensionCoordinate()
    else:
        c = AuxiliaryCoordinate()

    if axis_code:
        # Set attributes
        axis = _coord_axis[axis_code]
        if axis is not None:
            c.axis = axis

        positive = _coord_positive[axis_code]
        if positive is not None:
            c.positive = positive

        standard_name = _coord_standard_name[axis_code]
        if standard_name is not None:
            c.standard_name = standard_name
        else:
            c.long_name = _coord_long_name[axis_code]
        #--- End: if

        if units is not None:
            c.Units = units
        elif axis_code in (20, 23):
            # Time
            c.Units = p.reftime
        elif 100 < p.header[lbcode] < 10000:
            # Rotated lat-lon
            if axis_code == 10:
                c.Units         = _cached_units['degrees']
                c.standard_name = 'grid_latitude'
            elif axis_code == 11:
                c.Units         = _cached_units['degrees']
                c.standard_name = 'grid_longitude'
            else:
                c.Units = _coord_Units[axis_code] 
        else:
            c.Units = _coord_Units[axis_code] 
    #--- End: if

    # Apply extra public attributes, or overwrite existing ones
    for prop, value in pubattr.iteritems():
        if value is not None:
            c.setprop(prop, value)
        elif c.hasprop(prop):
            c.delprop(prop)
    #--- End: for

    # Set the coordinate's netCDF variable name - why, dch??
    c.ncvar = getattr(c, 'standard_name', 
                      getattr(c, 'long_name', None))
        
    # data
    _set_coordinate_data(c, p=p,
                         array        = array,
                         bounds_array = bounds_array,
                         climatology  = climatology,
                         coord_type   = coord_type,
                         extra_type   = extra_type, 
                         parameters   = parameters)  

    domain.insert_coord(c, key=key, axes=dimensions, copy=True)

    if cache_key:
        _cached_coordinate[cache_key] = c

    return c
#--- End: def

def _decode_exp(lbexp):
    '''
    
Decode the integer value of LBEXP in the PP header into a runid.

If this value has already been decoded, then it will be returned from
the cache, otherwise the value will be decoded and then added to the
cache.

:Parameters:

    lbexp : int
        The value of LBEXP in the PP header.

:Returns:

    out : str
       A string derived from LBEXP. If LBEXP is a negative integer
       then that number is returned as a string.

**Examples**

>>> _decode(2004)
'aaa5u'
>>> _decode(-34)
'-34'

'''
    if lbexp in _cached_runid:
        # Return a cached decoding of this LBEXP
        return _cached_runid[lbexp]

    if lbexp < 0:
        return str(lbexp)

    # Convert LBEXP to a binary string, filled out to 30 bits with
    # zeros
    bits = bin(lbexp)
    bits = bits.lstrip('0b').zfill(30)

    # Step through 6 bits at a time, converting each 6 bit chunk into
    # a decimal integer, which is used as an index to the characters
    # lookup list.
    runid = []
    for i in xrange(0,30,6):
        index = int(bits[i:i+6], 2) 
        if index < _n_characters:
            runid.append(_characters[index])
    #--- End: for
    runid = ''.join(runid)

    # Enter this runid into the cache
    _cached_runid[lbexp] = runid

    # Return the runid
    return runid
#--- End: def 

def _test_pp_condition(pp_condition, p=None):
    '''

Return True if a field satisfies the condition specified for a PP
STASH code to standard name conversion.

:Parameters:

    pp_condition : str

    p : PP
        A complete PP field (metadata, data and extra data).

:Returns:

   out : bool
       True if a field satisfies the condition specified, False
       otherwise.

**Examples**

>>> ok = _test_pp_condition('true_latitude_longitude', p=p)

'''
    if pp_condition == '':
        # Return True if no condition is set
        return True
    
    # Still here?
    header = p.header
    code = header[lbcode]

    if pp_condition == 'true_latitude_longitude':
        if code in (1, 2):
            return True

        # Check pole location in case of incorrect LBCODE
        if (abs(header[bplat]-90.0) <= ATOL() + RTOL()*90.0 and 
            abs(header[bplon]) <= ATOL()):
            return True

    elif pp_condition == 'rotated_latitude_longitude':
        if code in (101, 102):
            return True

        # Check pole location in case of incorrect LBCODE
        if not (abs(header[bplat]-90.0) <= ATOL() + RTOL()*90.0 and 
                abs(header[bplon]) <= ATOL()):
            return True
        
    else:
        raise ValueError(
            "Unknown PP condition in STASH code conversion table: %r" %
            pp_condition)

    # Still here? Then the condition has not been satisfied.
    return
#--- End: def

def _test_umversion(valid_from, valid_to, p=None):
    '''

Return True if the UM version applicable to this field is within the
given range.

If possible, the UM version is derived from the PP header and stored
in the metadata object. Otherwise it is taken from the *umversion*
parameter.

:Parameters:

    valid_from : str

    valid_to : str

    p : PP
        A complete PP field (metadata, data and extra data).

:Returns:

    out : bool
        True if the UM version applicable to this field is within the
        range, False otherwise.

**Examples**

>>> ok = _test_umversion('401', '505', p=p)

''' 
    if valid_from is '':
        valid_from = None

    if valid_to is '':
        if valid_from <= p.umversion:
            return True 
    elif valid_from <= p.umversion <= valid_to:
        return True 

    return False
#--- End: def

def _field_attributes(p):
    '''

Set public and private attributes on the domain (including the
standard name).
'''
    header = p.header

    attributes = {}
    properties = {}

    attributes['pp']   = p
    attributes['file'] = p.ppfile.name

    properties['Conventions'] = __Conventions__
    properties['history']     = p.history
    properties['runid']       = _decode_exp(p.header[lbexp])

    source = p.source
    if source is not None:
        properties['source'] = source

    # Set title
    if 'title' in  p.extra:
        properties['title'] = p.extra['title']
        
    # ----------------------------------------------------------------
    # Set the field's standard_name, long_name and units from its
    # STASH code and possibly other properties
    # ----------------------------------------------------------------
    stash    = header[lbuser4]
    submodel = header[lbuser7]

    properties['stash_code'] = stash
    properties['submodel']   = submodel

    BMDI = header[bmdi]
    if BMDI == -1.0e30:
        BMDI = None
#    elif datatype == self.file_int32:
#        BMDI = int(BMDI)        # dch reinstate

    if BMDI is not None:
        properties['_FillValue'] = BMDI

    p.cf_info      = {}
    p.pp_condition = ''

    # The STASH code has been set in the PP header, so try to find
    # its standard_name from the conversion table
    if (submodel, stash) in _stash2standard_name:
        for (long_name, 
             units,
             valid_from,
             valid_to, 
             standard_name,
             cf_info,
             pp_condition) in _stash2standard_name[(submodel, stash)]:

            # Check that conditions are met             
            version_ok      = _test_umversion(valid_from, valid_to, p=p)
            pp_condition_ok = _test_pp_condition(pp_condition, p=p)

            if not (version_ok and pp_condition_ok):                    
                continue

            # Still here? Then we have our standard_name, etc.
            properties['long_name'] = long_name.rstrip()

            if units:
                properties['units'] = units
#            if standard_name:
#                properties['standard_name'] = standard_name
                                    
            p.cf_info = cf_info
            p.pp_condition = pp_condition
                
            break
        #--- End: for

#    elif stash:
#        # STASH code with no standard_name
#        properties['long_name'] = 'PP_%d_%d' % (submodel, stash)
#    else:
#        # No STASH code and no standard_name
#        properties['long_name'] = 'PP_%d_fc%d' % (submodel, p.lhd[lbfc])
#    #--- End: if

    # If there is no standard name then set a identifying name based
    # on the submodel and STASHcode (or field code).
#    if 'standard_name' not in properties:
    if stash:
        identity = 'PP_%d_%d_vn%s' % (submodel, stash, p.umversion)
    else:
        identity = 'PP_%d_fc%d_vn%s' % (submodel, header[lbfc], p.umversion)

    if p.pp_condition is not '':
        identity += '_%s' % p.pp_condition

    attributes['id'] = identity
    
            
#    #--- End: if

    # If there is no long name then set a default
    if 'long_name' not in properties:
        properties['long_name'] = identity

#        if stash:
#            properties['long_name'] = 'PP_%d_%d' % (submodel, stash)
#        else:
#            properties['long_name'] = 'PP_%d_fc%d' % (submodel, p.lhd[lbfc])        
    #--- End: if

    # Set the field's coordinate's netCDF variable name. Note that
    # there is no danger of f.ncvar being None, since if f has no
    # standard_name then it is guaranteed to have id.
#    attributes['ncvar'] = properties.get('standard_name', attributes.get('id', 'ncvar'))
  

#        try:
#            f.getprop('long_name')
#            try:   # dch this is a nightmare
#                if not (f.getprop('units') == '%' and f.getprop('scale_factor') == 0.01):
#                    f.setprop('units', '%s %s' % (f.getprop('scale_factor'), f.getprop('units')))
#                    f.delprop('scale_factor')
#            except AttributeError:
#                pass
#        except AttributeError:
#            # Default long name in the absence of a conversion
#            f.setprop('long_name', 'STASHcode=%s' % stash)
#    #--- End: if

#    return f
    return properties, attributes
#--- End: def

def read_stash2standard_name(table=None, delimiter='!'):
    ''' 

Read the STASH to standard_name conversion table, as found at
http://puma.nerc.ac.uk/STASH_to_CF/STASH_to_CF.txt, into a dictionary.

:Parameters:

    table : str, optional
        Use the conversion table at this file location. By default the
        table will be looked for at
        ``os.path.join(os.path.dirname(cf.__file__),'etc/STASH_to_CF.txt')``

    delimiter : str, optional
        The table's delimiter. By default, ``!`` is taken as the
        delimiter.

:Returns:

    out : dict
        A dictionary of tuples of lists

*Examples*

>>> stash2sn = read_stash2standard_name()
>>> print stash2sn[(1, 2)]
(['U COMPNT OF WIND AFTER TIMESTEP     ',
  'm s-1',
  '',
  '',
  'eastward_wind',
  '',
  'true_latitude_longitude'],
 ['U COMPNT OF WIND AFTER TIMESTEP     ',
  'm s-1',
  '',
  '',
  'x_wind',
  '',
  'rotated_latitude_longitude'])

'''

    # 0  Model           
    # 1  STASH code      
    # 2  STASH name      
    # 3  units           
    # 4  valid from UM vn
    # 5  valid to   UM vn
    # 6  standard_name   
    # 7  CF extra info   
    # 8  PP extra info

    if table is None:
        # Use default conversion table
        package_path = os.path.dirname(__file__)
        table = os.path.join(package_path, 'etc/STASH_to_CF.txt')
    #--- End: if

    lines = csv.reader(open(table, 'r'), 
                       delimiter=delimiter, skipinitialspace=True)

    raw_list = []
    [raw_list.append(line) for line in lines]

    # Get rid of comments
    for line in raw_list[:]:
        if line[0].startswith('#'):
            raw_list.pop(0)
            continue
        break
    #--- End: for

    # Convert to a dictionary which is keyed by (submodel, STASHcode)
    # tuples

    (model, stash, name,
     units, 
     valid_from, valid_to,
     standard_name, cf, pp) = range(9)
        
    stash2sn = {}
    for x in raw_list:
        key = (int(x[model]), int(x[stash]))
        try:            
            cf_info = {}
            if x[cf]:
                for d in x[7].split():
                    if d.startswith('height='): 
                        cf_info['height'] = re.split(_number_regex, d,
                                                     re.IGNORECASE)[1:4:2]
                        if cf_info['height'] == '':
                            cf_info['height'][1] = '1'

                    if d.startswith('below_'):
                        cf_info['below'] = re.split(_number_regex, d,
                                                     re.IGNORECASE)[1:4:2]
                        if cf_info['below'] == '':
                            cf_info['below'][1] = '1'

                    if d.startswith('where_'):         
                        cf_info['where'] = d.replace('where_', 'where ', 1)
                    if d.startswith('over_'):         
                        cf_info['over'] = d.replace('over_', 'over ', 1)

            x[cf] = cf_info                    
        except IndexError:
            pass

        x[pp] = x[pp].rstrip()

        line = (x[name:],)

        if key in stash2sn:
            stash2sn[key] += line
        else:
            stash2sn[key] = line

    #--- End: for

    return stash2sn
#--- End: def

# ---------------------------------------------------------------------
# Create the STASH code to standard_name conversion dictionary
# ---------------------------------------------------------------------
_stash2standard_name = read_stash2standard_name()

def read(infile, umversion='405', verbose=False):
    ''' 

Read fields from an input PP file on disk.

The file may be big or little endian.

:Parameters:

    filename : file or str
        A string giving the file name, or an open file object, from
        which to read fields.

    umversion : str, optional
        The Unified Model (UM) version to be used when decoding the PP
        header. Valid versions are, for example, ``'402'``,
        ``'606.3'`` and ``'802'``.  The default version is
        ``'405'``. The version is ignored if it can be inferred from
        the PP headers, which will generally be the case for files
        created at versions 5.3 and later. Note that the PP header can
        not encode tertiary version elements (such as the ``3`` in
        ``'6.6.3'``), so it may be necessary to provide a UM version
        in such cases.
    
    verbose : bool, optional

:Returns:

    out : FieldList
        The fields in the file.

**Examples**

>>> f = read('file.pp')
>>> f = read('*/file[0-9].pp', umversion='7.8')

'''    
    # coord_type: A short string which acts as .... Valid values are
    # 't'  : time 
    #
    # 'v'  : an axis other than time which has the the same value for
    #        all data points, as described by LBVC
    #
    # 'p'  : pseudolevel
    #
    # 'rwl': radiation wavelength
    #
    # 'x'  : The X axis of the data array
    #
    # 'y'  : The Y axis of the data array
    

    # ------------------------------------------------------------
    # Preliminaries
    # ------------------------------------------------------------
    # Open the file, if it is not already open an open file object
    try:
        ppfile = open(infile, 'rb') 
    except TypeError:
        ppfile = infile

    # Initialize the output list of fields
    fields_in_file = FieldList()

#    history = '%s Converted from PP by cf-python v%s' % \
#        (time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
#         __version__)
    history = 'Converted from PP by cf-python v%s' % __version__


    # ****************************************************************
    # Loop round each PP field in the file, reading it into a field
    # ****************************************************************
    while True:

        # Set the FREE_MEMORY constant
#        SET_FREE_MEMORY()

        dimN   = 0  # Counter for dimension coordinates
        auxN   = 0  # Counter for auxiliary coordinates
#        transN = 0  # Counter for coordinate references

        # ============================================================
        # Get the next PP field's metadata and data and find some
        # derived metadata quantities.
        # ============================================================
        # Get the PP field (header and data and extra data)
        p = PP(ppfile, umversion)

        # Stop now if we have reached the end of the file
        if not p:
            break

#        lhd = p.lhd
#        bhd = p.bhd

        header = p.header

#        if not p.header_umversion:
#            # The header does not encode the UM version, so set it.
#            p.umversion = umversion
#        elif umversion != int(umversion):
#            # Given UM version has an tertiary element (such as the 3
#            # in 6.6.3), so override what's in the header.
#            p.umversion = umversion

        p.history = history

        # ============================================================
        # Initialize the field
        # ============================================================
        domain = Domain()

        # Create the field's properties and attributes
        properties, attributes = _field_attributes(p)

        axis_name = {}
        axis_dim  = {}
        
        # ============================================================
        # Create the field's domain
        # ============================================================

        LBVC    = header[lbvc]
        LBLEV   = header[lblev]
        LBUSER5 = header[lbuser5]

        dtime   = p.dtime
        vtime   = p.vtime
        reftime = p.reftime

        # ------------------------------------------------------------
        # Create a TIME dimension coordinate
        # ------------------------------------------------------------
        dim  = 'dim%(dimN)d' % locals()
        dimN += 1         # Increment dimension number
        tdim = dim      

        # Set coordinate type and axis code
        if p.ix in (20, 23):
            coord_type = 'x'
            axis_code  = p.ix
            # Flag that we have already created an 'X' coordinate
            p.ix = None
            cache_key = None
        elif p.iy in (20, 23):
            coord_type = 'y'
            axis_code  = p.iy
            # Flag that we have already created a 'Y' coordinate
            p.iy = None           
            cache_key = None
        else:
            coord_type = 't'
            axis_code  = p.it
            cache_key = ('time', reftime, vtime, dtime, p.lbtim_ib)

        #--- End: if

        # Set the coordinate's data
        if p.timeseries:
            # This PP field is a timeseries. The validity time is
            # taken to be the time for the first sample, the data time
            # for the last sample, with the others evenly between.
            size   = header[lbrow]
            delta  = (dtime - vtime)/(size - 1)
            origin = vtime
            array = numpy.linspace(origin, origin + delta*(size-1), num=size)

            cache_key = ('time', origin, size, delta)

            coord = _create_Coordinate(domain, tdim, axis_code, p=p, 
                                       array=array,
                                       dimensions=[tdim],
                                       cache_key=cache_key)
        else:
            coord = _create_Coordinate(domain, tdim, axis_code, p=p,
                                       coord_type=coord_type, 
                                       dimensions=[tdim],
                                       cache_key=cache_key)
       
        # Save the dimension name
        if coord_type == 'x':
            xdim = tdim
            x_dim_coord = coord
        elif coord_type == 'y' or p.timeseries:
            ydim = tdim
            y_dim_coord = coord

        # Set the T axis name for cell methods
        axis_name['t'] = coord.standard_name
        axis_dim['t']  = tdim

        # ------------------------------------------------------------
        # Create a 'VERTICAL' dimension coordinate. This size 1
        # coordinate will often by a vertical coordinate such as
        # pressure, but could be anything, such as longitude.
        # ------------------------------------------------------------
        axis_code = p.iv
        if axis_code is not None: 
            dim  = 'dim%(dimN)d' % locals()
            dimN += 1         # Increment dimension number
            vdim = dim

            if 'height' in p.cf_info:
                # Create the height coordinate from the information
                # given in the STASH to standard_name conversion table
                axis_code = 15
                height, units = p.cf_info['height']

                cache_key = ('height', height, units)

                if units in _cached_units:
                    height_units = _cached_units[units]
                else:
                    height_units = Units(units)
                    _cached_units[units] = height_units

                coord = _create_Coordinate(domain, vdim, axis_code=axis_code, 
                                           p=p,
                                           units=height_units,
                                           array=numpy_array([height],
                                                             dtype=float),
                                           dimensions=[vdim],
                                           cache_key=('height', height, units))
            else:
                # Create the height coordinate from the PP header
                array = None

                # Create the height coordinate from the PP header
                if LBVC == 9:
                    # atmosphere_hybrid_sigma_pressure_coordinate
                    BLEV   = header[blev]  
                    BHLEV  = header[bhlev] 
                    BRLEV  = header[brlev]  
                    BHRLEV = header[bhrlev] 
                    BRSVD1 = header[brsvd1] 
                    BRSVD2 = header[brsvd2]

                    array  = numpy_array([BLEV + BHLEV/_pstar], dtype='float32')
                    bounds = numpy_array([[BRLEV  + BHRLEV/_pstar,
                                           BRSVD1 + BRSVD2/_pstar]], dtype='float32')

                    cache_key = ('atmosphere_hybrid_sigma_pressure_coordinate',
                                 BLEV, BHLEV, BRLEV, BHRLEV, BRSVD1, BRSVD2)

                elif LBVC == 65:
                    # atmosphere_hybrid_height_coordinate: Can't
                    # calculate eta (because we don't know the height
                    # of the top level), so we'll create dimension
                    # coordinate for model_level_number instead
                    if LBLEV >= 0:
                        xxx = LBLEV
                        if xxx == 9999:
                            # Assume that 9999 means a 'surface' level '0'
                            xxx = 0

                        array     = numpy_array([xxx], dtype='int32')
                        bounds    = None
                        axis_code = 5
                        cache_key = ('model_level_number', xxx)

                else:  
                    BLEV   = header[blev]   
                    BRLEV  = header[brlev] 
                    BRSVD1 = header[brsvd1] 

                    array  = numpy_array([BLEV], dtype='float32')
                    bounds = numpy_array([[BRLEV, BRSVD1]], dtype='float32')
                    if equals(bounds[0,0], bounds[0,1]):
                        bounds = None

                    cache_key = (_coord_standard_name[axis_code],
                                 BLEV, BRLEV, BRSVD1)
                #--- End: if

                if array is not None:
                    # We have found some data, so create a dimension
                    # coordinate
                    coord = _create_Coordinate(domain, vdim, axis_code=axis_code,
                                               p=p,
                                               array=array, bounds_array=bounds,
                                               dimensions=[vdim], cache_key=cache_key)
                #--- End: if
            #--- End: if

            # Set the V axis name for cell methods
            axis_name['v'] = coord.standard_name
            axis_dim['v']  = vdim
        #--- End: if

        # ------------------------------------------------------------
        # Create a PSEUDOLEVEL dimension coordinate
        # ------------------------------------------------------------
        if LBUSER5 > 0: 
            dim  = 'dim%(dimN)d' % locals()
            dimN += 1         # Increment dimension number
            
            coord = _create_Coordinate(
                domain, dim, axis_code=40, p=p, 
                array=numpy_array([LBUSER5], dtype='int32'),
                dimensions=[dim],
                cache_key=('pseudolevel', LBUSER5))
        
            # Set the pseudolevel axis name for cell methods
            axis_name['p'] = coord.standard_name  ## dch: should this be something else?
            axis_dim['p']  = dim
        #--- End: if

        # ------------------------------------------------------------
        # Create a RADIATION WAVELENGTH dimension coordinate
        # ------------------------------------------------------------
            #dch : do this instead of VERTICAL, I wonder
        try:
            rwl, units = p.cf_info['below']
        except (KeyError, TypeError):
            pass
        else:           
            dim   = 'dim%(dimN)d' % locals()
            dimN += 1         # Increment dimension number
            rwldim = dim
            
            if units in _cached_units:
                rwl_units = _cached_units[units]
            else:
                rwl_units = Units(units)
                _cached_units[units] = rwl_units

            coord = _create_Coordinate(
                domain, rwldim, axis_code=None, p=p,
                pubattr={'standard_name' : 'radiation_wavelength'},
                units=rwl_units,
                array=numpy_array([rwl], dtype=float),
                bounds_array=numpy_array([[0.0, rwl]]),
                dimensions=[rwldim],
                cache_key=('radiation_wavelength', rwl, units))
            
            # Set the radiation wavelength axis name for cell methods
            axis_name['rwl'] = 'radiation_wavelength'
        #--- End: try

        # ------------------------------------------------------------
        # Create the Y dimension coordinate, if it hasn't already been
        # created. This coordinate represents the 'y' dimension of the
        # data array. In the case of cross sections, it may have
        # already been created.
        # ------------------------------------------------------------
        # Set coordinate type and axis code
        coord_type = 'y'
        axis_code  = p.iy

        # Skip this coordinate if it has already been created
        if axis_code is not None:
            dim   = 'dim%(dimN)d' % locals()           
            dimN += 1         # Increment dimension number       

            cache_key = (_coord_standard_name[axis_code],
                         header[lbcode],
                         header[bzy],
                         header[bdy],
                         header[lbrow])

            y_dim_coord = _create_Coordinate(domain, dim, axis_code,
                                             p=p,
                                             coord_type=coord_type,
                                             dimensions=[dim],
                                             cache_key=cache_key)
        
            ydim = dim
 
            # Set the Y axis name for cell methods
            axis_name[coord_type] = y_dim_coord.standard_name
            axis_dim[coord_type]  = dim
        #--- End: if

        # ------------------------------------------------------------
        # Create the X dimension coordinate, if it hasn't already been
        # created. This coordinate represents the 'x' dimension of the
        # data array. In the case of cross sections, it may have
        # already been created.
        # ------------------------------------------------------------
        # Set coordinate type and axis code
        coord_type = 'x'
        axis_code  = p.ix

        # Skip this coordinate if it has already been created
        if axis_code is not None:
            dim   = 'dim%(dimN)d' % locals()           
            dimN += 1         # Increment dimension number       

            cache_key = (_coord_standard_name[axis_code],
                         header[lbcode],
                         header[bzx],
                         header[bdx],
                         header[lbnpt])

            x_dim_coord = _create_Coordinate(domain, dim, axis_code, p=p,
                                             coord_type=coord_type,
                                             dimensions=[dim],
                                             cache_key=cache_key)
        
            xdim = dim
 
            # Set the Y axis name for cell methods
            axis_name[coord_type] = x_dim_coord.standard_name
            axis_dim[coord_type]  = dim
        #--- End: if

        ## ------------------------------------------------------------
        ## Create X and Y dimension coordinates, if they haven't
        ## already been created. These coordinates represent the 'x'
        ## and 'y' dimensions of the data array. In the case of cross
        ## sections, one of them may have already been created.
        ## ------------------------------------------------------------
        ## Set coordinate type and axis code
        #for coord_type, axis_code in zip(('y' , 'x' ),
        #                                 (p.iy, p.ix)):
        #
        #    # Skip this coordinate if it has already been created
        #    if axis_code is None:
        #        continue    
        #
        #    # Still here? Then create a coordinate
        #    dim   = 'dim%(dimN)d' % locals()           
        #    dimN += 1         # Increment dimension number       
        #
        #    delta  = bhd[bdx]
        #    origin = bhd[bzx]
        #    size   = lhd[lbnpt]
        #
        #    cache_key = None #(axis_code, bhd[bzx], bhd[bdx], lhd[lbnpt])
        #
        #    coord = _create_Coordinate(domain, dim, axis_code, p=p,
        #                               coord_type=coord_type,
        #                               dimensions=[dim], cache_key=cache_key)
        #
        #    if coord_type == 'y':
        #        ydim = dim
        #    else:
        #        xdim = dim
        #
        #    # Set the X or Y axis name for cell methods
        #    axis_name[coord_type] = coord.standard_name
        #    axis_dim[coord_type]  = dim
        ##--- End: for

        # ============================================================
        # Create 1-d, size 1 auxiliary coordinates
        # ============================================================
        axis_code = None
        if LBVC == 9:
            # ------------------------------------------------------------
            # Atmosphere hybrid sigma pressure coordinate components
            # (see Appendix D of the CF conventions)
            # ------------------------------------------------------------
            for long_name, value, units, bounds in zip(
                ('atmosphere_hybrid_sigma_pressure_coordinate_ak',      
                 'atmosphere_hybrid_sigma_pressure_coordinate_bk'),
                (BHLEV, BLEV),                     # value                 
                (_cached_units['Pa'], _cached_units['1']),    # units
                ([BHRLEV, BRSVD2], [BRLEV , BRSVD1])  # BOUNDS                 
                ):
                aux   = 'aux%(auxN)d' % locals()           
                auxN += 1         # Increment auxiliary number

                cache_key = ('aux', long_name, value, tuple(bounds))

                coord = _create_Coordinate(
                    domain, aux, axis_code=None,
                    p=p,
                    pubattr={'standard_name': long_name},
                    units=units,
                    array=numpy_array([value], dtype='float32'),
                    bounds_array=numpy_array([bounds], dtype='float32'),
                    dimensions=[vdim],
                    aux=True,
                    cache_key=cache_key)
            #--- End: for

        elif LBVC == 65:
            # --------------------------------------------------------
            # Atmosphere hybrid height coordinate components (see
            # Appendix D of the CF conventions)
            # -------------------------------------------------------- 
            # --------------------------------------------------------
            # atmosphere_hybrid_height_coordinate_ak
            # --------------------------------------------------------
            long_name ='atmosphere_hybrid_height_coordinate_ak'
            value = header[blev]
            bounds = (header[brlev], header[brsvd1])
            
            aux   = 'aux%(auxN)d' % locals()           
            auxN += 1         # Increment auxiliary number
            
            coord = _create_Coordinate(
                domain, aux, axis_code=None,
                p=p,
                pubattr      = {'standard_name': long_name},
                units        = _cached_units['m'],
                array        = numpy_array([value], dtype='float32'),
                bounds_array = numpy_array([bounds], dtype='float32'),
                dimensions   = [vdim],
                aux=True,
                cache_key=('aux', long_name, value, bounds))

            #--------------------------------------------------------
            # atmosphere_hybrid_height_coordinate_bk
            #--------------------------------------------------------
            long_name ='atmosphere_hybrid_height_coordinate_bk'
            value = header[bhlev]
            bounds = (header[bhrlev], header[brsvd2])

            aux   = 'aux%(auxN)d' % locals()           
            auxN += 1         # Increment auxiliary number
            
            coord = _create_Coordinate(
                domain, aux, axis_code=None,
                p=p,
                pubattr={'standard_name': long_name},
                units=_cached_units['1'],
                array=numpy_array([value], dtype='float32'),
                bounds_array=numpy_array([bounds], dtype='float32'),
                dimensions=[vdim],
                aux=True,
                cache_key=('aux', long_name, value, bounds))

            #for long_name, value, units, bounds in zip(
            #    ('atmosphere_hybrid_height_coordinate_ak',      
            #     'atmosphere_hybrid_height_coordinate_bk'),
            #    (bhd[blev],                      # value
            #     bhd[bhlev]),
            #    ('m',                              # units
            #     '1'),
            #    ([bhd[brlev] , bhd[brsvd1]],   # bounds
            #     [bhd[bhrlev], bhd[brsvd2]])
            #     
            #    ):
            #    aux   = 'aux%(auxN)d' % locals()           
            #    auxN += 1         # Increment auxiliary number
            #    
            #    pubattr = {'standard_name': long_name}
            #
            #    cache_key = (long_name, value, tuple(bounds))
            #
            #    coord = _create_Coordinate(
            #        domain, aux, axis_code=axis_code,
            #        p=p,
            #        pubattr      = pubattr, 
            #        units        = Units(units),
            #        array        = numpy_array([value]),
            #        bounds_array = numpy_array([bounds]),
            #        dimensions   = [vdim], cache_key=cache_key)
            ##--- End: for
  
        #--- End: if

        # ------------------------------------------------------------
        # forecast_reference_time auxiliary coordinate
        # ------------------------------------------------------------
        if p.lbtim_ib == 1: 
            aux   = 'aux%(auxN)d' % locals()           
            auxN += 1         # Increment auxiliary number
       
            coord = _create_Coordinate(
                domain, aux, axis_code=None, p=p,
                pubattr    = {'standard_name': 'forecast_reference_time'},
                units      = reftime,
                array      = numpy_array([dtime], dtype=float),
                dimensions=[tdim],
                aux=True,
                cache_key=('aux', 'forecast_reference_time', dtime, reftime))
        #--- End: if

        # -------------------------------------------------------
        # model_level_number auxiliary coordinate
        # -------------------------------------------------------
        if (p.iv is not None and 
            LBVC in (2, 9) and 
            LBLEV not in (7777, 8888)): # dch check 7777
            aux   = 'aux%(auxN)d' % locals()           
            auxN += 1         # Increment auxiliary number
            
            xxx = LBLEV
            if xxx == 9999:
                # Assume that 9999 means a 'surface' level '0'
                xxx = 0

            coord = _create_Coordinate(
                domain, aux, axis_code=5, p=p, 
                pubattr    = {'axis': None}, 
                array      = numpy_array([xxx], dtype='int32'), 
                dimensions = [vdim],
                aux=True,
                cache_key=('aux', 'model_level_number', xxx))
        #--- End: if

        # ------------------------------------------------------------
        # Domain title auxiliary coordinate
        # ------------------------------------------------------------
        if 'domain_title' in p.extra:
            domain_titles = p.extra['domain_title']

            if p.ix == 13:
                dim = xdim
            elif p.iy == 13:
                dim = ydim
            else:
                dim = None
    
            if dim:
                aux   = 'aux%(auxN)d' % locals()           
                auxN += 1                        # Increment auxiliary number

                coord = _create_Coordinate(
                    domain, aux, axis_code=None, p=p, 
                    array      = numpy_array(domain_titles), # dch array, or not?
                    pubattr    = {'long_name': 'domain title'},
                    aux=True,
                    dimensions = [dim])
        #--- End: if

        # ============================================================
        # Create N-d (N>1) auxiliary coordinates
        # ============================================================
        
        # ------------------------------------------------------------
        # 2-d unrotated latitude and longitude auxiliary coordinates
        # ------------------------------------------------------------
#        if 'degrees' == domain[ydim].units == domain[xdim].units:
        if y_dim_coord.getprop('standard_name', None) == 'grid_latitude':

            if x_dim_coord.getprop('standard_name', None) == 'grid_longitude':
                dim_lat, dim_lon = ydim, xdim
                rotated_lon = x_dim_coord
                rotated_lat = y_dim_coord
            else:
                dim_lat, dim_lon = xdim, ydim
                rotated_lon = y_dim_coord
                rotated_lat = x_dim_coord

            # Try to find the appropriate unrotated latitude and
            # longitude arrays in the cache, to avoid having to create
            # them.
            found_cached_latlon = False            
            for rot_lat, rot_lon in _cache['latlon']:
                if (rot_lon.Data.equals(rotated_lon.Data) and 
                    rot_lat.Data.equals(rotated_lat.Data)):
                    
                    found_cached_latlon = True

                    lat, lon = _cache['latlon'][(rot_lat, rot_lon)] 

#                    lat = lat.copy()
#                    lon = lon.copy()

                    break
            #--- End: for

            BPLAT = header[bplat]
            BPLON = header[bplon]

            # Create the unrotated latitude and longitude arrays if we
            # couldn't find them in the cache
            if not found_cached_latlon:
#                print  'CALC'

                lat, lon = unrotated_latlon(rotated_lat.varray, 
                                            rotated_lon.varray,
                                            BPLAT, BPLON) 

                # Add the newly created unrotated latitude and
                # longitude auxiliary coordinates to the cache
                _cache['latlon'][(rotated_lat, rotated_lon)] = (lat, lon)
            #--- End: if
             
            # Create the coordinate reference and insert it into the
            # projection coordinates
            coordref = CoordinateReference(
                name='rotated_latitude_longitude',
                grid_north_pole_latitude=BPLAT,
                grid_north_pole_longitude=BPLON)

            domain.insert_ref(coordref, copy=False)

            # Create the unrotated latitude and longitude coordinates        
            for (i, axis_code, standard_name, array,
                 units) in zip((  0          ,  1          ),
                               ( 10          , 11          ), # axis code
                               ('latitude'   , 'longitude' ), # standard name
                               ( lat         , lon         ), # numpy array
                               (_cached_units['degrees_north'],
                                _cached_units['degrees_east']), # units
                               ):
                aux   = 'aux%(auxN)d' % locals()           
                auxN += 1                        # Increment auxiliary number

                pubattr = {'standard_name': standard_name,
                           'axis'         : None}

                coord = _create_Coordinate(domain, aux, axis_code, p=p,
                                           pubattr    = pubattr,
                                           units      = units,
                                           array      = array,
                                           aux=True,
                                           dimensions=[dim_lat, dim_lon]) 
             #--- End: for

        #--- End: if

        # ------------------------------------------------------------
        # Create auxiliary coordinates for the latitudes and
        # longitudes of the sites in site-time cross sections. (Don't
        # consider 'z' extra data because we don't know what it refers
        # to.)
        # ------------------------------------------------------------
        if p.site_time_cross_section:
            for axis_code, extra_type in zip((11 , 10 ),
                                             ('x', 'y')):
                coord_type = extra_type + '_domain_bounds'

                if coord_type in p.extra:
                    p.extra[coord_type]
                    # Create, from extra data, an auxiliary coordinate                        # should   
                    # with 1) data and bounds, if the upper and lower                         # be       
                    # bounds have no missing values; or 2) data but no                        # the      
                    # bounds, if the upper bound has missing values                           # axis     
                    # but the lower bound does not.                                           # which    
                    file_position = ppfile.tell()                                             # has      
                    bounds = p.extra[coord_type][...]                                         # axis_code
                    # Reset the file pointer after reading the extra                          # 13       
                    # data into a numpy array
                    ppfile.seek(file_position, os.SEEK_SET)
                    data = None
                    if numpy.any(bounds[..., 1] == _pp_rmdi): # dch also test in bmdi?
                        if not numpy.any(bounds[...,0] == _pp_rmdi): # dch also test in bmdi?
                            data = bounds[...,0]
                        bounds = None
                    else:
                        data = numpy.mean(bounds, axis=1)

                    if (data, bounds) != (None, None):
                        aux   = 'aux%(auxN)d' % locals()           
                        auxN += 1                        # Increment auxiliary number
                        
                        coord = _create_Coordinate(domain, aux, axis_code, p=p,
                                                   array        = data,
                                                   aux=True,
                                                   bounds_array = bounds, 
                                                   pubattr      = {'axis': None},
                                                   dimensions   = [xdim]) # DCH      
                                                                        # xdim?    
                                                                        # should   
                                                                        # be       
                                                                        # the      
                                                                        # axis     
                                                                        # which    
                                                                        # has      
                                                                        # axis_code
                                                                        # 13       
                    #--- End: if
                else:
                    coord_type = '%s_domain_lower_bound' % extra_type
                    if coord_type in p.extra:
                        # Create, from extra data, an auxiliary
                        # coordinate with data but no bounds, if the
                        # data noes not contain any missing values
                        file_position = ppfile.tell()
                        data = p.extra[coord_type][...]
                        # Reset the file pointer after reading the
                        # extra data into a numpy array
                        ppfile.seek(file_position, os.SEEK_SET)
                        if not numpy.any(data == _pp_rmdi): # dch also test in bmdi?   
                            aux   = 'aux%(auxN)d' % locals()           
                            auxN += 1                        # Increment auxiliary number
                            coord = _create_Coordinate(domain, aux, axis_code, p=p,
                                                       aux=True,
                                                       array=numpy_array(data),
                                                       pubattr={'axis': None}, 
                                                       dimensions=[xdim])# DCH xdim?    
               #--- End: if
           #--- End: for
        #--- End: if
        
        # ------------------------------------------------------------
        # Set the field's data dimension names and the netCDF
        # dimension names for each of the domain's dimensions
        # ------------------------------------------------------------
        domain.nc_dimensions = {}
        for k, ncdim in axis_name.iteritems():
            domain.nc_dimensions[axis_dim[k]] = ncdim

        # ------------------------------------------------------------
        # Set the field's data
        # ------------------------------------------------------------
        if p.data is not None:
            domain._axes['data'] = [ydim, xdim]

            data = Data(p.data,
                        units=properties.pop('units', None),
                        fill_value=properties.get('_FillValue', None))
        #--- End: if

        # ============================================================
        # Create the field's cell methods
        # ============================================================
        cell_methods = []

        proc       = header[lbproc]
        tmean_proc = 0
        if p.lbtim_ib in (2, 3):
            if proc - 128 in (0, 64, 2048, 4096, 8192):
                tmean_proc = 128
                proc -= 128
                
        # ------------------------------------------------------------
        # Area cell methods
        # ------------------------------------------------------------
        if p.ix in (10, 11, 12) and p.iy in (10, 11, 12):
            if 'where' in p.cf_info:
                cell_methods.append('area: mean')
                axis_dim['area']  = None
                axis_name['area'] = 'area'

                cell_methods.append(p.cf_info['where'])
                if 'over' in p.cf_info:
                    cell_methods.append(p.cf_info['over'])
            #--- End: if

            if proc == 64:
                cell_methods.append('x: mean')

#            if proc == 64 or 'where' in p.cf_info:
#                cell_methods.append('area: mean')
#                axis_dim['area']  = None
#                axis_name['area'] = 'area'
#
#            try:
#                cell_methods.append(p.cf_info['where'])
#            except (KeyError, TypeError):
#                pass
#            else:
#                try:
#                    cell_methods.append(p.cf_info['over'])
#                except (KeyError, TypeError):
#                    pass

#            for info in p.cf_info:                
#                if info.startswith('area: mean where_'):                    
#                    cell_methods.append(info.replace('where_', 'where ', 1))
#                elif info.startswith('over_'):
#                    cell_methods.append(info.replace('over_', 'over ', 1))
        # dch : do special zonal mean as as in pp_cfwrite
        
        # ------------------------------------------------------------
        # Vertical cell methods
        # ------------------------------------------------------------
        if proc == 2048:
            cell_methods.append('v: mean')

        # ------------------------------------------------------------
        # Time cell methods
        # ------------------------------------------------------------
        if p.lbtim_ib in (0, 1):
            cell_methods.append('t: point')
        elif proc == 4096:
            cell_methods.append('t: minimum')
        elif proc == 8192:
            cell_methods.append('t: maximum')
        if tmean_proc == 128:
            if p.lbtim_ib == 2:
                cell_methods.append('t: mean')
            elif p.lbtim_ib == 3:
                cell_methods.append('t: mean within years')
                cell_methods.append('t: mean over years')
        #--- End: if

        # ------------------------------------------------------------
        # Add the cell methods to the field
        # ------------------------------------------------------------
        if cell_methods:
            cell_methods = CellMethods(' '.join(cell_methods))
            properties['cell_methods'] = _parse_cell_methods(cell_methods, 
                                                             axis_name, axis_dim)
        #-- End: if

        properties['lbproc'] = proc

        # ============================================================
        # The field is complete(!). So create it and add it to the
        # list of fields to be returned.
        # ============================================================
        f = Field(properties=properties, domain=domain, data=data,
                  attributes=attributes, copy=False)

        fields_in_file.append(f)

        # Reset the FREE_MEMORY constant
#        SET_FREE_MEMORY(None)
        
        # ============================================================
        # Now read the next PP field in the file back at the top of
        # this while loop
        # ============================================================
    #--- End: while

    # Close the PP file
    ppfile.close()

    # Return the fields
    return fields_in_file
#--- End: def

def _parse_cell_methods(cell_methods, axis_name, axis_dim):
    '''

:Parameters:

    cell_methods : cf.CellMethods

    axis_name : dict

    axis_dim : dict

:Returns:

    cell_methods : cf.CellMethods

**Examples**

'''
    for cell_method in cell_methods:
        cell_method.names = [axis_name[name] for name in cell_method.names[0]]
        cell_method.axes  = [axis_dim[name]  for dim  in cell_method.axes[0]]
    #--- End: for

    return cell_methods
#--- End: def
