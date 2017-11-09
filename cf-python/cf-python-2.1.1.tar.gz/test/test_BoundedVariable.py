import datetime
import os
import time 
import unittest

import numpy

import cf

class BoundedVariableTest(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'test_file.nc')
        self.chunk_sizes = (17, 34, 300, 100000)[::-1]
        self.original_chunksize = cf.CHUNKSIZE()
        
    def test_BoundedVariable__binary_operation(self):
        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0]
            x = f.coord('X')

            self.assertTrue(isinstance(x, cf.BoundedVariable))
            
            d = x.array
            b = x.bounds.array
            d2= numpy.expand_dims(d, -1)

            # --------------------------------------------------------
            # Out-of-place addition
            # --------------------------------------------------------
            c = x + 2
            self.assertTrue((c.array == d + 2).all())
            self.assertTrue((c.bounds.array == b + 2).all())
            
            c = x + x
            self.assertTrue((c.array == d + d).all())
            self.assertTrue((c.bounds.array == b + d2).all())
            
            c = x + 2
            self.assertTrue((c.array == d + 2).all())
            self.assertTrue((c.bounds.array == b + 2).all())
            
            self.assertTrue((x.array == d).all())
            self.assertTrue((x.bounds.array == b).all())

            # --------------------------------------------------------
            # In-place addition
            # --------------------------------------------------------
            x += 2
            self.assertTrue((x.array == d + 2).all())
            self.assertTrue((x.bounds.array == b + 2).all())
            
            x += x
            self.assertTrue((x.array == (d+2) * 2).all())
            self.assertTrue((x.bounds.array == b+2 + d2+2).all())

            x += 2
            self.assertTrue((x.array == (d+2)*2 + 2).all())
            self.assertTrue((x.bounds.array == b+2 + d2+2 + 2).all())
            
            # --------------------------------------------------------
            # Out-of-place addition (no bounds)
            # --------------------------------------------------------
            f = cf.read(self.filename)[0]
            x = f.coord('X')
            del x.bounds
            
            self.assertTrue(isinstance(x, cf.BoundedVariable))
            self.assertTrue(not hasattr(x, 'bounds'))
           
            d = x.array

            c = x + 2
            self.assertTrue((c.array == d + 2).all())
            
            c = x + x
            self.assertTrue((c.array == d + d).all())
            
            c = x + 2
            self.assertTrue((c.array == d + 2).all())
            
            self.assertTrue((x.array == d).all())

            # --------------------------------------------------------
            # In-place addition (no bounds)
            # --------------------------------------------------------
            x += 2
            self.assertTrue((x.array == d + 2).all())
            
            x += x
            self.assertTrue((x.array == (d+2) * 2).all())

            x += 2
            self.assertTrue((x.array == (d+2)*2 + 2).all())
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

#--- End: class

if __name__ == "__main__":
    print 'Run date:', datetime.datetime.now()
    cf.environment()
    print ''
    unittest.main(verbosity=2)
