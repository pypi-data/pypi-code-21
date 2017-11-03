#
# Copyright 2017 Wenter
#
# https://yowenter.github.io
#

import os
import re

from setuptools import find_packages
from setuptools import setup

with open(os.path.join('tcs_sdk', '__init__.py'), "r") as f:
    source = f.read()
    m = re.search("__version__ = '(.*)'", source, re.M)
    __version__ = m.groups()[0]

setup(
    name="tcs-sdk",
    version=__version__,
    description="Tensorflow as service  Python Sdk",
    long_description="tcs sdk",
    author="Wenter W",
    author_email="wenter.wu@gmail.com",
    license="MIT License",
    url="https://github.com/yowenter",
    keywords="tensorflow sdk",
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["tensorflow"],
    zip_safe=False

)


