import datetime
import tempfile
import os
import sys
import numpy
import unittest
import atexit

import cf

'''
Tests for the cf package.

'''

tmpfile  = tempfile.mktemp('.nc')
tmpfile2 = tempfile.mktemp('.nca')
tmpfiles = [tmpfile, tmpfile2]
def _remove_tmpfiles():
    '''
'''
    for f in tmpfiles:
        try:
            os.remove(f)
        except OSError:
            pass
#--- End: def
atexit.register(_remove_tmpfiles)


class generalTest(unittest.TestCase):   
    def setUp(self):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'test_file.nc')
        self.f = cf.read(filename)[0]

    def test_GENERAL(self):
        # Save original chunksize
        original_chunksize = cf.CHUNKSIZE()
        
        cf.CHUNKSIZE(60)

        g = self.f.squeeze()
        f = self.f.copy()

        c = cf.set([0,3,4,5])

        a = (f == c)
        
        # +, -, *, /, **
        h = g.copy()
        h **= 2
        h **= 0.5
        h.standard_name = g.standard_name
        self.assertTrue(cf.equals(g, h, traceback=True), repr(g.array - h.array))
        h *= 10
        h /= 10.
        self.assertTrue(cf.equals(g, h, traceback=True), repr(g.array - h.array))
        h += 1
        h -= 1
        self.assertTrue(cf.equals(g, h, traceback=True), repr(g.array - h.array))
        h = h ** 2.
        h = h ** 0.5
        h.standard_name = g.standard_name
        self.assertTrue(cf.equals(g, h, traceback=True), repr(g.array - h.array))
        h = h * 10
        h = h / 10.
        self.assertTrue(cf.equals(g, h, traceback=True), repr(g.array - h.array))
        h = h + 1
        h = h - 1
        self.assertTrue(cf.equals(g, h, traceback=True), repr(g.array - h.array))

#        # Operators on a field list
#        h = g.copy()
#        h.override_units('m')
#        gl = cf.FieldList([h.copy(), h.copy()])
#        gl += 2
#
#        x = 2 #.0
#        y = gl   + x
#        y = gl   * x
#        y = gl   - x
#        y = gl   / x
#        y = gl  // x
#        y = gl  ** int(x)
#        
#        y = x  + gl
#        y = x  * gl
#        y = x - gl
#        y = x  / gl
#        y = x // gl
#        #y = x ** gl
#        
#        y = gl.copy()
#        y += x
#        y = gl.copy()
#        y *= x
#        y = gl.copy()
#        y -= x
#        y = gl.copy()
#        y /= x
#        y = gl.copy()
#        y //= x
#        y = gl.copy()
#        y **= int(x)
#        
#        y = gl.__truediv__(x)
#        y = gl.__rtruediv__(x)
#        y = gl.copy()
#        y.__itruediv__(x)
#        
#        y = gl   > x
#        y = gl  >= x
#        y = gl   < x
#        y = gl  <= x
#        y = gl  == x
#        y = gl  != int(x)
#        
#        y = abs(gl)
#        y = -gl
#        y = +gl
#        #y = ~gl
#                
#        for _f in gl:
#            _f.dtype = int
#        
#        y =  gl  & x
#        y =  gl  | x               
#        y =  gl  ^ x               
#        y =  gl << x               
#        y =  gl >> x               
#                                   
#        y =  x   & gl              
#        y =  x   | gl              
#        y =  x  ^ gl               
#        y =  x << gl               
#        y =  x >> gl               
#                                        
#        y = gl.copy()                   
#        y       &= x                    
#        y = gl.copy()
#        y       |= x
#        y = gl.copy()
#        y       ^= x

        # flip, expand_dims, squeeze and remove_axes
        h = g.copy()
        h.flip((1, 0), i=True)
        h.flip((1, 0), i=True)
        h.flip(0, i=True)
        h.flip(1, i=True)
        h.flip([0, 1], i=True)
        self.assertTrue(cf.equals(g, h, traceback=True))

        # Access the field's data as a numpy array
        a = g.array
        a = g.item('lat').array
        a = g.item('lon').array
        
        # Subspace the field
        g[..., 2:5].array
        g[9::-4, ...].array
        h = g[(slice(None, None, -1),) * g.ndim]
        h = h[(slice(None, None, -1),) * h.ndim]
        self.assertTrue(g.equals(h, traceback=True))
        
        # Indices for a subspace defined by coordinates
        f.indices()
        f.indices(grid_lat=cf.lt(5), grid_lon=27)
        f.indices('exact', 
                  grid_latitude=cf.lt(5), grid_longitude=27,
                  atmosphere_hybrid_height_coordinate=1.5)
        
        # Subspace the field
        g.subspace(grid_latitude=cf.lt(5), grid_longitude=27, atmosphere_hybrid_height_coordinate=1.5)
        
        # Create list of fields
        fl = cf.FieldList([g, g, g, g])
        
        # Write a list of fields to disk
        cf.write((f, fl), tmpfile)
        cf.write(fl, tmpfile)

        # Read a list of fields from disk
        fl = cf.read(tmpfile, squeeze=True)
        try:
            fl.delattr('history')
        except AttributeError:
            pass
        
        # Access the last field in the list
        x = fl[-1]
        
        # Access the data of the last field in the list
        x = fl[-1].array
        
        # Modify the last field in the list
        fl[-1] *= -1
        x = fl[-1].array

        # Changing units
        fl[-1].units = 'mm.s-1'
        x = fl[-1].array
        
        # Combine fields not in place
        g = fl[-1] - fl[-1]
        x = g.array
        
        # Combine field with a size 1 Data object
        g += cf.Data([[[[[1.5]]]]], 'cm.s-1')
        x = g.array

        # Setting of (un)masked elements with where()
        g[::2, 1::2] = numpy.ma.masked
        g.Data.to_memory(1)
        g.where(True, 99)
        g.Data.to_memory(1)
        g.where(g.mask, 2)
        g.Data.to_memory(1)
        
        g[slice(None, None, 2), slice(1, None, 2)] = cf.masked
        g.Data.to_memory(1)
        g.where(g.mask, [[-1]])
        g.Data.to_memory(1)
        g.where(True, cf.Data(0, None))
        g.Data.to_memory(1)

        h = g[:3, :4]
        h.where(True, -1)
        h[0, 2] = 2
        h.transpose([1, 0], i=True)
        
        h.flip([1, 0], i=True)
        
        g[slice(None, 3), slice(None, 4)] = h
        
        h = g[:3, :4]
        h[...] = -1
        h[0, 2] = 2
        g[slice(None, 3), slice(None, 4)] = h

        # Make sure all partitions' data are in temporary files
        g.Data.to_disk()

        # Push partitions' data from temporary files into memory
        g.Data.to_memory(regardless=True)
        g.Data.to_disk()


        # Iterate through array values
        for x in f.Data.flat():
            pass

        # Reset chunk size
        cf.CHUNKSIZE(original_chunksize)

        # Move Data partitions to disk
        f.Data.to_disk()
        
        cf.CHUNKSIZE(original_chunksize)
        
        f.transpose(i=True)
        f.flip(i=True)
        
        cf.write(f, 'delme.nc')
        f = cf.read('delme.nc')[0]
        cf.write(f, 'delme.nca', fmt='CFA4')
        g = cf.read('delme.nca')[0]
        
        f.aux('aux0').id = 'atmosphere_hybrid_height_coordinate_ak'
        f.aux('aux1').id = 'atmosphere_hybrid_height_coordinate_bk'


        b = f[:,0:6,:]
        c = f[:,6:,:]
        d = cf.aggregate([b, c], info=1)[0]
        
        # Remove temporary files
        cf.data.partition._remove_temporary_files()

        cf.CHUNKSIZE(original_chunksize)

    #--- End: def

