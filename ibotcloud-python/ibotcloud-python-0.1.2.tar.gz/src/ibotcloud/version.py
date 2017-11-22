# -*- coding: utf-8 -*-

"""
程序包的版本信息
"""

from pkg_resources import get_distribution

__all__ = ['__version__']

__version__ = get_distribution('ibotcloud-python').version
