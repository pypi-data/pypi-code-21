# -*- coding: utf-8 -*-

from __future__ import with_statement

from setuptools import setup


version = '1.0.0'


setup(
    name='django-excel-storage',
    version=version,
    keywords='django-excel-storage',
    description='Django Excel Storage',
    long_description=open('README.rst').read(),

    url='https://github.com/Brightcells/django-excel-storage',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    py_modules=['excel_storage'],
    install_requires=['xlwt', 'pytz', 'screen', 'django-six>=1.0.4'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial :: Spreadsheet',
    ],
)
