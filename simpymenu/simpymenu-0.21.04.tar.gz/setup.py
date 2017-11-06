# simpymenu setup

from distutils.core import setup

setup(
    name = 'simpymenu',
    packages = ['simpymenu'],
    version = '0.21.04',
    description = 'Auto generate simple text menu with borders',
    author = 'Tai-Fong Foong',
    author_email = "georgie@puppycoders.com",
    url = "https://github.com/kylosolo/SimPy-Menu",
    download_url = "https://github.com/kylosolo/SimPy-Menu",
    keywords = ["text menu", "box", "menu system"],
    classifiers = [
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: User Interfaces",
        ],
    long_description = """\
Simple Python Text Menu
-----------------------

Auto generate a text menu with box border from a list of items.
 - Different box styles with option for no box.
 - Auto generating numbers for list of items
 - Optional header for menu
 - Optional sub-header for menu
 - Optional pairing of callables to menu items
 - Auto formatting with the headers/ sub-headers/ menu items
 - If no optional callables are paired, it will return the number selected

This version requires Python 3 or later.
Tested on macOS High Seirra, Ubuntu 16.04, Windows 10 Creator edition.
"""
)
