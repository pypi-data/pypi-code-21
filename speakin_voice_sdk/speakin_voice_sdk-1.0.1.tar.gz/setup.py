#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name = "speakin_voice_sdk",
    version = "1.0.1",
    description = "speakin voice sdk",
    packages = find_packages("src"),
    author = 'panleiming',
    author_email = 'panleiming@speakin.mobi',
    url = 'http://www.speakin.mobi/pages/index.html',
    install_requires = [
        "marshmallow",
        "requests",
        "pycrypto",
        "bson",
    ],
    package_dir = {"": "src"},
    )
