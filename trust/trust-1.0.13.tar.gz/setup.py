#!/usr/bin/env python

import setuptools

setuptools.setup(
    name="trust",
    version="1.0.13",
    description="A hierarchical database engine with read-only access to "
                "data, ideally used for cross-application settings and "
                "infrastructure description.",
    long_description=open("summary.rst", "r", encoding="utf-8").read(),
    author="Arseni Mourzenko",
    author_email="arseni.mourzenko@pelicandd.com",
    url="https://go.pelicandd.com/n/python-trust",
    license="MIT",
    keywords="database json settings",
    install_requires=[
        "flask==0.12.2",
        "passlib==1.7.1"
    ],
    packages=setuptools.find_packages(
        exclude=["tests", "tests.*", "www", "www.*"]
    ),
    # Since it seems that there is no way to include data with `data_files`,
    # this looks like the only way to include the deployment script and other
    # static files. Since the name of the package is mandatory, any name which
    # exists in the project will work.
    package_data={
        "trust": [
            "../summary.rst",
            "../localtrust.py",
            "../extras/*"
        ]
    }
)
