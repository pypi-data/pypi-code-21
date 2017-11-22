# -*- coding: utf-8 -*-

from setuptools import setup

version = '1.0.1'


setup(
    name='django-language-detect',
    version=version,
    keywords='django-language-detect',
    description='Django browser language detect',
    long_description=open('README.rst').read(),

    url='https://github.com/wmarquardt/django-language-detect',

    author='William Marquardt',
    author_email='williammqt@gmail.com',

    packages=['language_detect'],
    py_modules=[],
    install_requires=['django-six'],

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
