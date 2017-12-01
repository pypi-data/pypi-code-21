# -*- coding: utf-8 -*-

import functools

from log import logger


def safe_call(func, *args, **kwargs):
    """
    安全调用
    """
    try:
        return func(*args, **kwargs)
    except Exception, e:
        logger.error('exc occur. e: %s, func: %s', e, func, exc_info=True)
        # 调用方可以通过 isinstance(e, BaseException) 来判断是否发生了异常
        return e


def safe_func(func):
    """
    把函数变为安全的
    """
    @functools.wraps(func)
    def func_wrapper(*args, **kwargs):
        return safe_call(func, *args, **kwargs)
    return func_wrapper


def ip_bin_to_str(ip_num):
    """
    转换ip格式，从bin转为str
    :param ip_num:
    :return:
    """
    import socket
    return socket.inet_ntoa(ip_num)


def ip_str_to_bin(ip_str):
    """
    转化ip格式，从str转为bin
    :param ip_str:
    :return:
    """
    import socket
    return socket.inet_aton(ip_str)


def import_module_or_string(src):
    """
    按照模块导入或者字符串导入
    :param src:
    :return:
    """
    from config import import_string
    return import_string(src) if isinstance(src, (str, unicode)) else src
