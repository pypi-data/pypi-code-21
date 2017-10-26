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


from setuptools import setup, find_packages

setup(
    name = 'centroiding',      # The name of the PyPI-package.
    packages = find_packages(exclude=["test"]),
    version = '0.3.1',    # Update the version number for new releases
    #scripts=['ngtsio'],  # The name of the included script(s), and also the command used for calling it
    description = 'Centroiding analysis for transiting exoplanet candidate vetting',
    author = 'Maximilian N. Guenther',
    author_email = 'mg719@cam.ac.uk',
    url = 'https://github.com/MNGuenther/centroiding_pip',
    download_url = 'https://github.com/MNGuenther/centroiding_pip',
    classifiers = [],
    install_requires=['ngtsio>=1.4.0','mytools>=1.1.3','numpy>=1.10','matplotlib>0.1','scipy>=0.1','pandas>=0.1']
    )



