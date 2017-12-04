#!/usr/bin/env python3

from setuptools import setup, find_packages

readme = open('README.rst').read()

with open('njmls.py') as f:
    for line in f:
        if line.startswith('__version__ = '):
            version = eval(line.strip().split(' = ')[-1])
            break

if version is None:
    raise Exception("version not found")

setup(
    name='njmls',
    version=version,
    description='Python wrapper for njmls.',
    long_description=readme,
    author='Al Johri',
    author_email='al.johri@gmail.com',
    url='https://github.com/AlJohri/njmls',
    license='MIT',
    py_modules=['njmls'],
    install_requires=['requests', 'cssselect', 'lxml', 'PyYAML'],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
    ]
)
