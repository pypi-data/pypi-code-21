# coding: utf-8

"""
    stylelens-feature

    Feature extrator from a image file

    OpenAPI spec version: 0.0.1
    Contact: master@bluehack.net
"""


import sys
from setuptools import setup, find_packages

NAME = "stylelens-feature"
VERSION = "1.0.2"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil", \
            "tensorflow >= 1.3"]

setup(
    name=NAME,
    version=VERSION,
    description="stylelens-feature",
    author_email="devops@bluehack.net",
    url="",
    keywords=["Swagger", "stylelens-feature"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    This is a API document for Object Detection on fashion items\&quot;
    """
)
