# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 15:32:21 2016

@author: 
Maximilian N. Guenther
Battcock Centre for Experimental Astrophysics,
Cavendish Laboratory,
JJ Thomson Avenue
Cambridge CB3 0HE
Email: mg719@cam.ac.uk
"""


from setuptools import setup

setup(
    name = 'ngtsio',      # The name of the PyPI-package.
    packages = ['ngtsio'],
    version = '1.5.0',    # Update the version number for new releases
    #scripts=['ngtsio'],  # The name of the included script(s), and also the command used for calling it
    description = 'Wrapper for astropy and cfitsio readers for NGTS data files',
    author = 'Maximilian N. Guenther',
    author_email = 'mg719@cam.ac.uk',
    url = 'https://github.com/MNGuenther/ngtsio',
    download_url = 'https://github.com/MNGuenther/ngtsio/releases',
    classifiers = [],
    install_requires=['astropy>=1.1','fitsio>=0.9','numpy>=1.10'],
    include_package_data = True
    )



