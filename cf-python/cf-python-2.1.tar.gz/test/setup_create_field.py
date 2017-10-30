import datetime
import os
import sys
import unittest

import numpy

import cf

class create_fieldTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]

    def test_create_field(self):
        # Dimension coordinates
        dim1 = cf.Coordinate(data=cf.Data(numpy.arange(10.), 'degrees'))
        dim1.standard_name = 'grid_latitude'
         
        dim0 = cf.DimensionCoordinate(data=cf.Data(numpy.arange(9.) + 20, 'degrees'))
        dim0.standard_name = 'grid_longitude'
        dim0.Data[-1] += 5
        bounds = cf.Data(numpy.array([dim0.Data.array-0.5, dim0.Data.array+0.5]).transpose((1,0)))
        bounds[-2,1] = 30
        bounds[-1,:] = [30, 36]
        dim0.insert_bounds(cf.Bounds(data=bounds))
        
        dim2 = cf.Coordinate(data=cf.Data([1.5]), bounds=cf.Data([[1, 2.]]))
        dim2.standard_name = 'atmosphere_hybrid_height_coordinate'
        
        # Auxiliary coordinates
        ak = cf.AuxiliaryCoordinate(data=cf.Data([10.], 'm'))
        ak.id = 'atmosphere_hybrid_height_coordinate_ak'
        ak.insert_bounds(cf.Data([[5, 15.]]), ak.Units)
        
        bk = cf.AuxiliaryCoordinate(data=cf.Data([20.]))
        bk.id = 'atmosphere_hybrid_height_coordinate_bk'
        bk.insert_bounds(cf.Data([[14, 26.]]))
        
        aux2 = cf.AuxiliaryCoordinate(
            data=cf.Data(numpy.arange(-45, 45, dtype='int32').reshape(10, 9),
                         units='degree_N'))
        aux2.standard_name = 'latitude'
        
        aux3 = cf.Coordinate(
            data=cf.Data(numpy.arange(60, 150, dtype='int32').reshape(9, 10),
                         units='degreesE'))
        aux3.standard_name = 'longitude'
        
        aux4 = cf.AuxiliaryCoordinate(
            data=cf.Data(['alpha','beta','gamma','delta','epsilon',
                          'zeta','eta','theta','iota','kappa']))
        aux4.standard_name = 'greek_letters'
        aux4[0] = cf.masked
    
    
        # Cell measures
        msr0 = cf.CellMeasure(
            data=cf.Data(1+numpy.arange(90.).reshape(9, 10)*1234, 'km 2'))
        msr0.measure = 'area'
        
        # Coordinate references
        ref0 = cf.CoordinateReference(
            name='rotated_latitude_longitude',
            parameters={'grid_north_pole_latitude': 38.0,
                        'grid_north_pole_longitude': 190.0})
        
        # Data          
        data = cf.Data(numpy.arange(90.).reshape(10, 9), 'm s-1')

        properties = {'standard_name': 'eastward_wind'}
        
        f = cf.Field(properties=properties, data=data)

        x = f.insert_dim(dim0)
        y = f.insert_dim(dim1)
        z = f.insert_dim(dim2)

        f.insert_aux(aux2)
        f.insert_aux(aux3)
        f.insert_aux(aux4, axes=['Y'])

        ak = f.insert_domain_anc(ak, axes=[z])
        bk = f.insert_domain_anc(bk, axes=[z])

        f.insert_measure(msr0)

        f.insert_ref(ref0)


        orog = f.copy()
        orog.standard_name = 'surface_altitude'
        
        orog.insert_data(cf.Data(f.array*2, 'm'))
        orog.remove_axes(size=1)
        orog.transpose([1, 0])

        orog = f.insert_domain_anc(orog)

        ref1 = cf.CoordinateReference(name='atmosphere_hybrid_height_coordinate',
                                      ancillaries={'orog': orog, 'a': ak, 'b': bk})

        f.insert_ref(ref1)

        # Field ancillary variables
        g = f.transpose([1, 0])
        g.standard_name = 'ancillary0'
        g *= 0.01
        f.insert_field_anc(g)

        g = f.copy()
        g.standard_name = 'ancillary1'
        g *= 0.01
        f.insert_field_anc(g)

        g = f[0]
        g.squeeze(i=True)
        g.standard_name = 'ancillary2'
        g *= 0.001
        f.insert_field_anc(g)

        g = f[..., 0]
        g = g.squeeze()
        g.standard_name = 'ancillary3'
        g *= 0.001
        f.insert_field_anc(g)

        f.flag_values = [1,2,4]
        f.flag_meanings = ['a', 'bb', 'ccc']      

        f.insert_cell_methods('grid_longitude: mean grid_latitude: max')

        # Write the file, and read it in        
        cf.write(f, self.filename)

        g = cf.read(self.filename, squeeze=True)[0]

        self.assertTrue(g.equals(f, traceback=True), "Field not equal to itself read back in")
        
        x = g.dump(display=False)
        x = f.dump(display=False)
    #--- End: def

#--- End: class

if __name__ == "__main__":
    print 'Run date:', datetime.datetime.now()
    cf.environment()
    print ''
    unittest.main(verbosity=2)
