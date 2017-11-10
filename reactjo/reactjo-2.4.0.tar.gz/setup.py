# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup, find_packages

LATEST_VERSION = '2.4.0'

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('reactjo/reactjo.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name = "reactjo",
    packages = find_packages(include=["reactjo", "reactjo.*", "helpers"]),
    entry_points = {
        "console_scripts": ['reactjo = reactjo.reactjo:main']
        },
    version = LATEST_VERSION,
    description = "Extensible scaffolding engine.",
    long_description = long_descr,
    author = "Aaron Price",
    author_email = "coding.aaronp@gmail.com",
    url = "https://github.com/aaron-price/reactjo.git",
    install_requires=['six >= 1.10.0']
    )