#--- End: class
if __name__ == "__main__":
    print 'Run date:', datetime.datetime.utcnow()
    cf.environment()
    print
    unittest.main(verbosity=2)

#     items spanning ['grid_latitude', 'grid_longitude'] axes
'''     
{'dim0': <CF DimensionCoordinate: atmosphere_hybrid_height_coordinate(1) >,
 'dim1': <CF DimensionCoordinate: grid_latitude(10) degrees>,
 'dim2': <CF DimensionCoordinate: grid_longitude(9) degrees>,
 'aux0': <CF AuxiliaryCoordinate: latitude(10, 9) degree_N>,
 'aux1': <CF AuxiliaryCoordinate: longitude(9, 10) degreesE>,
 'ref0': <CF CoordinateReference: atmosphere_hybrid_height_coordinate>,
 'cct0': <CF DomainAncillary: ncvar%atmosphere_hybrid_height_coordinate_ak(1) m>,
 'cct1': <CF DomainAncillary: ncvar%atmosphere_hybrid_height_coordinate_bk(1) >,
 'cct2': <CF DomainAncillary: surface_altitude(10, 9) m>,
 'ref1': <CF CoordinateReference: rotated_latitude_longitude>,
 'fav0': <CF FieldAncillary: ancillary1(10, 9) m.s-1>,
 'fav1': <CF FieldAncillary: ancillary0(9, 10) m.s-1>,
 'fav2': <CF FieldAncillary: ancillary3(10) m.s-1>,
 'fav3': <CF FieldAncillary: ancillary2(9) m.s-1>,
 'msr0': <CF CellMeasure: area(9, 10) km 2>}

{'dim0': <CF DimensionCoordinate: atmosphere_hybrid_height_coordinate(1) >,
 'dim1': <CF DimensionCoordinate: grid_latitude(10) degrees>,
 'dim2': <CF DimensionCoordinate: grid_longitude(9) degrees>,
 'aux0': <CF AuxiliaryCoordinate: latitude(10, 9) degree_N>, 
 'aux1': <CF AuxiliaryCoordinate: longitude(10, 9) degreesE>,
 'ref0': <CF CoordinateReference: atmosphere_hybrid_height_coordinate>,
 'cct0': <CF DomainAncillary: ncvar%atmosphere_hybrid_height_coordinate_ak(1) m>,
 'cct1': <CF DomainAncillary: ncvar%atmosphere_hybrid_height_coordinate_bk(1) >,
 'cct2': <CF DomainAncillary: surface_altitude(10, 9) m>,
 'ref1': <CF CoordinateReference: rotated_latitude_longitude>,
 'fav0': <CF FieldAncillary: ancillary1(10, 9) m.s-1>,
 'fav1': <CF FieldAncillary: ancillary0(10, 9) m.s-1>,
 'fav2': <CF FieldAncillary: ancillary3(10) m.s-1>,
 'fav3': <CF FieldAncillary: ancillary2(9) m.s-1>,
 'msr0': <CF CellMeasure: area(10, 9) km 2>}
'''
