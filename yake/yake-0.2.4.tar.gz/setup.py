#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0',
"fire",
"numpy",
"segtok",
"pandas",
"networkx",
"jellyfish",
"unidecode>=0.4.19",
"nltk>=3.1",
"scipy"]

# with open('requirements_dev.txt') as req_file:
#     requirements = req_file.readlines()



# TODO(arrp): put setup requirements (distutils extensions, etc.) here
setup_requirements = [
    'pytest-runner'    
]


# TODO: put package test requirements here
test_requirements = [
    'pytest'    
]

# author="Arian Pasquali",
# author_email='arrp@inesctec.pt',

setup(
    name='yake',
    version='0.2.4',
    description="Keyword extraction Python package",
    long_description=readme + '\n\n' + history,
    
    url='https://pypi.python.org/pypi/yake',
    packages=find_packages(include=['yake','StopwordsList']),
    entry_points={
        'console_scripts': [
            'yake=yake.cli:keywords'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='yake',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
