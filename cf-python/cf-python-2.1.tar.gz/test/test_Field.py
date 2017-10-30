import datetime
import inspect
import os
import unittest

import numpy

import cf

class FieldTest(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     'test_file.nc')
        self.filename2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      'test_file2.nc')
        self.contiguous = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       'DSG_timeSeries_contiguous.nc')
        
        self.chunk_sizes = (17, 34, 300, 100000)[::-1]
        self.original_chunksize = cf.CHUNKSIZE()
        self.f = cf.read(self.filename)[0]

        self.test_only = []
#        self.test_only = ['NOTHING!!!!']
#        self.test_only = ['test_Field_AUXILIARY_MASK']
#        self.test_only = ['test_Field___add__']
#        self.test_only = ['test_Field_transpose','test_Field_squeeze']
#        self.test_only = ['test_Field_match','test_Field_items']
#        self.test_only = ['test_Field_items']
#        self.test_only = ['test_Field_axes','test_Field_data_axes']
#        self.test_only = ['test_Field_where']
#        self.test_only = ['test_Field_anchor']
#        self.test_only = ['test_Field_period']
#        self.test_only = ['test_Field_mask_invalid']
#        self.test_only = ['test_Field___getitem__']
#        self.test_only = ['test_Field_section']
#        self.test_only = ['test_Field_expand_dims']
#        self.test_only = ['test_Field_field']

    def test_Field_AUXILIARY_MASK(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        ac = numpy.ma.masked_all((3, 7))
        ac[0, 0:5] = [1.0, 2.0, 3.0, -99, 5.0]
        ac[0, 3  ] = numpy.ma.masked
        ac[1, 1:5] =      [1.5, 2.5, 3.5, 4.5]
        ac[2, 3:7] =                [1.0, 2.0, 3.0, 5.0]
        
        ae = numpy.ma.masked_all((3, 8))
        ae[0, 0:5] = [1.0, 2.0, 3.0, -99, 5.0]
        ae[0, 3  ] = numpy.ma.masked
        ae[1, 1:5] =      [1.5, 2.5, 3.5, 4.5]
        ae[2, 3:8] =                [1.0, 2.0, 3.0, -99, 5.0]
        ae[2, 6  ] = numpy.ma.masked

        af = numpy.ma.masked_all((4, 9))
        af[1, 0:5] = [1.0, 2.0, 3.0, -99, 5.0]
        af[1, 3  ] = numpy.ma.masked
        af[2, 1:5] =      [1.5, 2.5, 3.5, 4.5]
        af[3, 3:8] =                [1.0, 2.0, 3.0, -99, 5.0]
        af[3, 6  ] = numpy.ma.masked
        
        query1 = cf.wi(1, 5) & cf.ne(4)

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.contiguous)[0]
            
            for (method, shape, a) in zip(['compress', 'envelope', 'full'],
                                          [ac.shape, ae.shape, af.shape],
                                          [ac, ae, af]):
                message = 'method={!r}'.format(method)

                g = f.subspace(method, time=query1)
                t = g.coord('time')

                self.assertTrue(g.shape == shape, message)
                self.assertTrue(t.shape == shape, message)

                self.assertTrue((t.data._auxiliary_mask_return().array == a.mask).all(), message)
                self.assertTrue((g.data._auxiliary_mask_return().array == a.mask).all(), message)

                self.assertTrue(cf.functions._numpy_allclose(t.array, a), message)
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)

        query2 = cf.set([1, 3, 5])

        ac2 = numpy.ma.masked_all((2, 6))
        ac2[0, 0] = 1
        ac2[0, 1] = 3
        ac2[0, 3] = 5
        ac2[1, 2] = 1
        ac2[1, 4] = 3
        ac2[1, 5] = 5

        ae2 = numpy.ma.where((ae==1)| (ae==3) | (ae==5), ae, numpy.ma.masked)
        af2 = numpy.ma.where((af==1)| (af==3) | (af==5), af, numpy.ma.masked)

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.contiguous)[0]
            
            for (method, shape, a) in zip(['compress', 'envelope', 'full'],
                                          [ac2.shape, ae2.shape, af2.shape],
                                          [ac2, ae2, af2]):

                message = 'method={!r}'.format(method)

                h = f.subspace('full', time=query1)
                g = h.subspace(method, time=query2)
                t = g.coord('time')
    
                self.assertTrue(g.shape == shape, message)        
                self.assertTrue(t.shape == shape, message)
                            
                self.assertTrue((t.data._auxiliary_mask_return().array == a.mask).all(), message)
                self.assertTrue((g.data._auxiliary_mask_return().array == a.mask).all(), message)
                
                self.assertTrue(cf.functions._numpy_allclose(t.array, a), message)
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)

        ac3 = numpy.ma.masked_all((2, 3))
        ac3[0, 0] = -2
        ac3[1, 1] = 3
        ac3[1, 2] = 4
          
        ae3 = numpy.ma.masked_all((3, 6))
        ae3[0, 0]  = -2
        ae3[2, 4] = 3
        ae3[2, 5] = 4
          
        af3 = numpy.ma.masked_all((3, 8))
        af3[0, 0] = -2
        af3[2, 4] = 3
        af3[2, 5] = 4
        
        query3 = cf.set([-2, 3, 4])

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.contiguous)[0].subspace[[0, 2, 3], 1:]
            
            for (method, shape, a) in zip(['compress', 'envelope', 'full'],
                                          [ac3.shape, ae3.shape, af3.shape],
                                          [ac3, ae3, af3]):

                message = 'method={!r}'.format(method)

                g = f.subspace(method, time=query3)
                t = g.coord('time')
    
                self.assertTrue(g.shape == shape, message)        
                self.assertTrue(t.shape == shape, message)
                            
                self.assertTrue((t.data._auxiliary_mask_return().array == a.mask).all(), message)
                self.assertTrue((g.data._auxiliary_mask_return().array == a.mask).all(), message)
                
                self.assertTrue(cf.functions._numpy_allclose(t.array, a), message)
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
#--- End: def

    def test_Field___getitem__(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0].squeeze()
            d = f.data
            f = cf.read(self.filename)[0].squeeze()

            g = f[...]
            self.assertTrue((g.data == d).all())

            g = f[:, :]
            self.assertTrue((g.data == d).all())

            g = f[slice(None), :]
            self.assertTrue((g.data == d).all())

            g = f[:, slice(0, f.shape[1], 1)]
            self.assertTrue((g.data == d).all())

            g = f[slice(0, None, 1), slice(0, None)]
            self.assertTrue((g.data == d).all())

            g = f[3:7, 2:5]
            self.assertTrue((g.data == d[3:7, 2:5]).all())
            
            g = f[6:2:-1, 4:1:-1]
            self.assertTrue((g.data == d[6:2:-1, 4:1:-1]).all())
            
            g = f[[0, 3, 8], [1, 7, 8]]

            g = f[[8, 3, 0], [8, 7, 1]]

            g = f[[7, 4, 1], slice(6, 8)]
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field___setitem__(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0].squeeze()

            f[...] = 0
            self.assertTrue((f == 0).all())
            f[3:7, 2:5] = -1
            self.assertTrue((f.array[3:7, 2:5] == -1).all())
            f[6:2:-1, 4:1:-1] = numpy.array(-1)
            self.assertTrue((f.array[6:2:-1, 4:1:-1] == -1).all())
            f[[0, 3, 8], [1, 7, 8]] = numpy.array([[[[-2]]]])
            self.assertTrue((f[[0, 3, 8], [1, 7, 8]].array == -2).all())
            f[[8, 3, 0], [8, 7, 1]] = cf.Data(-3, None)
            self.assertTrue((f[[8, 3, 0], [8, 7, 1]].array == -3).all())
            f[[7, 4, 1], slice(6, 8)] = [-4]
            self.assertTrue((f[[7, 4, 1], slice(6, 8)].array == -4).all())
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field___add__(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0].squeeze()
            g = f.copy()
            f_plus_g = f + g
            g_plus_f = g + f
