# -*- coding: utf-8 -*-
# 异步调用模块，直接调用装饰器
import functools
import threading

def async(func):
    '''异步执行装饰器'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper

def async_exec(func,*args,**kwargs):
    '''异步调用指定的函数'''
    my_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    my_thread.setDaemon(True)
    my_thread.start()
    return my_thread

