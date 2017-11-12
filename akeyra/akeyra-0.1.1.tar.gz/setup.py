#!/usr/bin/python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import akeyra

setup(
    name='akeyra',
    version=akeyra.__version__,
    packages=find_packages(),
    author="Jeremy Collin",
    author_email="jeremy.collin.lnk@gmail.com",
    description="Client app for Sakeyra",
    long_description=open('README.rst').read(),
    install_requires=[
        "configparser==3.5.0",
        "pyjwt==1.5.3",
        "requests==2.18.4"],
    include_package_data=True,
    url='https://github.com/LaMethode/akeyra',
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Natural Language :: French",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",  # noqa
        "Topic :: System :: Systems Administration",
    ],
    entry_points={'console_scripts': ['akeyra = akeyra.akeyra:main']},
    license="GPLv3",
)
