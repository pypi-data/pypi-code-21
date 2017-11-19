#!/usr/bin/env python

""" setup.py pyinstamation."""

from setuptools import setup

setup(
    name="pyinstamation",
    version="1.1.0",
    description="Instagram bot, written in python 3",
    keywords=["bot", "instagram", "pybot", "Bot", "Instagram", "Pybot"],
    author="Santiago Fraire, Marcos Schroh",
    author_email="santiwilly@gmail.com, schrohm@gmail.com",
    url="https://github.com/dscovr/pyinstamation",
    download_url="https://github.com/dscovr/pyinstamation.git",
    install_requires=[
        "selenium==3.5.0"
        "PyYAML==3.12"
        "peewee==2.10.1"
        "requests==2.18.3"
        "coverage==4.4.1"
        "pyvirtualdisplay==0.2.1"
        "codecov==2.0.9"
    ],
    packages=["pyinstamation"],
    license='GPLv3'
)
