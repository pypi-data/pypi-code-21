#!/usr/bin/env python
import os
from setuptools import setup

here = os.path.dirname(__file__)


def read(filename):
    with open(os.path.join(here, filename)) as f:
        return f.read()


with open(os.path.join(here, "timeitd.py")) as f:
    for line in f:
        if line.startswith("__version__ = "):
            version = line.split(' = ')[1].strip('\'"\n')

setup(
    name="timeitd",
    version=version,
    author="Caner Çıdam",
    url="https://github.com/canercidam/timeitd",
    description="Simple timeit decorator for benchmark functions",
    long_description=read("README.md"),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python"
    ],
    license="MIT",
    py_modules=[
        "timeitd"
    ],
    test_suite="test_timeitd",
    zip_safe=False
)
