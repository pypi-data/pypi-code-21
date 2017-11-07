
import string
import datetime
import random

from .const import ConstInstance


class RandomGenerator(object):
    """ 随机数生成器 """

    @classmethod
    def get_random_digits(cls, seed_cnt=6):
        """ 获取指定位数``seed_cnt``的随机数字字符串 """
        return ConstInstance.BLANK_CHAR.join(random.sample(string.digits, seed_cnt))

    @classmethod
    def get_identity_with_datetime(cls, prefix=None, seed_cnt=6):
        """ 根据当前时间种子随机生成唯一标识, 精确到微秒, 在最后追加 ``seed_cnt`` 位随机数字

        >>> from velenxc.random import RandomGenerator
        >>> RandomGenerator.get_identity_with_datetime(prefix='FC')
        FC20170913095236030964587983
        """
        datetime_now_string = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        if prefix is None:
            prefix = ''

        seed_string = '' if seed_cnt <= 0 else cls.get_random_digits(seed_cnt=seed_cnt)

        return '{}{}{}'.format(prefix, datetime_now_string, seed_string)
