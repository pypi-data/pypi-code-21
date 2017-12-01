# coding: utf-8
from setuptools import setup
import sys


# set __version__, __author__
exec(open("cpinsim/version.py", encoding="utf-8").read())

setup(
    name = 'cpinsim',
    version=__version__,
    author=__author__,
    author_email = 'bianca.stoecker@tu-dortmund.de',
    description = 'CPINSim - Constrained Protein Interaction Networks Simulator\n CPINSim is a package for the simulation of constrained protein interaction networks. Beside simulation of complex formation in a cell there are methods for data preprocessing provided:  Annotation of interactions and constraints with domains; A parser to provide the needed protein input format.',
    long_description = open("README.rst").read(),
    license = 'MIT',
    url = 'https://github.com/BiancaStoecker/cpinsim',
    packages = ['cpinsim'],
    entry_points={
        "console_scripts": ["cpinsim = cpinsim:main"]
    },
    install_requires=[
        "networkx==1.11.0",
        "bitarray==0.8.1",
        "scipy"
    ],
    classifiers = [
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)    