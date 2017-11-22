# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="linearcorex",
    version="0.1.0",
    description="LinearCorex attempts to find non-overlapping latent factors which explain most correlation in continuous data.",
    license="MIT",
    author="Greg Ver Steeg/Rob Brekelmans",
    author_email="brekelma@usc.edu",
    url="https://www.github.com/brekelma/linearcorex",
    packages=find_packages(),
    install_requires=[],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ]
)
