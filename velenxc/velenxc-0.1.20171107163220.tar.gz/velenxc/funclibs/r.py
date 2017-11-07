# All of generic reduce functions are here
# Must to add unittest

import math
from functools import reduce

from .m import m_de_weight_of_list, m_timestamp_to_month, m_str_to_float, m_str_to_int, \
    m_cut_out_before_n
from .h import *


def r_count_of_list(seq):
    """
    :param seq: list
    :return: length of list
    """

    return len(seq)


def r_sum_with_average(seq):
    """ 求数值列表的平均值,返回列表
    如果len(seq) == 0, should return None, not 0
    """
    if len(seq) == 0:
        return [None]    # change 0 to None, by shniu 20170930

    average = sum(seq) / len(seq)
    return [float('%.2f' % average)]


def r_sum_str_0_divide_count_1_timestamp(seq):
    """
    average for seq[0]
    :param seq: seq[0] is list of digit, seq[1] list of timestamp
    :return: float
    """
    avg = None
    if seq and seq[0]:
        month_list = m_de_weight_of_list(m_timestamp_to_month(seq[1]))
        avg = sum(m_str_to_float(seq[0]))/len(month_list)

    return avg


def r_alipay_repayment_amount_month_avg(seq):
    """阿里支付还款月平均额"""
    avg = None
    if seq and seq[0]:
        amount_list = m_str_to_float(seq[0])
        month_list = m_de_weight_of_list(m_timestamp_to_month(seq[1]))
        avg = sum(amount_list)/len(month_list)

    return avg


def r_alipay_repayment_count_month_avg(seq):
    """阿里支付还款月平均次数"""
    avg = None
    if seq and seq[0]:
        month_list = m_de_weight_of_list(m_timestamp_to_month(seq[1]))
        avg = len(seq[0])/len(month_list)

    return avg


def r_alipay_repayment_difficulty(seq):
    """阿里支付还款是否有困难"""
    _count = None
    if seq:
        seq = m_timestamp_to_month(seq)
        counter = h_list_item_counter(seq)
        _count = counter.most_common(1)[0][1]

    return None if _count is None else _count > 2


def r_counter_result_avg(counter):
    """
    :param counter:  dict result of collections.Counter
    :return: float ,avg of count
    """
    if len(counter.values()):
        avg = sum(counter.values())/len(counter.values())
    else:
        avg = None

    return avg


def r_sum_of_list(seq):

    return sum(seq)


def r_night_hour_count(seq):
    """
    hour in [0-6], is night
    :param seq, hour(int) list
    :return: int, count of night hour
    """

    return len(list(filter(lambda h: h < 6, seq)))


def r_sets_distinct_len(seq):
    """ 去重后的个数 """
    return [len(set(seq))]


def r_compare_list_distinct_count(seq, count=1):
    """ 比较列表中去重数量是否等于count，
    :return int , 0 or 1
     """
    return int(len(set(seq)) == count)


def r_timedelta_days(seq):
    """ 计算两个日期datetime之间相差天数 """
    if None in seq or len(seq) < 2:
        return [None]

    return reduce(lambda x, y: (x - y).days, seq)


def r_counter_entropy(counter):
    """
    :param counter:  dict result of collections.Counter
    :return: float, entropy for counter.values()
    """
    total = sum(counter.values())
    pi_list = [0, ]
    if total:
        pi_list = [v*1.0/total * math.log(v*1.0/total, 2) for v in counter.values()]
    return abs(reduce(lambda p1, p2: p1+p2, pi_list))


def r_month_called_proportion(counter):
    """
    :param counter:  dict result of collections.Counter, '1': dialing, '2': called
    :return: float ,avg of count
    """

    if sum(counter.values()):
        proportion = counter['2']*1.0/sum(counter.values())
    else:
        proportion = None

    return proportion


def r_month_dialing_proportion(counter):
    """
    :param counter:  dict result of collections.Counter, '1': dialing, '2': called
    :return: float ,avg of count
    """
    if sum(counter.values()):
        proportion = counter['1']*1.0/sum(counter.values())
    else:
        proportion = None

    return proportion


def r_month_receive_msg_proportion(counter):
    """
    :param counter:  dict result of collections.Counter, '1': send message, '2': receive message
    :return: float ,avg of count
    """

    if sum(counter.values()):
        proportion = counter['2']*1.0/sum(counter.values())
    else:
        proportion = None

    return proportion


def r_month_send_msg_proportion(counter):
    """
    :param counter:  dict result of collections.Counter, '1': send message, '2': receive message
    :return: float ,avg of count
    """
    if sum(counter.values()):
        proportion = counter['1']*1.0/sum(counter.values())
    else:
        proportion = None

    return proportion


def r_month_short_call_avg(seq):
    """月短时间通话平均次数"""
    avg = None
    if seq and seq[0]:
        call_time_list = m_str_to_int(seq[0])
        month_list = m_de_weight_of_list(m_cut_out_before_n(seq[1]))
        avg = len(list(filter(lambda s: s < 30, call_time_list)))/len(month_list)

    return avg


def r_counter_value_more_than_n_count(counter, n=5):
    """
    :param counter:  dict result of collections.Counter
    :param n: compare number
    :return: float ,avg of count
    """

    return len(list(filter(lambda v: v > n, counter.values())))


def r_two_name_whether_equal(seq):
    """ check whether two name is equal, maybe some char will be replace by * in name
    :param seq : list, seq[0] is name1, seq[1] is name2
    :return: boolean
    """
    if len(seq) < 2:
        return False

    seq = list(map(lambda n: n.replace('*', ''), seq))
    return seq[0] in seq[1] or seq[1] in seq[0]





