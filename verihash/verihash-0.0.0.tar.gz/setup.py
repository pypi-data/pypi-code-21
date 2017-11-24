#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = []
test_requirements = []

setup(
    name="verihash",
    version="0.0.0",
    description="Format-independent structured hashing algorithm",
    long_description="Structured hashing algorithm that works across multiple formats (Veriform, TJSON)",
    author="Tony Arcieri",
    author_email="bascule@gmail.com",
    url="https://github.com/zcred/verihash",
    packages=find_packages(exclude=["tests"]),
    package_dir={"verihash": "verihash"},
    include_package_data=True,
    install_requires=[],
    license="MIT license",
    zip_safe=False,
    keywords=["authentication", "cryptography", "security", "serialization", "merkle"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
    ],
    test_suite="tests",
    tests_require=[]
)
