#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : .
* file   : setup.py
* time   : 2017/10/27
'''
#--------------------#
from setuptools import setup, find_packages
#----------#
from api_cli.acts import config
#--------------------#

#--------------------#
setup(
    name = 'api-cli',
    version = config.version,
    description = "A tiny and smart cli tool for managing api-frame based on Python.",
    keywords = 'api-cli api-frame api frame cli python',
    author = 'dzlua',
    author_email = '505544956@qq.com',
    url = 'https://gitee.com/dzlua/api-cli.git',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = True,
    test_suite = 'tests',
    entry_points = {
        'console_scripts': [
            'api-cli = api_cli.main:cli'
        ]
    },
    install_requires = [
        'click',
        'configparser'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
)
#--------------------#
