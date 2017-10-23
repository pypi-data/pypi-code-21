
import unittest

from Core.DatetimePlus import DatetimePlus


class TestService(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDateFormat(self):
        self.assertEqual(DatetimePlus.get_nowdate_to_str(), '2017-07-17')



    def testDatetimeToStr(self):
        curTime = DatetimePlus.get_now_datetime()
        self.assertEqual(DatetimePlus.datetime_to_str(curTime), '2017-07-14 15:25:40')

