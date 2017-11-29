#!/usr/bin/env python
# vim:set ts=4 sts=4 sw=4 et:

from setuptools import setup
from km3flux import __version__

setup(
    name='km3flux',
    version=__version__,
    description='Atmospheric Neutrino Fluxes',
    url='http://git.km3net.de/km3py/km3flux',
    author='Moritz Lotze',
    author_email='mlotze@km3net.de',
    license='MIT',
    packages=['km3flux', ],
    include_package_data=True,
    install_requires=[
        'numpy',
        'scipy>=0.19',
        'h5py',
        'docopt',
        'matplotlib>=2.0',
        'pandas',
        'tables',
        'km3pipe[full]>=7.3.2'
    ]
)
