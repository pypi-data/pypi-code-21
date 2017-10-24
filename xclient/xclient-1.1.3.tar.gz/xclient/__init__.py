#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

__version__ = '1.1.3'
py_version = sys.version_info
__all__ = ('register_xclient', 'register_xclient2', 'register_xclient3')


def register_xclient(options, loop=None):
    """
    注册交互工具
    :param options: 配置项
    :param loop: for python3
    :return:
    """
    if py_version >= (3, 5):
        return register_xclient3(options, loop)
    else:
        return register_xclient2(options)


def register_xclient3(options, loop):
    """
    注册python3交互工具
    :param options:
    :param loop:
    :return:
    """

    if not py_version >= (3, 5):
        raise RuntimeError('use client3 should python >= 3.5')

    from .client3 import TradeClient3

    configs = _parse_options(options)
    return TradeClient3(*configs, loop=loop)


def register_xclient2(options):
    """
    注册xclient　python2版本
    :param options:
    :return:
    """
    from .client2 import TradeClient2

    configs = _parse_options(options)
    return TradeClient2(*configs)


def _parse_options(options):
    """ 解析xclient配置　"""
    api_host = options.get('API_HOST')
    api_key = options.get("API_KEY")
    api_secret = options.get("API_SECRET")
    api_version = options.get("API_VERSION")

    configs = (api_key, api_secret, api_host, api_version)
    if not all(configs):
        raise KeyError('API_HOST, API_KEY, API_SECRET, API_VERSION is required')
    return configs
