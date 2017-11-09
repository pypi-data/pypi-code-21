#!/usr/bin/python3

from setuptools import setup

PACKAGE = 'blogrunner'
NAME = 'blogrunner'
DESCRIPTION = 'This module create the platform for the Linuxer'
AUTHOR = 'GMFTBY'
AUTHOR_EMAIL = '18811371908@163.com'
URL = 'https://github.com/gmftbyGMFTBY'
VERSION = 1.1

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url=URL,
    packages = ['blogrunner' , 'blogrunner.AI' , 'blogrunner.CSDN' , 'blogrunner.MYSQL' , 'blogrunner.Bottle' , 'blogrunner.dist'],
    install_requires = ['requests' ,'bs4']
)
