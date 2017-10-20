#! /usr/bin/env python

from setuptools import setup, find_packages
import versioneer
from io import open

setup (
    name = "s3lncoll",
    version = versioneer.get_version (),
    description = "Line stream s3 files into ~uniform lumps in S3",
    long_description = open ("README.rst", "r", encoding = "utf-8").read (),
    cmdclass = versioneer.get_cmdclass (),
    classifiers = [],
    keywords = "S3 aggregate tarball compress",
    author = "J C Lawrence",
    author_email = "claw@kanga.nu",
    url = "https://pypi.python.org/pypi/s3lncoll",
    license = "LGPL v3.0",
    packages = find_packages (exclude = ["tests",]),
    package_data = {
    },
    zip_safe = True,
    install_requires = [line.strip ()
                        for line in open ("requirements.txt", "r",
                                          encoding = "utf-8").readlines ()],
    entry_points = {
        "console_scripts": [
            "s3lncoll = s3lncoll.main:main",
        ],
    },
)
