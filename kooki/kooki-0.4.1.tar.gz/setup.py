#!/usr/bin/env python
import os
from setuptools import setup, find_packages

__version__ = '0.4.1'

datadir = os.path.join('jars')
data_files = [(os.path.join('/usr/share/kooki', d), [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(datadir)]

setup(
    name='kooki',
    version=__version__,
    description='The ultimate document generator.',
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/kooki/kooki',
    scripts=['scripts/kooki'],
    install_requires=['markdown', 'empy', 'pyyaml', 'toml', 'requests', 'termcolor', 'vcstool', 'libsass'],
    packages=find_packages(exclude=['tests*', 'jars']),
    test_suite='tests',
    data_files=data_files,
)
