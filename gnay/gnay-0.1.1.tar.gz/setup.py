#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
"""
打包的用的setup必须引入，
"""
VERSION = '0.1.1'

setup(
    name = 'gnay',
    version=VERSION,
    description='desc me',
    keywords = 'me',
    author = 'yang',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts':[
                        'me = me.me:main'
        ]
    }
)
