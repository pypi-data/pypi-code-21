import datetime
import inspect
import os
import sys
import unittest

import numpy

import cf

class FieldTest(unittest.TestCase):
    def setUp(self):
        self.filename2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'test_file2.nc')
        
        self.chunk_sizes = (17, 34, 300, 100000)[::-1]
        self.original_chunksize = cf.CHUNKSIZE()

        self.f = cf.read(self.filename2)[0]

        self.test_only = []

    def test_COLLAPSE(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        cf.CHUNKSIZE(self.original_chunksize)
        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)

            f = self.f

            g = f.collapse('mean')
            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: latitude: longitude: mean').write(f.axes_names()))

            g = f.collapse('mean', axes=['T', 'X'])
            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: longitude: mean').write(f.axes_names()))

            g = f.collapse('mean', axes=[0, 2])
            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: longitude: mean').write(f.axes_names()))

            g = f.collapse('T: mean within years time: minimum over years', 
                           within_years=cf.M(), weights=None, _debug=0)
            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: mean within years time: minimum over years').write(f.axes_names()))

            for m in range(1, 13):
                a = numpy.empty((5, 4, 5))
                for i, year in enumerate(f.subspace(T=cf.month(m)).coord('T').year.unique()):
                    q = cf.month(m) & cf.year(year)
                    x = f.subspace(T=q)
                    x.data.mean(axes=0, i=True)
                    a[i] = x.array

                a = a.min(axis=0)
                self.assertTrue(numpy.allclose(a, g.array[m % 12]))
            #--- End: for  

            g = f.collapse('T: mean', group=360)

            for group in (cf.M(12), 
                          cf.M(12, month=12),
                          cf.M(12, day=16),
                          cf.M(12, month=11, day=27)):
                g = f.collapse('T: mean', group=group)
                bound = g.coord('T').bounds.dtarray[0, 1]
                self.assertTrue(bound.month == group.offset.month,
                                "{}!={}, group={}".format(bound.month, group.offset.month, group))
                self.assertTrue(bound.day   == group.offset.day,
                                "{}!={}, group={}".format(bound.day, group.offset.day, group))
            #--- End: for  

#            for group in (cf.D(30), 
#                          cf.D(30, month=12),
#                          cf.D(30, day=16),
#                          cf.D(30, month=11, day=27)):
#                g = f.collapse('T: mean', group=group)
#                bound = g.coord('T').bounds.dtarray[0, 1]
#                self.assertTrue(bound.day == group.offset.day,
#                                "{}!={}, bound={}, group={}".format(bound.day, group.offset.day, bound, group))
            #--- End: for  

        #--- End: for    

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def
     
#--- End: class

if __name__ == '__main__':
    print 'Run date:', datetime.datetime.now()
    cf.environment()
    print''
    unittest.main(verbosity=2)
