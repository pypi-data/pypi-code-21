import os
import unittest

import numpy

import cf

class CoordinateReferenceTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]

    def test_CoordinateReference_equals(self):
        f = cf.read(self.filename)[0]
        
        t = cf.CoordinateReference(name='atmosphere_hybrid_height_coordinate',
                                   ancillaries={'a': 'aux0', 'b': 'aux1', 'orog': 'orog'})
        self.assertTrue(t.equals(t.copy(), traceback=True))
        
        # Create a rotated_latitude_longitude grid mapping coordinate
        # reference
        t = cf.CoordinateReference(name='rotated_latitude_longitude',
                                   parameters={'grid_north_pole_latitude': 38.0,
                                               'grid_north_pole_longitude': 190.0})
        self.assertTrue(t.equals(t.copy(), traceback=True))

        t = cf.CoordinateReference(name='rotated_latitude_longitude',
                                   coordinates=('coord1', 'coord2'),
                                   parameters={'grid_north_pole_latitude': 38.0,
                                               'grid_north_pole_longitude': 190.0},
                                   ancillaries={'a': 'aux0', 'b': 'aux1', 'orog': 'orog'})
        self.assertTrue(t.equals(t.copy(), traceback=True))
    #--- End: def

    def test_Field_ref_refs(self):
        f = cf.read(self.filename)[0]
        
        self.assertTrue(f.ref('BLAH') is None)
        self.assertTrue(f.ref('atmos', key=True) == 'ref0')
        self.assertTrue(f.ref('atmos', key=True, inverse=True) == 'ref1')

        self.assertTrue(set(f.refs()) == set(['ref0', 'ref1']))
        self.assertTrue(set(f.refs('BLAH')) == set())
        self.assertTrue(set(f.refs('rot')) == set(['ref1']))
        self.assertTrue(set(f.refs('rot', inverse=True)) == set(['ref0']))
        self.assertTrue(set(f.refs('atmosphere_hybrid_height_coordinate', exact=True)) == set(['ref0']))
    #--- End: def
#--- End: class

if __name__ == '__main__':
    print 'cf-python version:', cf.__version__
    print 'cf-python path:'   , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)

  
