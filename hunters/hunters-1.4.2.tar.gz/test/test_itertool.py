# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/11
import itertools

from hunters.browser import MiniBrowser, Browser

c = itertools.count()
t = MiniBrowser()

print(issubclass(t.__class__, Browser))
