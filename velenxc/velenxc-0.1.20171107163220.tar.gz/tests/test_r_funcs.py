import unittest
from datetime import datetime

from velenxc.funclibs.r import *


class RCountOfListCase(unittest.TestCase):
    """test r.r_count_of_list function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(0, r_count_of_list([]))

    def test_input_list_return_length_of_list(self):
        self.assertEqual(2, r_count_of_list([1, 2]))


class RSumWithAverageCase(unittest.TestCase):
    """test r.r_sum_with_average function
    """
    def test_input_null_list_return_None(self):
        self.assertEqual([None], r_sum_with_average([]))

    def test_input_digit_list_return_average(self):
        self.assertEqual([1.5], r_sum_with_average([1, 2]))


class RSumStr0DivideCount1TimestampCase(unittest.TestCase):
    """test r.r_sum_str_0_divide_count_1_timestamp function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(None, r_sum_str_0_divide_count_1_timestamp([]))

    def test_input_str_and_timestamp_list_return_average(self):
        self.assertEqual(3.0, r_sum_str_0_divide_count_1_timestamp([[1, 2], [1505730929, 1505730922]]))


class RAlipayRepaymentAmountMonthAvgCase(unittest.TestCase):
    """test r.r_alipay_repayment_amount_month_avg function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(None, r_alipay_repayment_amount_month_avg([]))

    def test_input_amount_and_timestamp_list_return_average(self):
        self.assertEqual(3.0, r_alipay_repayment_amount_month_avg([['1', '2'], [1505730929, 1505730920]]))


class RAlipayRepaymentCountMonthAvgCase(unittest.TestCase):
    """test r.r_alipay_repayment_count_month_avg function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(None, r_alipay_repayment_count_month_avg([]))

    def test_input_amount_and_timestamp_list_return_average(self):
        self.assertEqual(2.0, r_alipay_repayment_count_month_avg([['1', '3'], [1505730929, 1505730920]]))


class RAlipayRepaymentDifficultyCase(unittest.TestCase):
    """test r.r_alipay_repayment_difficulty function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(None, r_alipay_repayment_difficulty([]))

    def test_input_timestamp_list_return_false(self):
        self.assertEqual(False, r_alipay_repayment_difficulty([1505730929, 1505730920]))

    def test_input_timestamp_list_return_true(self):
        self.assertEqual(True, r_alipay_repayment_difficulty([1505730929, 1505730920, 1505730220]))


class RCounterResultAvgCase(unittest.TestCase):
    """test r.r_counter_result_avg function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(None, r_counter_result_avg(Counter([])))

    def test_input_item_list_return_avg(self):
        self.assertEqual(1.5, r_counter_result_avg(Counter([1, 2, 1])))


class RSumOfListCase(unittest.TestCase):
    """test r.r_sum_of_list function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(0, r_sum_of_list([]))

    def test_input_item_list_return_sum(self):
        self.assertEqual(6, r_sum_of_list([1, 2, 3]))


class RNightHourCountCase(unittest.TestCase):
    """test r.r_night_hour_count function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(0, r_night_hour_count([]))

    def test_input_item_list_return_night_hour_count(self):
        self.assertEqual(3, r_night_hour_count([1, 2, 3, 8]))


class RSetsDistinctLenCase(unittest.TestCase):
    """test r.r_sets_distinct_len function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual([0], r_sets_distinct_len([]))

    def test_input_item_list_return_list_count(self):
        self.assertEqual([3], r_sets_distinct_len([1, 2, 3, 3]))


class RCompareListDistinctCountCase(unittest.TestCase):
    """test r.r_compare_list_distinct_count function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(0, r_compare_list_distinct_count([]))

    def test_input_item_list_return_true(self):
        self.assertEqual(1, r_compare_list_distinct_count([1, 2, 3, 3], 3))


class RTimedeltaDaysCase(unittest.TestCase):
    """test r.r_timedelta_days function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual([None], r_timedelta_days([]))

    def test_input_datetime_list_timedelta_days(self):
        self.assertEqual(2, r_timedelta_days([datetime(2017, 6, 22), datetime(2017, 6, 20)]))


class RCounterEntropyCase(unittest.TestCase):
    """test r.r_counter_entropy function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(0, r_counter_entropy(Counter([])))

    def test_input_counter_return_float(self):
        self.assertIsInstance(r_counter_entropy(Counter([1, 2, 2])), float)


class RMonthCalledProportionCase(unittest.TestCase):
    """test r.r_month_called_proportion function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(None, r_month_called_proportion(Counter([])))

    def test_input_counter_return_proportion(self):
        self.assertEqual(0.5, r_month_called_proportion(Counter({'1': 5, '2': 5})))


class RMonthDialingProportionCase(unittest.TestCase):
    """test r.r_month_dialing_proportion function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(None, r_month_dialing_proportion(Counter([])))

    def test_input_counter_return_proportion(self):
        self.assertEqual(0.4, r_month_dialing_proportion(Counter({'1': 4, '2': 6})))


class RMonthReceiveMsgProportionCase(unittest.TestCase):
    """test r.r_month_receive_msg_proportion function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(None, r_month_receive_msg_proportion(Counter([])))

    def test_input_counter_return_proportion(self):
        self.assertEqual(0.6, r_month_receive_msg_proportion(Counter({'1': 4, '2': 6})))


class RMonthSendMsgProportionCase(unittest.TestCase):
    """test r.r_month_send_msg_proportion function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(None, r_month_send_msg_proportion(Counter([])))

    def test_input_counter_return_proportion(self):
        self.assertEqual(0.4, r_month_send_msg_proportion(Counter({'1': 4, '2': 6})))


class RMonthShortCallAvgCase(unittest.TestCase):
    """test r.r_month_short_call_avg function
    """
    def test_input_null_list_return_false(self):
        self.assertEqual(None, r_month_short_call_avg([]))

    def test_input_list_return_proportion(self):
        self.assertEqual(1, r_month_short_call_avg([[1, 20, 50],
                                                      ['2016-10-01 00:17:17', '2016-11-01 00:19:17',
                                                       '2016-10-02 00:17:17']]))


class RCounterValueMoreThanNCountCase(unittest.TestCase):
    """test r.r_counter_value_more_than_n_count function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(0, r_counter_value_more_than_n_count(Counter([])))

    def test_input_counter_return_proportion(self):
        self.assertEqual(1, r_counter_value_more_than_n_count(Counter({'1': 4, '2': 6}), 5))


class RTowNameWhetherEqualCase(unittest.TestCase):
    """test r.r_two_name_whether_equal function
    """
    def test_input_null_list_return_0(self):
        self.assertEqual(False, r_two_name_whether_equal([]))

    def test_input_part_name_return_true(self):
        self.assertEqual(True, r_two_name_whether_equal(['牛二*', '牛二蛋']))

    def test_input_full_name_return_true(self):
        self.assertEqual(True, r_two_name_whether_equal(['牛二蛋', '牛二蛋']))

