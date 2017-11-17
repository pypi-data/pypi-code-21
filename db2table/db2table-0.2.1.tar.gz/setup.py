#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

requirements = [
    'Click>=6.0',
    'awesome-slugify==1.6.5',
    'Jinja2',
    'sqlalchemy',
]


test_requirements = [
    'pytest',
]

setup(
    name='db2table',
    version='0.2.1',
    description="Extract data from database in html table",
    author="Khalid Chakhmoun",
    author_email='fr.ckhalid@gmail.com',
    url='https://github.com/KhalidCK/db2table',
    py_modules=['db2table'],
    packages=find_packages(include=['db2table']),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'db2table=db2table:cli'
        ]
    },
    install_requires=requirements,
    zip_safe=False,
    keywords='db2table',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
