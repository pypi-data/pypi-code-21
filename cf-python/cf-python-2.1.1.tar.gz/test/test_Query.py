import datetime
import os
import unittest

import numpy

import cf

class QueryTest(unittest.TestCase):
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            'test_file.nc')
    chunk_sizes = (17, 34, 300, 100000)[::-1]
    original_chunksize = cf.CHUNKSIZE()

    def test_Query_contain(self):
        for chunksize in self.chunk_sizes:  
            f = cf.read(self.filename)[0]
            c = f.dim('X')
            self.assertTrue(((cf.contain(21.1)==c).array == 
                            numpy.array([0,1,0,0,0,0,0,0,0], bool)).all())
            self.assertTrue(((cf.contain(999)==c).array == 
                            numpy.array([0,0,0,0,0,0,0,0,0], bool)).all())
    #--- End: def

    def test_Query_datetime1(self):
        for chunksize in self.chunk_sizes:    
            cf.CHUNKSIZE(chunksize)
            d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:00:00')

            message = 'Diff ='+str((d-cf.Data(cf.dt('2001-01-03 21:00:00'))).array)
            
            self.assertTrue((d==cf.eq(cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[False, True], [False, False]])), message)
            self.assertTrue((d==cf.ne(cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[True, False], [True, True]])), message)
            self.assertTrue((d==cf.ge(cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[False, True], [True, False]])), message)
            self.assertTrue((d==cf.gt(cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[False, False], [True, False]])), message)
            self.assertTrue((d==cf.le(cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[True, True], [False, True]])), message)
            self.assertTrue((d==cf.lt(cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[True, False], [False, True]])), message) 
            self.assertTrue((d==cf.wi(cf.dt('2000-12-31 21:00:00'), cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[False, True], [False, True]])), message) 
            self.assertTrue((d==cf.wo(cf.dt('2000-12-31 21:00:00'), cf.dt('2001-01-03 21:00:00'))).equals(cf.Data([[True, False], [True, False]])), message) 
            self.assertTrue((d==cf.set([cf.dt('2000-12-31 21:00:00'), cf.dt('2001-01-03 21:00:00')])).equals(cf.Data([[False, True], [False, True]])), message) 

        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Query_year_month_day_hour_minute_second(self):
        for chunksize in self.chunk_sizes:    
            cf.CHUNKSIZE(chunksize)
            d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:57:57')   
            self.assertTrue((d==cf.year(2000)).equals(cf.Data([[True, False], [False, True]])))
            self.assertTrue((d==cf.month(12)).equals(cf.Data([[True, False], [False, True]])))
            self.assertTrue((d==cf.day(3)).equals(cf.Data([[False, True], [False, False]])))
            d = cf.Data([[1., 5], [6, 2]], 'hours since 2000-12-29 21:57:57')
            self.assertTrue((d==cf.hour(2)).equals(cf.Data([[False, True], [False, False]])))
            d = cf.Data([[1., 5], [6, 2]], 'minutes since 2000-12-29 21:57:57')
            self.assertTrue((d==cf.minute(2)).equals(cf.Data([[False, True], [False, False]])))
            d = cf.Data([[1., 5], [6, 2]], 'seconds since 2000-12-29 21:57:57')
            self.assertTrue((d==cf.second(2)).equals(cf.Data([[False, True], [False, False]]))) 
        
            d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:57:57')   
            self.assertTrue((d==cf.year(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
            self.assertTrue((d==cf.month(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
            self.assertTrue((d==cf.day(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
            d = cf.Data([[1., 5], [6, 2]], 'hours since 2000-12-29 21:57:57')
            self.assertTrue((d==cf.hour(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
            d = cf.Data([[1., 5], [6, 2]], 'minutes since 2000-12-29 21:57:57')
            self.assertTrue((d==cf.minute(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]])))
            d = cf.Data([[1., 5], [6, 2]], 'seconds since 2000-12-29 21:57:57')
            self.assertTrue((d==cf.second(cf.ne(-1))).equals(cf.Data([[True, True], [True, True]]))) 
        #--- End: def
        cf.CHUNKSIZE(self.original_chunksize)  
    #--- End: def

    def test_Query_dteq_dtne_dtge_dtgt_dtle_dtlt(self):
        for chunksize in self.chunk_sizes:    
            cf.CHUNKSIZE(chunksize)
            d = cf.Data([[1., 5.], [6, 2]], 'days since 2000-12-29 21:00:00')

            message = 'Diff ='+str((d-cf.Data(cf.dt('2001-01-03 21:00:00'))).array)
            
            self.assertTrue((d==cf.dteq('2001-01-03 21:00:00')).equals(cf.Data([[False, True], [False, False]])), message)
            self.assertTrue((d==cf.dtne('2001-01-03 21:00:00')).equals(cf.Data([[True, False], [True, True]])), message)
            self.assertTrue((d==cf.dtge('2001-01-03 21:00:00')).equals(cf.Data([[False, True], [True, False]])), message)
            self.assertTrue((d==cf.dtgt('2001-01-03 21:00:00')).equals(cf.Data([[False, False], [True, False]])), message)
            self.assertTrue((d==cf.dtle('2001-01-03 21:00:00')).equals(cf.Data([[True, True], [False, True]])), message)
            self.assertTrue((d==cf.dtlt('2001-01-03 21:00:00')).equals(cf.Data([[True, False], [False, True]])), message) 
        
            self.assertTrue((d==cf.dteq(2001, 1, 3, 21, 0, 0)).equals(cf.Data([[False, True], [False, False]])), message)
            self.assertTrue((d==cf.dtne(2001, 1, 3, 21, 0, 0)).equals(cf.Data([[True, False], [True, True]])), message)
            self.assertTrue((d==cf.dtge(2001, 1, 3, 21, 0, 0)).equals(cf.Data([[False, True], [True, False]])), message)
            self.assertTrue((d==cf.dtgt(2001, 1, 3, 21, 0, 0)).equals(cf.Data([[False, False], [True, False]])), message)
            self.assertTrue((d==cf.dtle(2001, 1, 3, 21, 0, 0)).equals(cf.Data([[True, True], [False, True]])), message)
            self.assertTrue((d==cf.dtlt(2001, 1, 3, 21, 0, 0)).equals(cf.Data([[True, False], [False, True]])), message) 
        
            d = cf.dt(2002, 6, 16)
            self.assertTrue(not (d == cf.dteq(1990, 1, 1)))
            self.assertTrue(d == cf.dteq(2002, 6, 16))
            self.assertTrue(not(d == cf.dteq('2100-1-1')))
            self.assertTrue(not (d == cf.dteq('2001-1-1') & cf.dteq(2010, 12, 31)))
        
            d = cf.dt(2002, 6, 16)
            self.assertTrue(d == cf.dtge(1990, 1, 1))
            self.assertTrue(d == cf.dtge(2002, 6, 16))
            self.assertTrue(not (d == cf.dtge('2100-1-1')))
            self.assertTrue(not (d == cf.dtge('2001-1-1') & cf.dtge(2010, 12, 31)))
                                        
            d = cf.dt(2002, 6, 16)
            self.assertTrue(d == cf.dtgt(1990, 1, 1))
            self.assertTrue(not (d == cf.dtgt(2002, 6, 16)))
            self.assertTrue(not (d == cf.dtgt('2100-1-1')))
            self.assertTrue(d == cf.dtgt('2001-1-1') & cf.dtle(2010, 12, 31))
        
            d = cf.dt(2002, 6, 16)
            self.assertTrue(d == cf.dtne(1990, 1, 1))
            self.assertTrue(not (d == cf.dtne(2002, 6, 16)))
            self.assertTrue(d == cf.dtne('2100-1-1'))
            self.assertTrue(d == cf.dtne('2001-1-1') & cf.dtne(2010, 12, 31))
        
            d = cf.dt(2002, 6, 16)
            self.assertTrue(not (d == cf.dtle(1990, 1, 1)))
            self.assertTrue(d == cf.dtle(2002, 6, 16))
            self.assertTrue(d == cf.dtle('2100-1-1'))
            self.assertTrue(not (d == cf.dtle('2001-1-1') & cf.dtle(2010, 12, 31)))
        
            d = cf.dt(2002, 6, 16)
            self.assertTrue(not (d == cf.dtlt(1990, 1, 1)))
            self.assertTrue(not (d == cf.dtlt(2002, 6, 16)))
            self.assertTrue(d == cf.dtlt('2100-1-1'))
            self.assertTrue(not (d == cf.dtlt('2001-1-1') & cf.dtlt(2010, 12, 31)))
        #--- End: for
        cf.CHUNKSIZE(self.original_chunksize)
    #--- End: def

    def test_Query_evaluate(self):
        for x in (5, cf.Data(5, 'kg m-2'), cf.Data([5], 'kg m-2 s-1')):
            self.assertTrue(x == cf.eq(5))
            self.assertTrue(x == cf.lt(8))
            self.assertTrue(x == cf.le(8))
            self.assertTrue(x == cf.gt(3))
            self.assertTrue(x == cf.ge(3))
            self.assertTrue(x == cf.wi(3, 8))
            self.assertTrue(x == cf.wo(8, 11))
            self.assertTrue(x == cf.set([3, 5, 8]))

            self.assertTrue(cf.eq(5)          == x)
            self.assertTrue(cf.lt(8)          == x)
            self.assertTrue(cf.le(8)          == x)
            self.assertTrue(cf.gt(3)          == x)
            self.assertTrue(cf.ge(3)          == x)
            self.assertTrue(cf.wi(3, 8)       == x)
            self.assertTrue(cf.wo(8, 11)      == x)
            self.assertTrue(cf.set([3, 5, 8]) == x)

            self.assertFalse(x == cf.eq(8))
            self.assertFalse(x == cf.lt(3))
            self.assertFalse(x == cf.le(3))
            self.assertFalse(x == cf.gt(8))
            self.assertFalse(x == cf.ge(8))
            self.assertFalse(x == cf.wi(8, 11))
            self.assertFalse(x == cf.wo(3, 8))
            self.assertFalse(x == cf.set([3, 8, 11]))

            self.assertFalse(x == cf.eq(8)           == x)
            self.assertFalse(x == cf.lt(3)           == x)
            self.assertFalse(x == cf.le(3)           == x)
            self.assertFalse(x == cf.gt(8)           == x)
            self.assertFalse(x == cf.ge(8)           == x)
            self.assertFalse(x == cf.wi(8, 11)       == x)
            self.assertFalse(x == cf.wo(3, 8)        == x)
            self.assertFalse(x == cf.set([3, 8, 11]) == x)
        #--- End: for

        c = cf.wi(2, 4)
        d = cf.wi(6, 8)

        e = d | c

        self.assertTrue(c.evaluate(3))
        self.assertFalse(c.evaluate(5))

        self.assertTrue(e.evaluate(3))
        self.assertTrue(e.evaluate(7))
        self.assertFalse(e.evaluate(5))

        self.assertTrue(3 == c)
        self.assertFalse(5 == c)

        self.assertTrue(c == 3)
        self.assertFalse(c == 5)

        self.assertTrue(3 == e)
        self.assertTrue(7 == e)
        self.assertFalse(5 == e)

        self.assertTrue(e == 3)
        self.assertTrue(e == 7)
        self.assertFalse(e == 5)


        x = 'qwerty'        
        self.assertTrue(x == cf.eq('qwerty'))
        self.assertTrue(x == cf.eq('qwerty'  , exact=False))
        self.assertTrue(x == cf.eq('^qwerty$', exact=False))
        self.assertTrue(x == cf.eq('qwe'     , exact=False))
        self.assertTrue(x == cf.eq('qwe.*'   , exact=False))
        self.assertTrue(x == cf.eq('.*qwe'   , exact=False))
        self.assertTrue(x == cf.eq('.*rty'   , exact=False))
        self.assertTrue(x == cf.eq('.*rty$'  , exact=False))
        self.assertTrue(x == cf.eq('^.*rty$' , exact=False))
        self.assertTrue(x == cf.eq('qwerty'))
        self.assertTrue(x == cf.eq('qwerty'))

        self.assertTrue(x != cf.eq('QWERTY'))  
        self.assertTrue(x != cf.eq('QWERTY'  , exact=False))
        self.assertTrue(x != cf.eq('^QWERTY$', exact=False))
        self.assertTrue(x != cf.eq('QWE'     , exact=False))
        self.assertTrue(x != cf.eq('QWE.*'   , exact=False))
        self.assertTrue(x != cf.eq('.*QWE'   , exact=False))
        self.assertTrue(x != cf.eq('.*RTY'   , exact=False))
        self.assertTrue(x != cf.eq('rty$'    , exact=False))
        self.assertTrue(x != cf.eq('.*RTY$'  , exact=False))
        self.assertTrue(x != cf.eq('^.*RTY$' , exact=False))

#        self.assertTrue(x == cf.set([5, 'qwerty']))
#        self.assertTrue(x == cf.set([5, 'qwerty']  , exact=False))
#        self.assertTrue(x == cf.set([5, '^qwerty$'], exact=False))
#        self.assertTrue(x == cf.set([5, 'qwe']     , exact=False))
#        self.assertTrue(x == cf.set([5, 'qwe.*']   , exact=False))
#        self.assertTrue(x == cf.set([5, '.*qwe']   , exact=False))
#        self.assertTrue(x == cf.set([5, '.*rty']   , exact=False))
#        self.assertTrue(x == cf.set([5, '.*rty$']  , exact=False))
#        self.assertTrue(x == cf.set([5, '^.*rty$'] , exact=False))
    #--- End: def

#--- End: class

if __name__ == '__main__':
    print 'cf-python version:'     , cf.__version__
    print 'cf-python path:'        , os.path.abspath(cf.__file__)
    print ''
    unittest.main(verbosity=2)
