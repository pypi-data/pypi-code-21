"""
Publish a new version:
Change version in package __init__ file
Change version in this setup file
pull __init__ and setup
Execute:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel --universal
$ twine upload dist/*
"""
import codecs
import os
import sys
from setuptools import setup, find_packages


NAME = 'lifepo4weredPyController'
GITHUB_NAME = 'Lifepo4weredPyController'
VERSION = '0.1.0'
DOWNLOAD_URL = (
    'https://github.com/fredericklussier/' + GITHUB_NAME + '/' + VERSION
)


setup(
    name=NAME,
    packages=[NAME],
    version=VERSION,
    description='Enable observable behavior.',
    long_description=open('ReadMe.rst').read(),
    license='MIT',
    author='Frederick Lussier',
    author_email='frederick.lussier@hotmail.com',
    url='https://github.com/fredericklussier/' + GITHUB_NAME,
    download_url=DOWNLOAD_URL,
    install_requires=[
        "tinyPeriodicTask>=1.3.1",
        "observablePy>=0.2.2",
        "lifepo4weredPy>=0.1.0"
    ],
    keywords=[
        'raspberry-pi', 'raspberrypi', 'lifepo4wered', 'battery', 'powersource'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English',
    ],
)
