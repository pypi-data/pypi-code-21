import datetime
import tempfile
import os
import unittest
import atexit
import inspect

import numpy

import cf

tmpfile  = tempfile.mktemp('.cf-python_test')
tmpfiles = [tmpfile]
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

class read_writeTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    test_only = []
#    test_only = ['NOTHING!!!!!']
#    test_only = ['test_write_reference_datetime']
#    test_only = ['test_write_HDF_chunks']
#    test_only = ['test_read_write_unlimited']
#    test_only = ['test_read_field']
#    test_only = ['test_write_datatype']
#    test_only = ['test_read_field_function']
    
    def test_read_select(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        # select on field list
        f = cf.read(self.filename, select='eastward_wind')
        g = cf.read(self.filename)
        self.assertTrue(f.equals(g, traceback=True),
                        'Bad read with select keyword')
    #--- End: def

    def test_read_field_function(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        g = cf.read_field(self.filename)

        self.assertTrue(f.equals(g, traceback=True))
    #--- End: def


    def test_read_field(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        # Test field keyword of cfdm.read
        filename = self.filename
        
        f = cf.read(filename)
        self.assertTrue(len(f) == 1, '\n'+str(f))

        f = cf.read(filename, field=['dimension_coordinate'])
        self.assertTrue(len(f) == 4, '\n'+str(f))

        f = cf.read(filename, field=['auxiliary_coordinate'])
        self.assertTrue(len(f) == 4, '\n'+str(f))
        
        f = cf.read(filename, field='cell_measure')
        self.assertTrue(len(f) == 2, '\n'+str(f))

        f = cf.read(filename, field=['field_ancillary'])
        self.assertTrue(len(f) == 5, '\n'+str(f))
                
        f = cf.read(filename, field='domain_ancillary')
        self.assertTrue(len(f) == 4, '\n'+str(f))
        
        f = cf.read(filename, field=['field_ancillary', 'auxiliary_coordinate'])
        self.assertTrue(len(f) == 8, '\n'+str(f))
        
        self.assertTrue(len(cf.read(filename, field=['domain_ancillary', 'auxiliary_coordinate'])) == 7)
        f = cf.read(filename, field=['domain_ancillary', 'cell_measure', 'auxiliary_coordinate'])
        self.assertTrue(len(f) == 8, '\n'+str(f))
        
        f = cf.read(filename, field='all')
        self.assertTrue(len(f) == 15, '\n'+str(f))

        f = cf.read(filename, field=('field_ancillary', 'dimension_coordinate',
                                     'cell_measure', 'auxiliary_coordinate',
                                     'domain_ancillary'))
        self.assertTrue(len(f) == 15, '\n'+str(f))
    #--- End: def

    def test_read_write_format(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            f = cf.read(self.filename)[0]
            for fmt in ('NETCDF3_CLASSIC',
                        'NETCDF3_64BIT',
                        'NETCDF4',
                        'NETCDF4_CLASSIC',
                        'CFA3', 
                        'CFA4'):
                cf.write(f, tmpfile, fmt=fmt)
                g = cf.read(tmpfile)[0]
                self.assertTrue(f.equals(g, traceback=True),
                                'Bad read/write of format: {0}'.format(fmt))
        #--- End: for
    #--- End: def

    def test_read_write_netCDF4_compress_shuffle(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            f = cf.read(self.filename)[0]
            for fmt in ('NETCDF4',
                        'NETCDF4_CLASSIC',
                        'CFA4'):
                for no_shuffle in (True, False):
                    for compress in range(10):
                        cf.write(f, tmpfile, fmt=fmt,
                                 compress=compress,
                                 no_shuffle=no_shuffle)
                        g = cf.read(tmpfile)[0]
                        self.assertTrue(
                            f.equals(g, traceback=True),
                            'Bad read/write with lossless compression: {0}, {1}, {2}'.format(fmt, compress, no_shuffle))
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize) 
    #--- End: def

    def test_write_datatype(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:   
            cf.CHUNKSIZE(chunksize) 
            f = cf.read(self.filename)[0] 
            self.assertTrue(f.dtype == numpy.dtype(float))
            cf.write(f, tmpfile, fmt='NETCDF4', 
                     datatype={numpy.dtype(float): numpy.dtype('float32')})
            g = cf.read(tmpfile)[0]
            self.assertTrue(g.dtype == numpy.dtype('float32'), 
                            'datatype read in is '+str(g.dtype))
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize) 
    #--- End: def

    def test_write_reference_datetime(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for reference_datetime in ('1751-2-3', '1492-12-30'):
            for chunksize in self.chunk_sizes:   
                cf.CHUNKSIZE(chunksize) 
                f = cf.read(self.filename)[0]
                t = cf.DimensionCoordinate(data=cf.Data(123, 'days since 1750-1-1'))
                t.standard_name = 'time'
                dim = f.insert_axis(cf.DomainAxis(1))
                f.insert_dim(t, key=dim)
                cf.write(f, tmpfile, fmt='NETCDF4', reference_datetime=reference_datetime)
                g = cf.read(tmpfile)[0]
                t = g.dim('T')
                self.assertTrue(t.Units == cf.Units('days since '+reference_datetime),
                                'Units written were '+repr(t.Units.reftime)+' not '+repr(reference_datetime))
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize) 
    #--- End: def

    def test_write_HDF_chunks(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return
            
        for chunksize in self.chunk_sizes:   
            for fmt in ('NETCDF3_CLASSIC', 'NETCDF4'):
                cf.CHUNKSIZE(chunksize) 
                f = cf.read(self.filename)[0]
                f.HDF_chunks({'T': 10000, 1: 3, 'grid_lat': 222, 45:45})
                cf.write(f, tmpfile, fmt=fmt, HDF_chunksizes={'X': 6})
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize) 
    #--- End: def

    def test_read_write_unlimited(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return
        f = cf.read(self.filename)[0]

        fmt = 'NETCDF4'
        for axis in ('atmosphere_hybrid_height_coordinate', 'X', 'Y'):
            org = f.unlimited({axis: True})
            cf.write(f, tmpfile, fmt=fmt)
            f.unlimited(org)
            
            g = cf.read(tmpfile)[0]
            self.assertTrue(g.unlimited()[g.axis(axis, key=True)] is True,
                            'Failed with axis={}, fmt={}'.format(axis, fmt))

        fmt = 'NETCDF3_CLASSIC'
        for axis in ('atmosphere_hybrid_height_coordinate',):
            org = f.unlimited({axis: True})
            cf.write(f, tmpfile, fmt=fmt)
            f.unlimited(org)
            
            g = cf.read(tmpfile)[0]
            self.assertTrue(g.unlimited()[g.axis(axis, key=True)] is True,
                            'Failed with axis={}, fmt={}'.format(axis, fmt))

        fmt = 'NETCDF4'
        org = f.unlimited({'Y': True, 'X': True})
        cf.write(f, tmpfile, fmt=fmt)
        f.unlimited(org)

        g = cf.read(tmpfile)[0]
        self.assertTrue(g.unlimited()[g.axis('X', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('X', fmt))
        self.assertTrue(g.unlimited()[g.axis('Y', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('Y', fmt))


        fmt = 'NETCDF4'
        org = f.unlimited({'X': False})
        cf.write(f, tmpfile, fmt=fmt, unlimited=['X'])
        f.unlimited(org)

        g = cf.read(tmpfile)[0]
        self.assertTrue(not g.unlimited()[g.axis('X', key=True)],
                        'Failed with axis={}, fmt={}'.format('X', fmt))


        fmt = 'NETCDF4'
        org = f.unlimited({'X': True})
        cf.write(f, tmpfile, fmt=fmt, unlimited=['X'])
        f.unlimited(org)

        g = cf.read(tmpfile)[0]
        self.assertTrue(g.unlimited()[g.axis('X', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('X', fmt))


        fmt = 'NETCDF4'
        org = f.unlimited({'Y': True})
        cf.write(f, tmpfile, fmt=fmt, unlimited=['X'])
        f.unlimited(org)

        g = cf.read(tmpfile)[0]
        self.assertTrue(g.unlimited()[g.axis('X', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('X', fmt))
        self.assertTrue(g.unlimited()[g.axis('Y', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('Y', fmt))

 

        fmt = 'NETCDF4'
        org = f.unlimited({('X', 'Y'): True})
        cf.write(f, tmpfile, fmt=fmt)
        f.unlimited(org)

        g = cf.read(tmpfile)[0]
        self.assertTrue(g.unlimited()[g.axis('X', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('X', fmt))
        self.assertTrue(g.unlimited()[g.axis('Y', key=True)] is True,
                        'Failed with axis={}, fmt={}'.format('Y', fmt))

 

        fmt = 'NETCDF4'
        org = f.unlimited({('X', 'Y'): True})
        f.unlimited(None)
        cf.write(f, tmpfile, fmt=fmt)
        f.unlimited(org)

        g = cf.read(tmpfile)[0]
        self.assertTrue(not g.unlimited()[g.axis('X', key=True)],
                        'Failed with axis={}, fmt={}'.format('X', fmt))
        self.assertTrue(not g.unlimited()[g.axis('Y', key=True)],
                        'Failed with axis={}, fmt={}'.format('Y', fmt))

    #--- End: def
#--- End: class

if __name__ == "__main__":
    print 'Run date:', datetime.datetime.now()
    cf.environment()
    print''
    unittest.main(verbosity=2)
