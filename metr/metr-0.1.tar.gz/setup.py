#!/usr/bin/env python

from setuptools import setup, find_packages
setup(
    name="metr",
    version="0.1",
    packages=find_packages(),
    # metadata for upload to PyPI
    author="Andrey Volkov",
    author_email="amadev@mail.ru",
    description="Simple metric service",
    license="MIT",
    keywords="analytics statistics",
    url="https://github.com/amadev/metr",
    install_requires=[
        'doan'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
)
