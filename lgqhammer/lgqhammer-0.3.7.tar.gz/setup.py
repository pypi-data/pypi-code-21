# -*- coding=utf-8 -*-

from distutils.core import setup

setup(
    name = 'lgqhammer',
    version = '0.3.7',

    requires = ['pymysql', 'thrift'],

    packages = ['hammer', 'hammer.pymysqlpool', 'hbase'],
    scripts = ['./kill_port'],

    url = 'http://awolfly9.com/',
    license = 'MIT Licence',
    author = 'lgq',
    author_email = 'awolfly9@gmail.com',

    description = 'lgq hammer',
)
