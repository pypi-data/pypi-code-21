"""
Publish a new version:
Change version in packageInfo file (lifepo4weredPyController)
pull changes
Execute:
$ git tag X.Y.Z -m "Release X.Y.Z"
$ git push --tags
$ pip install --upgrade twine wheel
$ python setup.py sdist bdist_wheel --universal
$ twine upload dist/*
"""
from lifepo4weredPyController.packageInfo import (PACKAGE_NAME, AUTHOR,
                                                  VERSION, STATUS)
import os
import sys
from setuptools import setup, find_packages

# 'Lifepo4weredPyController'
_GITHUB_NAME = PACKAGE_NAME[0].upper() + PACKAGE_NAME[1:]
_DOWNLOAD_URL = (
    'https://github.com/fredericklussier/' + _GITHUB_NAME + '/' + VERSION
)

_LONG_DESCRIPTION = """
Our intention is to design an oriented object access to the
lifepo4wered-pi3 data module during runtime application.

reference: http://lifepo4wered.com/lifepo4wered-pi3.html

Using the Raspbery Pi zero in many projects, I found this product
very usefull. So to help my children and python colleagues, we design this.

You can find here the documentation of the lifepo4wered product:
http://lifepo4wered.com/files/LiFePO4wered-Pi3-Product-Brief.pdf.

"""

setup(
    name=PACKAGE_NAME,
    packages=[PACKAGE_NAME],
    version=VERSION,
    description='Observable data and class oriented of Lifepo4wered battery power module.',
    long_description=_LONG_DESCRIPTION,
    license='MIT',
    author=AUTHOR.split("<")[0].strip(),
    author_email=(AUTHOR.split("<")[1])[:-1],
    url='https://github.com/fredericklussier/' + _GITHUB_NAME,
    download_url=_DOWNLOAD_URL,
    install_requires=[
        "tinyPeriodicTask>=1.3.1",
        "observablePy>=0.2.2",
        "lifepo4weredPy>=0.1.0"
    ],
    keywords=[
        'raspberry-pi', 'raspberrypi',
        'lifepo4wered', 'lifepo4wered-pi', 'lifepo4weredpi',
        'battery', 'powersource'
    ],
    classifiers=[
        'Development Status :: ' + STATUS,
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English'
    ],
)
