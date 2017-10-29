#!/usr/bin/env python
# -*- coding: utf-8 -*-
#                     __          ___        __      ___
#                    /\ \__ __  /'___\      /\ \    /\_ \
#    ___     __  _ __\ \ ,_/\_\/\ \__/   __ \ \ \___\//\ \      __
#   /'___\ /'__`/\`'__\ \ \\/\ \ \ ,__\/'__`\\ \ '__`\\ \ \   /'__`\
#  /\ \__//\  __\ \ \/ \ \ \\ \ \ \ \_/\ \L\.\\ \ \L\ \\_\ \_/\  __/
#  \ \____\ \____\ \_\  \ \__\ \_\ \_\\ \__/.\_\ \_,__//\____\ \____\
#   \/____/\/____/\/_/   \/__/\/_/\/_/ \/__/\/_/\/___/ \/____/\/____/
#
#

"""The setup script."""

import os
import sys

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open(os.path.join(here, 'requirements', 'requirements.txt')) as rq_file:
    requirements = [i.strip() for i in rq_file.readlines() if i.strip()]

setup_requirements = [
    'nose',
]

with open(os.path.join(here, 'requirements', 'requirements-test.txt')) as rq_file:
    test_requirements = [i.strip() for i in rq_file.readlines()]
test_requirements.extend([
    'nosetests',
    'nose-cov',
    'nose-parameterized',
])

about = {}
with open(os.path.join(here, 'certifiable', '__version__.py')) as f:
    exec (f.read(), about)
version = about['__version__']

# 'setup.py publish' shortcut.
if sys.argv[-1] == 'publish':
    version = about['__version__']
    print("Tagging release as: {v}".format(v=version))
    os.system("git tag -a {v} -m 'version {v}'".format(v=version))
    os.system('git push --tags')
    os.system('python setup.py sdist bdist_wheel')
    os.system('twine upload dist/*')
    sys.exit()
elif sys.argv[-1] == 'test':
    os.system('make test')
    sys.exit()

setup(
    name='certifiable',
    version=about['__version__'],
    description=about['__short_description__'],
    long_description=readme + '\n\n' + history,
    author=about['__author__'],
    author_email=about['__email__'],
    url=about['__url__'],
    packages=find_packages(include=['certifiable']),
    entry_points={
        'console_scripts': [
            'certifiable=certifiable.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords=about['__keywords__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
