# coding: utf-8

"""
    bluelens-log

    Contact: master@bluehack.net
"""


import sys
from setuptools import setup, find_packages

NAME = "bluelens-log"
VERSION = "1.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["redis"]

setup(
    name=NAME,
    version=VERSION,
    description="bluelens-log",
    author_email="master@bluehack.net",
    url="",
    keywords=["bluelens", "bluelens-log"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)
