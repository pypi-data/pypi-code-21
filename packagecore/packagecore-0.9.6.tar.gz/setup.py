#!/usr/bin/env python3

PACKAGENAME = "packagecore"

from setuptools import setup, find_packages

with open("%s/VERSION" % PACKAGENAME, "r") as versionFile:
  version = versionFile.read().strip()

setup(
  name=PACKAGENAME,
  description="Utility for building Linux packages for multiple " \
      "distributions.",
  author="Dominique LaSalle",
  author_email="dominique@bytepackager.com",
  url="https://github.com/bytepackager/packagecore",
  license="GPL2",
  install_requires="pyyaml",
  python_requires=">=3.0",
  version=version,
  packages=find_packages(),
  test_suite=PACKAGENAME,
  include_package_data=True,
  entry_points={
    "console_scripts": [
      "%s = %s.__main__:main" % (PACKAGENAME, PACKAGENAME)
    ]
  })
