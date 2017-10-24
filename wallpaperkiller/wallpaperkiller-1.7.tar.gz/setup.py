#!/usr/bin/python3

from setuptools import setup

PACKAGE = "wallpaperkiller"
NAME = "wallpaperkiller"
DESCRIPTION = "This package can change the wallpaper under the GNOME Linux / Ubuntu16.04"
AUTHOR = "GMFTBY"
AUTHOR_EMAIL = "18811371908@163.com"
URL = "https://github.com/gmftbyGMFTBY"
VERSION = 1.7

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    # long_description=read("README.md"),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=["stretch"],
    install_requires = ['requests' , 'bs4']
)

