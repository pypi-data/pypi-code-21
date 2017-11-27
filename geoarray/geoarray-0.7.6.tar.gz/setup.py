#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import warnings
from importlib import util

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'py_tools_ds>=0.10.0', 'numpy', 'matplotlib', 'six', 'gdal', 'shapely', 'geopandas', 'pandas', 'dill', 'mpld3',
    'geojson', 'folium', 'scikit-image', 'dask>=0.15.0'
    # dask is only indirectly needed but updating to >=0.15.0 resolves https://stackoverflow.com/questions/43833081/
    #   attributeerror-module-object-has-no-attribute-computation
    # 'holoviews', #  conda install --yes -c ioam bokeh holoviews ; \
    # git+https://github.com/matplotlib/basemap.git  # conda install --yes -c conda-forge basemap
    ]
setup_requirements = ['dask>=0.15.0']
test_requirements = requirements + ["coverage", "nose", "nose2", "nose-htmloutput", "rednose"]

setup(
    name='geoarray',
    version='0.7.6',
    description="Fast Python interface for geodata - either on disk or in memory.",
    long_description=readme + '\n\n' + history,
    author="Daniel Scheffler",
    author_email='danschef@gfz-potsdam.de',
    url='https://gitext.gfz-potsdam.de/danschef/geoarray',
    packages=find_packages(),  # searches for packages with an __init__.py and returns them as properly formatted list
    package_dir={'geoarray': 'geoarray'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords=['geoarray', 'geoprocessing', 'gdal', 'numpy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements
)


# check for holoviews
if not util.find_spec('holoviews'):
    warnings.warn('You need to install holoviews manually (see www.holoviews.org) if you want to use interactive '
                  'plotting. It is not automatically installed.')

# check for basemap
if not util.find_spec('mpl_toolkits.basemap'):
    warnings.warn('You need to install basemap manually (see www./matplotlib.org/basemap) if you want to plot maps. '
                  'It is not automatically installed.')
