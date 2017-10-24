#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script of pysrc3."""

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
]

test_requirements = [
]

setup(
    name='pysrc3',
    version='0.1.3',
    description="Opens the source file of Python modules in an editor, "
                "a pager, or any other program of choice.",
    long_description=readme + '\n\n' + history,
    author="Eugene M. Kim",
    author_email='astralblue@gmail.com',
    url='https://github.com/astralblue/pysrc3',
    py_modules=['pysrc3'],
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pysrc3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
        'console_scripts': [
            'pysrc3 = pysrc3:main',
        ],
    }
)
