import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "munger",
    version = "0.0.1",
    author = "Nicholas Del Grosso and Achilleas Koutsou",
    author_email = "delgrosso.nick@gmail.com",
    description = ("A Python module that munges all variables in a namespace, as a demonstration of some aspects of the Python language."),
    license = "GNU",
    keywords = "example mungin python tutorial",
    url = "https://github.com/neuroneuro15/munger",
    packages=['munger'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
