# -*- coding: utf-8 -*-
import io
import sys

NAME = 'uqer'
MAINTAINER = 'uqer'
EMAIL = 'service.uqer@datayes.com'
URL = 'uqer.io'
LICENSE = 'DataYes'


import os

from setuptools import find_packages, setup

exec(compile(open('uqer/version.py').read(), 'pypkg/version.py', 'exec'))
version = __version__

setup(
      name = NAME,
      description = 'Package for DataYes Uqer API access',
      version = version,
      maintainer = MAINTAINER,
      maintainer_email = EMAIL,
      license = LICENSE,
      author = NAME,
      author_email = EMAIL,
      packages=find_packages(),
      package_data = {'': ['*.ipynb']},
      install_requires = [
        "requests>=2.7.0",
        "pandas",
        "zerorpc",
        "python-dateutil>=2.5.3"
      ]
)

if len(sys.argv)>=2 and sys.argv[1] in ['sdist']:
    os.system("mv dist/uqer-%s.zip dist/uqer.zip" %version)

