#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='dynamat2050',
    version='0.2.4',
    description='A library for accessing data from the Dynamat2050 API',
    keywords='energy consumption data API',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    author='Graeme Stuart',
    author_email='gstuart@dmu.ac.uk',
    url='https://github.com/ggstuart/dynamat2050',
    # modules=['']
    # package_dir={'':'dynamat2050'},
    packages=find_packages(),
    install_requires=['requests'],
    entry_points = {
        'console_scripts': [
            'dynamat_meters=dynamat2050.download:meters',
            'dynamat_data=dynamat2050.download:data'
        ],
    }
)
