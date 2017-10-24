#!/usr/bin/env python

import setuptools
from os import path

from starter_api import info
from pip.req import parse_requirements

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

install_reqs = parse_requirements(path.join(here, 'requirements.txt'), session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


setuptools.setup(
    name=info.__package_name__,
    version=info.__version__,

    description='Client for Starter Server API',
    long_description=long_description,

    url='https://github.com/rw-meta/starter-py-client',

    author='Artur Geraschenko',
    author_email='arturgspb@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],

    install_requires=reqs,
    packages=["starter_api"],
    package_data={'': ['LICENSE']},
    package_dir={'starter_api': 'starter_api'},
    include_package_data=True,
)
