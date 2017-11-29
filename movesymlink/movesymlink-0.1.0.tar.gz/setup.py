#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
]

setup_requirements = [
    'pytest-runner',
]

test_requirements = [
    'pytest',
]

setup(
    name='movesymlink',
    version='0.1.0',
    description="Move Symlink provides a function and a command that moves a "
                "symbolic link to another directory and adjusts its link "
                "target.",
    long_description=readme + '\n\n' + history,
    author="Eugene M. Kim",
    author_email='astralblue@gmail.com',
    url='https://github.com/astralblue/movesymlink',
    py_modules=['movesymlink'],
    entry_points={
        'console_scripts': [
            'movesymlink = movesymlink:main',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='movesymlink',
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
    setup_requires=setup_requirements,
)
