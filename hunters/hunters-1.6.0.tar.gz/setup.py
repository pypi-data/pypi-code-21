# -*- coding:utf-8 -*-
# Created by qinwei on 2017/8/9
from setuptools import setup, find_packages

setup(
    name='hunters',
    version='1.6.0',
    description="A spider automation framework, provide uniform API to use selenium and requests",
    author='Qin Wei (ChineseTiger)',
    long_description='Hunters provide a uniform API to call Selenium and requests for common crawlers and headless crawlers',
    author_email='imqinwei@qq.com',
    url="https://github.com/LoginQin/hunters",
    license='Apache License, Version 2.0',
    packages=find_packages(),
    keywords='hunters spider headless crawlers screenshot',
    install_requires=['requests', 'lxml', 'cssselect', 'selenium==3.3.1', 'redis', 'cachetools']
)
