import unittest

from velenxc.funclibs.m import *


class MStrToFloatCase(unittest.TestCase):
    """test m.m_str_to_float function"""
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_str_to_float([]))

    def test_input_str_list_return_float_list(self):
        self.assertEqual([1, 2.0], m_str_to_float(['1', '2.0']))

    def test_input_str_list_contains_non_numeric(self):
        self.assertEqual([1, 'a'], m_str_to_float(['1', 'a']))


class MDeWeightOfListCase(unittest.TestCase):
    """test m.m_de_weight_of_list function"""

    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_de_weight_of_list([]))

    def test_input_list_return_de_weight_list(self):
        self.assertEqual([1, 2], m_de_weight_of_list([1, 2, 2]))


class MTimestampToMonthCase(unittest.TestCase):
    """test m.m_timestamp_to_month function
    """
    def test_input_0_list_return_0_list(self):
        self.assertEqual([1, 1], m_timestamp_to_month([0, 0]))

    def test_input_str_timestamp_list_return_month_list(self):
        self.assertEqual([9, 9], m_timestamp_to_month(['1505730909', '1505730929']))

    def test_input_int_timestamp_list_return_month_list(self):
        self.assertEqual([9, 9], m_timestamp_to_month([1505730929, 1505730909]))


class MTimestampToHourCase(unittest.TestCase):
    """test m.m_timestamp_to_hour function
    """
    def test_input_0_list_return_0_list(self):
        # utc +8
        self.assertEqual([8, 8], m_timestamp_to_hour([0, 0]))

    def test_input_str_timestamp_list_return_month_list(self):
        self.assertEqual([18, 18], m_timestamp_to_hour(['1505730909', '1505730929']))

    def test_input_int_timestamp_list_return_month_list(self):
        self.assertEqual([18, 18], m_timestamp_to_hour([1505730929, 1505730909]))


class MCutOutBeforeNCase(unittest.TestCase):
    """test m.m_cut_out_before_n function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_cut_out_before_n([]))

    def test_input_str_datetime_list_return_month_list(self):
        self.assertEqual(['2016-10', '2016-10'],
                         m_cut_out_before_n(['2016-10-01 00:17', '2016-10-08 00:17:17 ']))


class MOneListToNCase(unittest.TestCase):
    """test m.m_one_list_to_n function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_one_list_to_n([], 2))

    def test_input_list_return_big_list_contain_sub_list(self):
        self.assertEqual([(1, 2), (3, None)], m_one_list_to_n([1, 2, 3], 2))


class MTransformByKeyCase(unittest.TestCase):
    """test m.m_transform_by_key function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_transform_by_key([]))

    def test_input_tuple_list_return_max_value_list(self):
        self.assertEqual([3000, 3000], m_transform_by_key([('a', 2000), ('b', 3000), ('a', 3000)]))


class MDividedByCase(unittest.TestCase):
    """test m.m_divided_by function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_divided_by([], 1))

    def test_input_digit_list_return_divided_list(self):
        self.assertEqual([0.5, 1.0, 1.5, 2.0], m_divided_by([1, 2, 3, 4], 2))


class MCutOutLastNCase(unittest.TestCase):
    """test m.m_cut_out_last_n function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_cut_out_last_n([], 1))

    def test_input_str_list_return_cut_list(self):
        self.assertEqual(['34', '78'], m_cut_out_last_n(['1234', '5678'], 2))


class MDateStrToDatetimeCase(unittest.TestCase):
    """test m.m_date_str_to_datetime function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_date_str_to_datetime([]))

    def test_input_null_string_list_return_none(self):
        self.assertEqual([None], m_date_str_to_datetime(['']))

    def test_input_str_date_list_return_datetime_list(self):
        self.assertIsInstance(m_date_str_to_datetime(['2017-09-19', '2017-09-20'])[0], datetime)
        self.assertIsInstance(m_date_str_to_datetime(['2017-09-19', '2017-09-20'])[1], datetime)

    def test_input_str_datetime_list_return_datetime_list(self):
        self.assertIsInstance(m_date_str_to_datetime(['2017-09-19 17:17:08', '2017-09-20 17:17:08'])[0], datetime)
        self.assertIsInstance(m_date_str_to_datetime(['2017-09-19 17:17:08', '2017-09-20 17:17:08'])[1], datetime)

    def test_input_error_datetime_list_return_datetime_list(self):
        self.assertIsInstance(m_date_str_to_datetime(['-2017-09-19 17:17:08', ])[0], datetime)

    def test_input_compact_date_list_return_datetime_list(self):
        self.assertIsInstance(m_date_str_to_datetime(['20170919', ])[0], datetime)

    def test_input_compact_datetime_list_return_datetime_list(self):
        self.assertIsInstance(m_date_str_to_datetime(['20170919171708', ])[0], datetime)

    def test_input_timestamp_list_return_datetime_list(self):
        self.assertIsInstance(m_date_str_to_datetime([time.time(), ])[0], datetime)


class MStrToIntCase(unittest.TestCase):
    """test m.m_str_to_int function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_str_to_int([]))

    def test_input_string_list_return_int_list(self):
        self.assertEqual([1, 2, 3], m_str_to_int(['1.0', '2', '3']))


class MTimestampToHourSlotCase(unittest.TestCase):
    """test m.m_timestamp_to_hour_slot function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_timestamp_to_hour_slot([]))

    def test_input_timestamp_list_return_hour_list(self):
        self.assertEqual(['2', '2'], m_timestamp_to_hour_slot([1505730929, 1505730920]))


class MToValueCase(unittest.TestCase):
    """test m.m_to_value function
    """
    def test_input_null_list_return_null_list(self):
        self.assertEqual([], m_to_value([], 8))

    def test_input_value_list_return_replace_value_list(self):
        self.assertEqual([8, 8], m_to_value([1, 2], 8))
