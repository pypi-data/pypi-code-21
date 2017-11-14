#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
from setuptools import setup


name = 'retexto'
package = 'retexto'
repo_url = 'https://github.com/Edux87/retexto'
REQUIREMENTS = [
    'unidecode'
]

DESCRIPTION = ("Fast text processing")
def find_version(fname):
    """Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    """
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version

__version__ = find_version(name + "/__init__.py")

with open('README.md') as f:
    LONG_DESCRIPTION = f.read()


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


setup(
    name=name,
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Edgar Castañeda',
    author_email='edaniel15@gmail.com',
    platforms=['linux'],
    packages=get_packages(package),
    package_data=get_package_data(package),
    install_requires=REQUIREMENTS,
    url=repo_url,
    tests_require=['invoke'],
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Editors :: Word Processors'
    ],
)
