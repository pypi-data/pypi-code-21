#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('LICENSE') as license_file:
    license = license_file.read()

about = {}
with open(os.path.join(here, "inventorpy", "__version__.py")) as f:
    exec(f.read(), about)

requirements = [
    # TODO: put package requirements here
]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    packages=find_packages(exclude=["tests"]),
    install_requires=requirements,
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__url__'],
    py_modules=[about['__title__']],
    long_description=readme,
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: MIT License",
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
)
