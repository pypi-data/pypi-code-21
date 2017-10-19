# -*- encoding: utf-8 -*-
from setuptools import setup

setup(
    name='datetime_truncate',
    version='1.1.0',
    url='https://github.com/gaqzi/datetime_truncate',
    author='Björn Andersson',
    author_email='ba@sanitarium.se',
    description='Truncate datetime objects to a set level of precision',
    license='BSD',
    long_description=open('README.rst').read(),
    packages=['datetime_truncate'],
    package_data={
        '': ['README.rst']
    },
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose>=1.2.1'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'six',
        'typing',
    ]
)
