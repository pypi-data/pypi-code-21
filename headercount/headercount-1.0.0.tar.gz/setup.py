#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2017 Nico Madysa

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
from headercount import get_version


long_description = """Headercount goes through a C or C++ project and
searches for #include directives. It recursively follows project header
includes and prints statistics about which header was included how many
times. This indicates which headers are depended on the most, which is
useful when debugging long compile times of medium-sized projects.
"""

setup(
    name='headercount',
    version=get_version(),
    python_requires='>=3.4',
    packages=['headercount'],
    entry_points={
        'console_scripts': [
            'headercount = headercount.__main__:main',
            ]
        },
    zip_safe=True,
    author='Nico Madysa',
    author_email='uebertreiber@gmx.de',
    description='Count directly and indirectly included headers in a C/C++ project',
    long_description=long_description,
    license='Apache License, Version 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Debuggers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        ],
    keywords='header include c c++ include',
    url='https://github.com/troiganto/headercount',
)
