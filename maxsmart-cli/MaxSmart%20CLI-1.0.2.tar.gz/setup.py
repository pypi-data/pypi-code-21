# This Python file uses the following encoding: utf-8

from setuptools import setup

setup(
    name='MaxSmart CLI',
    version='1.0.2',
    url='https://github.com/phylor/maxcli',
    author='Serge Hänni',
    author_email='serge@nyi.ch',
    py_modules=[
        'maxcli',
        'maxsmart_http',
        'explorer',
    ],
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        maxcli=maxcli:cli
    ''',
)
