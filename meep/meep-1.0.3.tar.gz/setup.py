# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name = "meep",
    version = "1.0.3",
    packages = ['meep'],

    entry_points = {
        'console_scripts': ['meep=meep.meep:meep'],
    },
    author = "Fredrik Håård",
    author_email = "fredrik@metallapan.se",
    description = "Very light-weight task runner",
    license = "Do whatever you want, don't blame me",
    keywords = "ci cd automation operations",
    package_data={'meep': ['filelist.txt']},
    url = "https://bitbucket.org/metallapan/meep",
    classifiers = """Intended Audience :: Developers
License :: Freely Distributable
License :: OSI Approved :: BSD License
License :: OSI Approved :: MIT License
Operating System :: Unix
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries
Topic :: Software Development :: Version Control""".split('\n'),
    long_description = """Prototype of very light task runner, meant to be used for CI/CD tasks triggered by VCS hooks"""
)
