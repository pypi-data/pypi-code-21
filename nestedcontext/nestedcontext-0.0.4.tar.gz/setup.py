#!/usr/bin/env python

import unittest
from distutils.core import setup
from setuptools import find_packages


setup(
    name="nestedcontext",
    version="0.0.4",
    description="Nested context for scoped variables.",
    author="Tony Tung",
    author_email="tonytung@merly.org",
    packages=find_packages("src"),
    package_dir={"":"src"},
    test_suite="tests",
)
