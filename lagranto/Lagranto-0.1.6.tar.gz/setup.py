#!/usr/bin/env python
# coding: utf-8
import os
import io
from glob import glob
from os.path import splitext, basename
from setuptools import setup, find_packages

# Package meta-data.
__NAME__ = 'Lagranto'
__AUTHOR__ = 'Nicolas Piaget'
__AUTHOR_EMAIL__ = 'nicolas.piaget@env.ethz.ch'
__URL__ = 'https://lagranto.readthedocs.io/en/latest/'
__DW_URL__ = 'https://git.iac.ethz.ch/npiaget/Lagranto'
__DESCRIPTION__ = 'Library to work with trajectories.'

with io.open('README.rst', encoding='utf-8') as f:
    readme = '\n' + f.read()

on_rtd = os.environ.get('READTHEDOCS') == 'True'
if on_rtd:
    install_requires = ['path.py'],
else:
    install_requires = ['path.py', 'cartopy', 'numpy',
                        'netCDF4', 'matplotlib'],

setup(name=__NAME__,
      version='0.1.6',
      author=__AUTHOR__,
      author_email=__AUTHOR_EMAIL__,
      maintainer=__AUTHOR__,
      maintainer_email=__AUTHOR_EMAIL__,
      url=__URL__,
      download_url=__DW_URL__,
      description=__DESCRIPTION__,
      long_description=readme,
      packages=find_packages('src', exclude=['docs', 'tests*']),
      package_dir={'': 'src'},
      py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
      install_requires=install_requires,
      scripts=['bin/quickview.py'],
      tests_require=['pytest'],
      extras_require={
          'docs':  ['Sphinx', 'sphinx-rtd-theme'],
          'testing': ['pytest'],
      },
      include_package_data=True,
      license='GPL-3.0+',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering :: Atmospheric Science'
      ],
      keywords=['data', 'science', 'meteorology', 'climate trajectories'],
      python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
      )
