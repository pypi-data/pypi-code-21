#sdelib's setup.py
from setuptools import setup, find_packages
from distutils.core import setup
setup(
    name = "sdelib",
    packages = find_packages(),
    version = "0.905",
    description = "Performs various actions on Ito SDEs",
    author = "Per Hauan",
    author_email = "perman07@hotmail.com",
    url = "https://github.com/perhauan/sdelib",
    download_url = "https://github.com/perhauan/sdelib/archive/master.zip",
    keywords = ["SDE", "Ito", "convergence", "stability"],
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        ],
    long_description = """\
sdelib is a Python package (written in Python 3.5) for performing various
actions on Ito stochastic differential equations (SDE). These actions include:
1) Input SDEs as SDEprob objects.
2) Solve SDEs with an SDEint class that performs numerical Ito integration on
SDEprob objects.
3) Estimate strong and weak orders of convergence through a SDEanalysis class
4) Perform these actions either through creating a Python script which uses the
above classes, or running gui.py which allows you to perform these actions
quickly through a GUI.

sdelib was written as part of a Master's thesis and is intended to be able to
do simple actions on SDEs without requiring a lot of coding to do so.


This version requires Python 3 or later;
"""
)