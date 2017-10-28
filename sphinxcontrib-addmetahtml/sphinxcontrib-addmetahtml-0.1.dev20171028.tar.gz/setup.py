#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requires = ['Sphinx>=1.6']

setup(
    name='sphinxcontrib-addmetahtml',
    version='0.1',
    url='https://github.com/0xHiteshPatel/sphinxcontrib-addmetahtml',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-addmetahtml',
    license='BSD',
    author='Hitesh Patel',
    author_email='hp@hiteshpatel.net',
    description='Sphinx "addmetahtml" extension',
    long_description=
          "Sphinx extension that enables addition of user-defined HTML to docs",
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
