# coding: utf-8

"""
    BlueLens Index API Client for bl-api-index server.

    Contact: master@bluehack.net
"""


import sys
from setuptools import setup, find_packages

NAME = "stylelens-index"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="BlueLens Index API",
    author_email="devops@bluehack.net",
    url="",
    keywords=["Swagger", "BlueLens Index API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    This is a bl-api-index server.
    """
)
