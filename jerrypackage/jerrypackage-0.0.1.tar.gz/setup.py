# coding: utf-8

from setuptools import setup

setup(
    name='jerrypackage',
    version='0.0.1',
    author='jerrychy',
    author_email='jerrychen@ustc.edu',
    url='https://www.zhihu.com/people/jerrychen-57/activities',
    description='Tools for daily use',
    packages=['jerrypackage'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'jujube=jerrypackage:jujube',
            'pill=jerrypackage:pill'
        ]
    }
)