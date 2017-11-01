# -*- coding:utf-8 -*-
import datetime
from unittest import TestCase

# Created by qinwei on 2017/8/25
from hunters.utils import get_real_url


def mtime():
    return datetime.datetime.now().microsecond


class TestGet_real_url(TestCase):
    def test_get_real_url(self):
        start = mtime()
        get_real_url(base_url=None, relate_url="http://baidu.com")
        print("%s ms" % (mtime() - start))
        print(get_real_url("http://baidu.com", "//baidu.com/xxxx.png"))
        print(get_real_url("http://baidu.com", ""))
