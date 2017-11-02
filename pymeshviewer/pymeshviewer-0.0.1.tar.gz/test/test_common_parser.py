import unittest

from pymeshviewer.parser.node import parse_datetime


class CommonParserTest(unittest.TestCase):
    def test_datetime_parser(self):
        """
        Verify correct datetime parsing
        """
        teststring_1 = "2017-02-10T18:28:24+0000"
        parsed_string_1 = parse_datetime(teststring_1)
        self.assertEqual(parsed_string_1.day, 10)
        self.assertEqual(parsed_string_1.month, 2)
        self.assertEqual(parsed_string_1.year, 2017)
        self.assertEqual(parsed_string_1.hour, 18)
        self.assertEqual(parsed_string_1.minute, 28)
        self.assertEqual(parsed_string_1.second, 24)

        teststring_2 = "2017-10-21T00:33:52+0200"
        parsed_string_2 = parse_datetime(teststring_2)
        self.assertEqual(parsed_string_2.day, 21)
        self.assertEqual(parsed_string_2.month, 10)
        self.assertEqual(parsed_string_2.year, 2017)
        self.assertEqual(parsed_string_2.hour, 00)
        self.assertEqual(parsed_string_2.minute, 33)
        self.assertEqual(parsed_string_2.second, 52)
