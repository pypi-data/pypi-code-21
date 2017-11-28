# coding: utf-8
# Copyright (c) 2016, 2017, Oracle and/or its affiliates. All rights reserved.

import io
import os
import re
from setuptools import setup, find_packages

PACKAGE_LONG_DESCRIPTION = """This package is deprecated in favor of the `OCI CLI <https://pypi.python.org/pypi/oci-cli>`_ package. This package will stop being updated in March 2018. Please upgrade to the OCI CLI package to avoid interruption."""


def open_relative(*path):
    """
    Opens files in read-only with a fixed utf-8 encoding.

    All locations are relative to this setup.py file.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    filename = os.path.join(here, *path)
    return io.open(filename, mode="r", encoding="utf-8")


with open_relative("src", "oraclebmc_cli", "version.py") as fd:
    version = re.search(
        r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
        fd.read(), re.MULTILINE).group(1)
    if not version:
        raise RuntimeError("Cannot find version information")

with open_relative("README.rst") as f:
    readme = f.read()


requires = [
    'oci-cli==2.4.12'
]

setup(
    name='oraclebmc-cli',
    url='https://docs.us-phoenix-1.oraclecloud.com/Content/API/SDKDocs/cli.htm',
    version=version,
    author='Oracle',
    author_email='joe.levy@oracle.com',
    description='Oracle Cloud Infrastructure CLI',
    long_description=PACKAGE_LONG_DESCRIPTION,
    install_requires=requires,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    license="Universal Permissive License 1.0 or Apache License 2.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: Universal Permissive License (UPL)",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ]
)
