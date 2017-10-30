
#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="sxtjson",
    version="0.1.2",
    author="sxt",
    author_email="justcodepy@gmail.com",
    description="simple json parse",
    long_description=open("README.rst").read(),
    license="MIT",
    url="http://www.bjsxt.com",
    packages=['sxtjson'],
    install_requires=[
        "django",
        ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
         "Programming Language :: Python",
        ],
)

