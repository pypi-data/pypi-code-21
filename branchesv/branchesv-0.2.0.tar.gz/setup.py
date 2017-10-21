#!/usr/bin/env python
# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = open('requirements.txt').readlines()

test_requirements = open('requirements_dev.txt').readlines()

setup(
    name='branchesv',
    version='0.2.0',
    description="Python package to get the information of all the repos in a directory",
    long_description=readme + '\n\n' + history,
    author="Vauxoo",
    author_email='joseangel@vauxoo.com',
    url='https://git.vauxoo.com/vauxoo/branchesv',
    packages=find_packages(),
    package_dir={'branchesv':
                 'branchesv'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='branchesv',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',

    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points='''
        [console_scripts]
        branchesv=branchesv.branchesvcmd:cli
    ''',
)
