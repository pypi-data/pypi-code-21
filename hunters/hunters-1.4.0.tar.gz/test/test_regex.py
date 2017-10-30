# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/11
import re
import unittest
from unittest import TestCase

import requests

from hunters.constant import Regex

url = "http://www.baidu.com/da.js?xxxxxxxx"
clean_url = re.sub(r"\?.*", "", url)
print(clean_url, url)


class TestRegex(TestCase):
    def test_raw(self):
        assert Regex.RE_RAW_LINK.search("xxx.jpg")

    def decode_(self, url):
        r = requests.get(url)
        print(r.encoding)
        print(str(r._content, "utf-8"))

    def test_decode_url(self):
        self.decode_("http://spiderx.ks3-cn-beijing.ksyun.com/2017/09/http/money.qq.com/a/20170919/025636.htm")
        self.decode_("http://spiderx.ks3-cn-beijing.ksyun.com/2017/09/https/www.baidu.com")

    def test_encode(self):
        # r = urllib.urlopen('http://www.google.com.hk/')
        # print(r.readlines())
        str_ = "中文"
        str_gbk = str(str_.encode("gbk"), encoding="gbk")
        print(str_.encode("utf8"))
        print(str_gbk)

    def test_link(self):
        print(Regex.RE_LINK.findall('open("mylink-hello")'))


if __name__ == '__main__':
    unittest.main()
