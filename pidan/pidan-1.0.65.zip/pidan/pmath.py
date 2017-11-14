# -*- coding: utf-8 -*-
__author__ = 'gang'

import random,time

def create_new_id():
    '''根据时间撮创建唯一编号，方式：unix时间撮（单位毫秒） + 3位随机数'''
    return int(time.time()*1000*1000) + random.randint(100,999)


if __name__ == '__main__':
    for i in range(1,99999999):
        print(create_new_id())



