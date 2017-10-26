#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午4:53
# @Author  : Hou Rong
# @Site    : 
# @File    : System.py
# @Software: PyCharm
import socket


def get_local_ip():
    res = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        res = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    return res