#            self.assertTrue((f_plus_g).equals(g_plus_f, traceback=True),
#                            'f\n{}\nf.copy()\n{}\nf+f.copy()\n{}\nf.copy()+f\n{}'.format(
#                                str(f), str(g), str(f_plus_g), str(g_plus_f)))

            g = f[0]
            f_plus_g = f + g
            g_plus_f = g + f
#            self.assertTrue((f_plus_g).equals(g_plus_f, traceback=True),
#                            'f\n{}\nf[0]\n{}\nf+f[0]\n{}\nf[0]+f\n{}'.format(
#                                str(f), str(g), str(f_plus_g), str(g_plus_f)))
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_anchor(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        dimarray = self.f.dim('grid_lon').array
      
        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0]

            for period in (dimarray.min()-5, dimarray.min()):
                anchors = numpy.arange(dimarray.min()-3*period,
                                       dimarray.max()+3*period, 0.5)

                f.cyclic('grid_lon', period=period)

                # Increasing dimension coordinate    
                for anchor in anchors:
                    g = f.anchor('grid_lon', anchor)
                    x0 = g.coord('grid_lon').datum(-1) - period
                    x1 = g.coord('grid_lon').datum(0)
                    self.assertTrue(
                        x0 < anchor <= x1,
                        'INCREASING period=%s, x0=%s, anchor=%s, x1=%s' % \
                        (period, x0, anchor, x1))
                #--- End: for

                # Decreasing dimension coordinate    
                flipped_f = f.flip('grid_lon')
                for anchor in anchors:
                    g = flipped_f.anchor('grid_lon', anchor)
                    x1 = g.coord('grid_lon').datum(-1) + period
                    x0 = g.coord('grid_lon').datum(0)
                    self.assertTrue(
                        x1 > anchor >= x0,
                        'DECREASING period=%s, x0=%s, anchor=%s, x1=%s' % \
                        (period, x1, anchor, x0))
                #--- End: for
            #--- End: for
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_axes(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return


        f = self.f

        da = {'dim0': 1, 'dim1': 10, 'dim2': 9}

        self.assertTrue(f.axes() == da)

        self.assertTrue(f.axes() == {'dim0': cf.DomainAxis(1), 'dim1': cf.DomainAxis(10), 'dim2': cf.DomainAxis(9)})

        for key in f.data_axes():
            self.assertTrue(f.axis(key).size == da[key])

        for i in range(f.ndim):
            self.assertTrue(f.axis(i, key=True) == f.data_axes()[i])

        self.assertTrue(set(f.axes(slice(0,3))) == set(f.data_axes()))

        for k, v in f.ncdimensions.iteritems():
            self.assertTrue(f.axis('ncdim%'+v, key=True) == k)
    #--- End: def

    def test_Field_data_axes(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        self.assertTrue(self.f.copy().data_axes() == ['dim0', 'dim1', 'dim2'])
        f = cf.Field(data=cf.Data(9))
        self.assertTrue(f.data_axes() == [])
        del f.Data
        self.assertTrue(f.data_axes() == None)
    #--- End: def

    def test_Field_equals(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:    
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0]
            g = f.copy()
            self.assertTrue(f.equals(g, traceback=True))
            self.assertFalse(f.equals(g+1, traceback=False))
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_expand_dims(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        
        g = f.copy()   
        g.expand_dims(i=1)
        self.assertTrue(g.ndim == f.ndim + 1)
        self.assertTrue(g.data_axes()[1:] == f.data_axes())

        g = f.expand_dims(0)
        self.assertTrue(g.ndim == f.ndim + 1)
        self.assertTrue(g.data_axes()[1:] == f.data_axes())

        g = f.expand_dims(3)
        self.assertTrue(g.ndim == f.ndim + 1)
        self.assertTrue(g.data_axes()[:-1] == f.data_axes())

        g = f.expand_dims(-3)
        self.assertTrue(g.ndim == f.ndim + 1)
        self.assertTrue(g.data_axes()[1:] == f.data_axes())
    #--- End: def

#    def test_Field_indices(self):
#        if self.test_only and inspect.stack()[0][3] not in self.test_only:
#            return
#
#        for chunksize in self.chunk_sizes:
#            cf.CHUNKSIZE(chunksize)
#            f = cf.read(self.filename)[0]
#            
#            
#
#        cf.CHUNKSIZE(self.original_chunksize)
#    #--- End: def

    def test_Field_items(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]

        self.assertTrue(len(f.Items()) == 16)
        self.assertTrue(len(f.Items(role='damr')) == 9)

        self.assertTrue(len(f.items()) == 14)
        self.assertTrue(len(f.items(inverse=True)) == 0)

        self.assertTrue(len(f.items(ndim=1)) == 8)
        self.assertTrue(len(f.items(ndim=1, inverse=True)) == 6)

        self.assertTrue(len(f.items(ndim=2)) == 6)
        self.assertTrue(len(f.items(ndim=2, inverse=True)) == 8)

        self.assertTrue(len(f.items(ndim=cf.ge(3))) == 0)
        self.assertTrue(len(f.items(ndim=cf.ge(3), inverse=True)) == 14)

        self.assertTrue(len(f.items(ndim=cf.gt(3))) == 0)
        self.assertTrue(len(f.items(ndim=cf.gt(3), inverse=True)) == 14)

        self.assertTrue(len(f.items(role='d')) == 3)
        self.assertTrue(len(f.items(role='da')) == 6)
        self.assertTrue(len(f.items(role='dam')) == 7)

        self.assertTrue(len(f.items(axes='Y')) == 9)
        self.assertTrue(len(f.items(axes='Y', inverse=True)) == 5)

        self.assertTrue(len(f.items(axes='Z')) == 3)
        self.assertTrue(len(f.items(axes='Z', inverse=True)) == 11)
        
        self.assertTrue(len(f.items('X')) == 1)
        self.assertTrue(len(f.items('Y')) == 1)
        self.assertTrue(len(f.items('Z')) == 1)
        self.assertTrue(len(f.items('X', inverse=True)) == 13)
        self.assertTrue(len(f.items('Y', inverse=True)) == 13)
        self.assertTrue(len(f.items('Z', inverse=True)) == 13)
        self.assertTrue(len(f.items(['X', 'Y', {'standard_name': 'longitude', 'units': 'radians'}])) == 3)
        self.assertTrue(len(f.items(['X', 'Y', {'standard_name': 'longitude', 'units': 'K'}])) == 2)

        self.assertTrue(len(f.items(ndim=2)) == 6)
        self.assertTrue(len(f.items(axes='X', ndim=2)) == 6)

        self.assertTrue(len(f.items(axes='X', ndim=2, match_and=False)) == 8)

        self.assertTrue(len(f.items('longitude', axes='X', ndim=2)) == 1)
        self.assertTrue(len(f.items('grid_longitude', axes='X', ndim=2)) == 0)
        self.assertTrue(len(f.items('grid_longitude', axes='X', ndim=2, match_and=False)) == 8)

        self.assertTrue(len(f.items('atmosphere_hybrid_height_coordinate')) == 1)

        self.assertTrue(len(f.items(axes='X')) == 8)
        self.assertTrue(len(f.items(axes='Y')) == 9)
        self.assertTrue(len(f.items(axes='Z')) == 3)

        self.assertTrue(len(f.items(axes=['X','Y'])) == 11)
        self.assertTrue(len(f.items(axes=['X','Z'])) == 11)
        self.assertTrue(len(f.items(axes=['Z','Y'])) == 12)

        self.assertTrue(len(f.items(axes_all='X')) == 2)
        self.assertTrue(len(f.items(axes_all='Y')) == 3)
        self.assertTrue(len(f.items(axes_all='Z')) == 3)
        self.assertTrue(len(f.items(axes_all=['X','Y'])) == 6)
        self.assertTrue(len(f.items(axes_all=['X','Z'])) == 0)
        self.assertTrue(len(f.items(axes_all=['Z','Y'])) == 0)

        self.assertTrue(len(f.items(axes_subset='X')) == 8)
        self.assertTrue(len(f.items(axes_subset='Y')) == 9)
        self.assertTrue(len(f.items(axes_subset='Z')) == 3)
        self.assertTrue(len(f.items(axes_subset=['X','Y'])) == 6)
        self.assertTrue(len(f.items(axes_subset=['X','Z'])) == 0)
        self.assertTrue(len(f.items(axes_subset=['Z','Y'])) == 0)

        self.assertTrue(len(f.items(axes_superset='X')) == 2)
        self.assertTrue(len(f.items(axes_superset='Y')) == 3)
        self.assertTrue(len(f.items(axes_superset='Z')) == 3)

        self.assertTrue(len(f.items(axes_superset=['X','Y'])) == 11)
        self.assertTrue(len(f.items(axes_superset=['X','Z'])) == 5)
        self.assertTrue(len(f.items(axes_superset=['Z','Y'])) == 6)
    #--- End: def

    def test_Field_match(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        f.long_name = 'qwerty'
        f.ncvar = 'tas'
        all_kwargs = (
            {'inverse': False},
            {'inverse': False, 'description': None},
            {'inverse': False, 'description': {}},
            {'inverse': False, 'description': []},
            {'inverse': False, 'description': [None]},
            {'inverse': False, 'description': [{}]},
            {'inverse': False, 'description': [None, {}]},
            {'inverse': False, 'description':  'eastward_wind'},
            {'inverse': False, 'description':  'eastward_wind', 'exact': True},
            {'inverse': False, 'description':  'eastward_'},
            {'inverse': False, 'description':  'e.*_wind$'},
            {'inverse': False, 'description':  'standard_name:eastward_wind'},
            {'inverse': False, 'description':  'standard_name:eastward_wind', 'exact': True},
            {'inverse': False, 'description':  'standard_name:eastward_'},
            {'inverse': False, 'description': {'standard_name': 'eastward_wind'}},
            {'inverse': False, 'description': {'standard_name': 'eastward_'}},
            {'inverse': False, 'description': cf.eq('.*_wind', exact=False)},
            {'inverse': False, 'description':  'long_name:qwerty'},
            {'inverse': False, 'description':  'long_name:qwerty', 'exact': True},
            {'inverse': False, 'description':  'long_name:qwe'},
            {'inverse': False, 'description': {'long_name': 'qwerty'}},
            {'inverse': False, 'description': {'long_name': 'qwe'}},
            {'inverse': False, 'description': {'long_name': cf.eq('qwerty')}},
            {'inverse': False, 'description': {'long_name': cf.eq('qwe', exact=False)}},
            {'inverse': False, 'description': 'ncvar%tas'},
            {'inverse': False, 'description': 'ncvar%tas', 'exact': True},
            {'inverse': False, 'description': 'ncvar%ta'},
            {'inverse': False, 'description': {None: 'ncvar%.*as$'}},
            {'inverse': False, 'description': {None: 'ncvar%tas$'}},
            {'inverse': False, 'description': {None: 'ncvar%tas'}},
            {'inverse': False, 'description': {None: 'ncvar%ta'}},
            #          
            {'inverse': False, 'description':  'eastward_wind', 'ndim': cf.wi(1, 3)},
            {'inverse': False, 'description':  'BBB', 'ndim': cf.wi(1, 3), 'match_and': False},
            {'inverse': False, 'description':  ['BBB', 'east'], 'ndim': cf.wi(1, 3), 'match_and': True},
            {'inverse': False, 'ndim': cf.wi(1, 3)},
        )
        for kwargs in all_kwargs:
            self.assertTrue(f.match(**kwargs), 
                            'f.match(**{}) failed'.format(kwargs))
            kwargs['inverse'] = not kwargs['inverse']
            self.assertFalse(f.match(**kwargs),
                             'f.match(**{}) failed'.format(kwargs))
        #--- End: for
    #--- End: def

    def test_Field_period(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        f.dim('X').period(None)
        f.cyclic('X', False)
        self.assertTrue(f.period('X') is None)
        f.cyclic('X', period=360)
        self.assertTrue(f.period('X') == cf.Data(360, 'degrees'))
        f.cyclic('X', False)
        self.assertTrue(f.period('X') == cf.Data(360, 'degrees'))
        f.dim('X').period(None)
        self.assertTrue(f.period('X') is None)
    #--- End: def

    def test_Field_section(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename2)[0][0:100]
            self.assertTrue(len(f.section(('X','Y'))) == 100,
                            'CHUNKSIZE = %s' % chunksize)
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Field_squeeze(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]

        f.squeeze(i=True)
        g = f.copy()
        h = f.copy()
        i = h.squeeze(i=True)
        self.assertTrue(f.equals(g))
        self.assertTrue(h is i)
    #--- End: def

    def test_Field_transpose(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]

        # Null tranpose
        self.assertTrue(f is f.transpose([0, 1, 2], i=True))
        self.assertTrue(f.equals(f.transpose([0, 1, 2])))

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)            
            f = cf.read(self.filename)[0]
            h = f.transpose((1, 2, 0))
            h0 = h.transpose(('atmos', 'grid_latitude', 'grid_longitude'))
            h.transpose((2, 0, 1), i=True)
            h.transpose(('grid_longitude', 'atmos', 'grid_latitude'), i=True)
            h.varray
            h.transpose(('atmos', 'grid_latitude', 'grid_longitude'), i=True)
            self.assertTrue(cf.equals(h, h0, traceback=True))
            self.assertTrue((h.array==f.array).all())
        #--- End: for    
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

#    def test_Field_collapse(self):
#        if self.test_only and inspect.stack()[0][3] not in self.test_only:
#            return
#
#        for chunksize in self.chunk_sizes:
#            cf.CHUNKSIZE(chunksize)
#            f = cf.read(self.filename2)[0]
#
#            g = f.collapse('mean')
#            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: latitude: longitude: mean').write(f.axes_names()))
#
#            g = f.collapse('mean', axes=['T', 'X'])
#            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: longitude: mean').write(f.axes_names()))
#
#            g = f.collapse('mean', axes=[0, 2])
#            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: longitude: mean').write(f.axes_names()))
#            
#            g = f.collapse('T: mean within years time: minimum over years', 
#                           within_years=cf.M(), weights=None, _debug=0)
#            self.assertTrue(g.cell_methods == cf.CellMethods('time: maximum time: mean within years time: minimum over years').write(f.axes_names()))
#
#            for m in range(1, 13):
#                a = numpy.empty((5, 4, 5))
#                for i, year in enumerate(f.subspace(T=cf.month(m)).coord('T').year.unique()):
#                    q = cf.month(m) & cf.year(year)
#                    x = f.subspace(T=q)
#                    x.data.mean(axes=0, i=True)
#                    a[i] = x.array
#                #--- End: for
#                a = a.min(axis=0)
#                self.assertTrue(numpy.allclose(a, g.array[m % 12]))
#            #--- End: for  
#
#            g = f.collapse('T: mean', group=360)
#
#            for group in (cf.M(12), 
#                          cf.M(12, month=12),
#                          cf.M(12, day=16),
#                          cf.M(12, month=11, day=27)):
#                g = f.collapse('T: mean', group=group)
#                bound = g.coord('T').bounds.dtarray[0, 1]
#                self.assertTrue(bound.month == group.offset.month,
#                                "{}!={}, group={}".format(bound.month, group.offset.month, group))
#                self.assertTrue(bound.day   == group.offset.day,
#                                "{}!={}, group={}".format(bound.day, group.offset.day, group))
#            #--- End: for  
#
##            for group in (cf.D(30), 
##                          cf.D(30, month=12),
##                          cf.D(30, day=16),
##                          cf.D(30, month=11, day=27)):
##                g = f.collapse('T: mean', group=group)
##                bound = g.coord('T').bounds.dtarray[0, 1]
##                self.assertTrue(bound.day == group.offset.day,
##                                "{}!={}, bound={}, group={}".format(bound.day, group.offset.day, bound, group))
#            #--- End: for  
#
#        #--- End: for    
#
#        cf.CHUNKSIZE(self.original_chunksize)
#    #--- End: def

    def test_Field_where(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        a = f.array

        for chunksize in self.chunk_sizes:
            cf.CHUNKSIZE(chunksize)
            f = cf.read(self.filename)[0]

            for condition in (True, 1, [[[True]]], [[[[[456]]]]]):
                g = f.where(condition, -9)
                self.assertTrue(g[0].min() == -9)
                self.assertTrue(g[0].max() == -9)                

            g = f.where(cf.le(34), 34)
            self.assertTrue(g[0].min() == 34)
            self.assertTrue(g[0].max() == 89)   

            g = f.where(cf.le(34), cf.masked)
            self.assertTrue(g[0].min() == 35)
            self.assertTrue(g[0].max() == 89) 

            g = f.where(cf.le(34), cf.masked, 45)
            self.assertTrue(g[0].min() == 45)
            self.assertTrue(g[0].max() == 45)               
        #--- End: for

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def   

    def test_Field_mask_invalid(self):
        if self.test_only and inspect.stack()[0][3] not in self.test_only:
            return

        f = cf.read(self.filename)[0]
        g = f.mask_invalid()

        f = cf.read(self.filename)[0]
        f.mask_invalid(i=True)
    #--- End: def


#    def test_Field_field(self):
#        if self.test_only and inspect.stack()[0][3] not in self.test_only:
#            return
#
#        f = cf.read(self.filename)[0]
#
#        y = f.field('grid_lat')
#        print y
#    #--- End: def

#--- End: class

if __name__ == '__main__':
    print 'Run date:', datetime.datetime.now()
    cf.environment()
    print''
    unittest.main(verbosity=2)
