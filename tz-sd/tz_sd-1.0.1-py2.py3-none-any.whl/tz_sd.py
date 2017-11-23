#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/11/18 18:52
# @Author  : 强子
# @File    : tz_sd.py
# @Software: PyCharm

'''
    该工具主要用于爬虫开发过程中把请求中的参数信息以及头信息转换成dict
'''

def tz_sd(string):
    dt = {}
    tmp_list = string.split('\n')
    for i in tmp_list:
        if i:
            t_list = i.split(':')
            dt[t_list[0].replace(' ','').replace('\t','')] = t_list[1]
    return dt