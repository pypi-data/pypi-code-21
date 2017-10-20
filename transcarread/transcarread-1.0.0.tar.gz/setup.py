#!/usr/bin/env python
req = ['nose','python-dateutil', 'pytz','numpy','xarray', 'scipy', 'matplotlib','seaborn',]
pipreq=['gridaurora','sciencedates']

import pip
try:
    import conda.cli
    conda.cli.main('install',*req)
except Exception as e:
    pip.main(['install'] + req)
pip.main(['install'] + pipreq)
# %%
from setuptools import setup

setup(name='transcarread',
      packages=['transcarread'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scivision/transcarrread',
      version='1.0.0',
	  classifiers=[
      'Intended Audience :: Science/Research',
      'Development Status :: 4 - Beta',
      'Topic :: Scientific/Engineering :: Atmospheric Science',
      'Programming Language :: Python :: 3',
	  ],
	  install_requires=req+pipreq,
	  )
