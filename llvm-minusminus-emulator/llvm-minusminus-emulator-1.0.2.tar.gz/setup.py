#!/usr/bin/env python3
"""
Setup configuration for llvm--emulator.

Note that due to naming issues with egg/pypi, the program is known as
'llvm-minusminus-emulator' (without the 'quotes').

"""


from setuptools import setup

packages = ['llvm_emulator']

with open('pypi_readme.rst') as f:
    long_description = f.read()

setup(
    name='llvm-minusminus-emulator',
    version='1.0.2',
    description='A simple hacky emulator/debugger for LLVM--',
    long_description=long_description,
    url='https://gitlab.com/cfreksen/llvm--emulator',
    author='Casper Freksen',
    author_email='cfreksen@cs.au.dk',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: System :: Emulators',
        'Topic :: Software Development :: Debuggers',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Environment :: Console'
    ],
    keywords='llvm debugger',
    packages=packages,
    include_package_data=True,
    install_requires=[
        'ply >= 3'
    ],
    python_requires='~=3.5',
    package_data={},
    data_files=[],
    scripts=['bin/llvm--emulator']
)
