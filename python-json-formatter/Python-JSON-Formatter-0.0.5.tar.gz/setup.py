#!/usr/bin/env python
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()


setup(
    name='Python-JSON-Formatter',
    version='0.0.5',
    description='A log formatter for python logging.',
    long_description=readme,
    author='codeif',
    author_email='me@codeif.com',
    url='https://github.com/codeif/Python-JSON-Formatter',
    license='MIT',
    install_requires=['JSON-log-formatter'],
    packages=find_packages(exclude=("tests", "tests.*")),
)
