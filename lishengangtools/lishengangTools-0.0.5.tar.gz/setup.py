#/usr/bin/env python3
#-*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='lishengangTools',
    version='0.0.5',
    description='personal python package of lishengang',
    long_description=open('README.rst').read(),
	#install_requires=['Twisted>=13.1.0',]#需要依赖的包
    author='lishengang',
    author_email='cszy2013@163.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://www.github.com',
    classifiers=[],
)