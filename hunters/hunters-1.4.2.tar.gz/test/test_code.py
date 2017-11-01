# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/8
import logging

from hunters.browser import MiniBrowser
from hunters.constant import Regex
from hunters.defaults import DefaultFilter

print("window.scrollBy({}, {})".format(10, 10))

filter = DefaultFilter()
FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(module)s[%(lineno)d]-%(message)s"

logging.basicConfig(level=logging.INFO, format=FORMAT)


def lookup(func):
    print(func("url"))
    print(func("url"))
    print(func("url"))
    print(func("url"))


lookup(filter.url_raw_filter)
lookup(filter.url_duplicate_filter)
lookup(filter.url_schema_filter)

t = MiniBrowser()
# r = t.get("https://video.so.com/")
r = t.get("https://zhidao.baidu.com/")

m = Regex.RE_MATA_CHARSET.search(str(r.content))

print(m.group(1))

print(r.text)
