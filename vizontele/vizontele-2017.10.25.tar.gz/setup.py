#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

version = '2017.10.25'
setup(
    name='vizontele',
    version=version,
    description='A tool to crawl and get sources of TV Shows from various Turkish web sites.',
    author='Halil Ozercan',
    author_email='halilozercan@gmail.com',
    url='https://github.com/halilozercan/vizontele',
    download_url='https://github.com/halilozercan/vizontele/tarball/' + version,
    entry_points={
        'console_scripts': [
            'vizontele = vizontele.bin:main',
            'mizontele = vizontele.bin_movie:main'
        ],
    },
    install_requires=['requests', 'pyquery', 'demjson', 'pget', 'furl', 'PyExecJS'],
    packages=find_packages(exclude=("tests", "tests.*")),
)
