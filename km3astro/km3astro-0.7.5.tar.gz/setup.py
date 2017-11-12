#!/usr/bin/env python
# vim:set ts=4 sts=4 sw=4 et:

from setuptools import setup
from km3astro import __version__


setup(
    name='km3astro',
    version=__version__,
    description='Astro Utils',
    url='http://git.km3net.de/km3py/km3astro',
    author='Moritz Lotze',
    author_email='mlotze@km3net.de',
    license='BSD-3',
    packages=['km3astro', ],
    install_requires=[
        'astropy>=1.3',
        'numpy',
        'pandas',
        'matplotlib>=2.0',
        'utm',
        'km3pipe[full]>=7.3.2',
        'tables'
    ]
)
