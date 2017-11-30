#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name = "zuanfeng",
    version = "0.0.3",
    keywords = ("pip", "zuanfeng", "xiaozuanfeng", "zuanfengxiaojiang", "zf"),
    description = "zuanfeng captain sdk",
    long_description = "zuanfeng captain sdk for python",
    license = "MIT Licence",

    url = "http://lazybios.com",
    author = "lazybios",
    author_email = "lazybios@gmail.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['requests']
)
