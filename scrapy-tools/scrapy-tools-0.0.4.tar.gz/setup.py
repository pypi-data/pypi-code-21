# -*- coding:utf8 -*-
from setuptools import setup, find_packages

setup(
    name="scrapy-tools",
    version="0.0.4",
    description="tools for scrapy_tools, consist of middlewares",
    author="jack.cong",
    author_email='congshuanglong@126.com',
    url="http://blog.livedrof.com",
    license="LGPL",
    packages=find_packages(exclude=['test']),
    scripts=["scrapy_tools/storage/rabbitmq.py"],
    py_modules=['scrapy_tools', 'scrapy_tools.storage', 'scrapy_tools.storage.rabbitmq']
)
