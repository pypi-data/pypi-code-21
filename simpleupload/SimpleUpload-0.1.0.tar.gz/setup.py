#!/usr/bin/env python
from setuptools import setup


with open('README.rst') as f:
    readme = f.read()


setup(
    name='SimpleUpload',
    version='0.1.0',
    description='A HTTP Server for upload file.',
    long_description=readme,
    packages=['simple_upload'],
    url='https://github.com/codeif/SimpleUpload',
    license='MIT',
    author='codeif',
    author_email='me@codeif.com',
    install_requires=['Flask']
)
