# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from setuptools import setup, find_packages

from django_boxberry import __version__


try:
    from pypandoc import convert
except ImportError:
    import io

    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()


setup(
    name='django-boxberry',
    version=__version__,
    author='Aleksandr Alekseev',
    author_email='alekseevavx@gmail.com',
    description='Приложение для интеграции с API Boxberry',
    long_description=convert('README.md', 'rst'),
    url='',
    license='MIT',
    keywords=['django', 'boxberry'],
    install_requires=[
        'boxberry==0.1'
    ],
    include_package_data=True,
    packages=find_packages(),
)
