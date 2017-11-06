import os
from setuptools import setup, find_packages


PACKAGE = "kysdk"
VERSION = __import__('ky').__version__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="kysdk",
    version=VERSION,
    author="ShangHai Shilai",
    author_email="developers@kuaiyutech.com",
    description=read("README"),
    license="BSD",
    keywords="stock kuaiyutech",
    url="http://packages.python.org/kysdk",
    packages=find_packages(exclude=["tests.*", "tests"]),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
