# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/22
import threading

from hunters.utils import ForeverThreadPool

fx = ForeverThreadPool(1)


def test():
    print("MyPrint->" + threading.currentThread().name)


fx.submit(target=test, args=())
print("Hello")
