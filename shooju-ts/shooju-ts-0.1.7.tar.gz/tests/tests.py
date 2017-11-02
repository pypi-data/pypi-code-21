# coding=UTF-8
from __future__ import print_function, unicode_literals
import six
from six.moves import range, zip
import numpy as np
if six.PY2:
    import unittest2 as unittest
else:
    import unittest

import sjts

try:
    from blist import blist
except ImportError:
    blist = None

class SJTSTests(unittest.TestCase):
    def test_simple(self):
        encoded = sjts.encode({'success': False})
        self.assertEqual(encoded, b'SJTS\x11\x00\x00\x00{"success":false}')
    def test_simpleException1(self):
        with self.assertRaises(sjts.ParseException):
            sjts.encode(True)
    def test_simpleException3(self):
        with self.assertRaises(sjts.ParseException):
            sjts.encode({'success': False, 'series': []})
    def test_big(self):
        obj = {'success': False, 'big_value': [{'abcdef': 12345.67890}] * 10000}
        encoded = sjts.encode(obj)
        self.assertEqual(obj, sjts.decode(encoded))
    def test_encodeResponses(self):
        obj = {'success': True, 'series' : [1,2]}
        encoded = sjts.encode(obj)
        self.assertEqual(encoded, b'SJTS\x1b\x00\x00\x00{"series":2,"success":true}\x01\x00\x00\x001\x01\x00\x00\x002')
        self.assertEqual(sjts.decode(encoded), obj)
    def test_encodeBigReponse(self):
        obj = {'success': True, 'series': [{'big_value': [{'abcdef': 12345.67890}] * 10000}]}
        encoded = sjts.encode(obj)
        self.assertEqual(obj, sjts.decode(encoded))
    def test_encodePoint(self):
        obj = {'success': True, 'series' : [{'points':[(1,1234.5678)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(encoded[39:-22], b'{"points":1}\x10\x00')
        self.assertEqual(obj, sjts.decode(encoded))
    def test_encodePointAsList(self):
        obj = {'success': True, 'series' : [{'points':[[1,1234.5678]]}]}
        objTuple = {'success': True, 'series' : [{'points':[(1,1234.5678)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(objTuple, sjts.decode(encoded))
    def test_encodePoints2(self):
        obj = {'success': True, 'series' : [{'points':[(1,1234.5678),(2,33.2)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(encoded[39:-34], b'{"points":2}\x1c\x00')
        self.assertEqual(obj, sjts.decode(encoded))
    def test_encodePoints2Backward(self):
        obj = {'success': True, 'series' : [{'points':[(2,1234.5678),(1,33.2)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(encoded[39:-34], b'{"points":2}\x1c\x00')
        self.assertEqual(obj, sjts.decode(encoded))
    def test_encodeDecode(self):
        obj = {'success': True,'series': [{'points': [(a, 12.345) for a in range(100)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(obj, sjts.decode(encoded))
    def test_encodeDecodeSkippedPonts(self):
        obj = {'success': True, 'series' : [{'points':[(1,1234.5678),(2,33.2),(10, 123.445),(20, 323.33), (50, 323.1)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(obj, sjts.decode(encoded))
    def test_emptyPoints(self):
        obj = {'success':True,'series':[{'points':[]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(obj, sjts.decode(encoded))
    def test_emptyPointWithInteger(self):
        obj = {'success':True,'series':[{'points':[[1,2]]}]}
        objFloat = {'success':True,'series':[{'points':[(1,2.0)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(objFloat, sjts.decode(encoded))
    def test_emptyPointWithFloat(self):
        obj = {'success':True,'series':[{'points':[[1.2345,2.0]]}]}
        objFloat = {'success':True,'series':[{'points':[(1,2.0)]}]}
        encoded = sjts.encode(obj)
        self.assertEqual(objFloat, sjts.decode(encoded))
    def test_malloc_memory_corruption(self):
        obj = {'series': [
            {'series_id': u'G_LA_43\\Output\\Ammonia',
             'points': [(1293840000000, 0.132), (1325376000000, 0.0), (1356998400000, 0.0), (1388534400000, 0.0),
                        (1420070400000, 0.132), (1451606400000, 0.132), (1483228800000, 0.132), (1514764800000, 0.132),
                        (1546300800000, 0.132), (1577836800000, 0.132), (1609459200000, 0.132), (1640995200000, 0.132),
                        (1672531200000, 0.132), (1704067200000, 0.132), (1735689600000, 0.132),
                        (1767225600000, 0.132)]},
            {'series_id': u'Gasification\\gasification_plants\\G_NA_72'},
            {'series_id': u'Gasification\\gasification_plant_series\\G_AS_997\\Input\\Natural Gas',
             'points': [(1293840000000, 36.358), (1325376000000, 36.358), (1356998400000, 36.358),
                        (1388534400000, 36.358), (1420070400000, 36.358), (1451606400000, 36.358),
                        (1483228800000, 36.358), (1514764800000, 36.358), (1546300800000, 36.358),
                        (1577836800000, 36.358), (1609459200000, 36.358), (1640995200000, 36.358),
                        (1672531200000, 36.358), (1704067200000, 36.358), (1735689600000, 36.358),
                        (1767225600000, 36.358)]}
        ], 'success': True}
        encoded = sjts.encode(obj)
        self.assertEqual(obj, sjts.decode(encoded))
    def test_series_jobs(self):
        series = {'points': [(1,1,4),(2,2,5),(4,3,6),(10,1,1)]}
        decode_data = sjts.dumps_series(series, True, False)
        self.assertEqual(series, sjts.loads_series(decode_data))
    def test_series_timestamps(self):
        series = {'points': [(1,1,4),(2,2,5),(4,3,6),(10,1,1)]}
        decode_data = sjts.dumps_series(series, False, True)
        # loads_series returns the same what dump_series got as parameter
        self.assertEqual(series, sjts.loads_series(decode_data))
    def test_series_job_timestamps(self):
        series = {'points': [(1,1,4,10),(2,2,5,11),(4,3,6,12),(10,1,1,14)]}
        decode_data = sjts.dumps_series(series, True, True)
        self.assertEqual(series, sjts.loads_series(decode_data))
    def test_with_sjts_key(self):
        with self.assertRaises(sjts.ParseException):
            sjts.encode({'success': True, 'sjts': {}})
    def test_with_sjts_key2(self):
        with self.assertRaises(sjts.ParseException):
            sjts.dumps_series({'success': True, 'sjts': {}})

    def test_crash_regression(self):
        series = {'points': [(1,1,),(2,2),(4,3),(10,1,)]}
        sjts.dumps_series(series)
    def test_job_timestamps(self):
        series = {'success': True, 'series': [{'points': [(1,1,4,10),(2,2,5,11),(4,3,6,12),(10,1,1,14)]}]}
        decode_data = sjts.dumps(series, True, True)
        self.assertEqual(series, sjts.loads(decode_data))
    def test_numpy(self):
        points = [(1,2), (3,4), (5,6)]
        def obj(points): return {'success': True, 'series': [{'points' : points}]}
        decode_data = sjts.dumps(obj(np.array(points)))
        self.assertEqual(obj(points), sjts.loads(decode_data))
    def test_numpy_series(self):
        points = [(1,2), (3,4), (5,6)]
        obj = {'success': True, 'series': [{'points' : points}]}
        decode_data = sjts.dumps_series({'points': np.array(points)})
        self.assertEqual(obj['series'][0], sjts.loads_series(decode_data))
    def test_numpy_loads(self):
        obj = {'success': True, 'series': [{'points' : np.array([(1,2), (3,4), (5,6)])}]}
        decode_data = sjts.dumps(obj)
        obj2 = sjts.loads(decode_data, True)
        def to_list(obj): obj['series'][0]['points'] = obj['series'][0]['points'].tolist()
        to_list(obj)
        to_list(obj2)
        self.assertEqual(obj, obj2)
    def test_numpy_loads_series(self):
        points = np.array([(1,2), (3,4), (5,6)])
        obj = {'points' : points}
        decode_data = sjts.dumps_series({'points': points})
        obj2 = sjts.loads_series(decode_data, True)
        def to_list(obj): obj['points'] = obj['points'].tolist()
        to_list(obj)
        to_list(obj2)
        self.assertEqual(obj, obj2)
    def test_without_success(self):
        try:
            encoded = sjts.encode({})
        except sjts.ParseException:
            self.fail("should encode without success key!")

if __name__ == "__main__":
    unittest.main()

"""
# Use this to look for memory leaks
if __name__ == '__main__':
    from guppy import hpy
    hp = hpy()
    hp.setrelheap()
    while True:
        try:
            unittest.main()
        except SystemExit:
            pass
        heap = hp.heapu()
        print(heap)
"""
