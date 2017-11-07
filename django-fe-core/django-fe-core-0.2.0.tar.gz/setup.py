# -*- coding:utf-8 -*-
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-fe-core',
    version='0.2.0',
    description='',
    long_description=README,
    url='https://github.com/fernandoe/django-fe-core',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    author='Fernando Espíndola',
    author_email='fer.esp@gmail.com',
)
