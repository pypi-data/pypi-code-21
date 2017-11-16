#!/usr/bin/env python

from setuptools import setup
from os.path import exists

import versioneer


setup(name='xarray-topo',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='xarray extension for topographic analysis and modelling',
      url='https://gitext.gfz-potsdam.de/sec55-public/xarray-topo',
      maintainer='Benoit Bovy',
      maintainer_email='bbovy@gfz-potsdam.de',
      license='BSD-Clause3',
      keywords='python xarray topography modelling DEM digital-elevation-model',
      packages=['xtopo', 'xtopo.models', 'xtopo.algos'],
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      python_requires='>=3.4',
      install_requires=['numpy', 'xarray >= 0.8.0', 'numba >= 0.35.0'],
      zip_safe=False)
