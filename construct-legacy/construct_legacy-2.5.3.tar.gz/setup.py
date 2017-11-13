#!/usr/bin/env python
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

HERE = os.path.dirname(__file__)
exec(open(os.path.join(HERE, "construct_legacy", "version.py")).read())

setup(
    name = "construct_legacy",
    version = version_string, #@UndefinedVariable
    packages = [
        'construct_legacy',
        'construct_legacy.lib', 
        'construct_legacy.formats', 
        'construct_legacy.formats.data', 
        'construct_legacy.formats.executable', 
        'construct_legacy.formats.filesystem', 
        'construct_legacy.formats.graphics',
        'construct_legacy.protocols', 
        'construct_legacy.protocols.application', 
        'construct_legacy.protocols.layer2', 
        'construct_legacy.protocols.layer3', 
        'construct_legacy.protocols.layer4',
    ],
    license = "MIT",
    description = "A powerful declarative parser/builder for binary data (legacy version - 2.5)",
    long_description = open(os.path.join(HERE, "README.rst")).read(),
    platforms = ["POSIX", "Windows"],
    url = "http://construct.readthedocs.org",
    author = "Tomer Filiba, Corbin Simpson",
    author_email = "tomerfiliba@gmail.com, MostAwesomeDude@gmail.com",
    install_requires = ["six"],
    requires = ["six"],
    provides = ["construct_legacy"],
    keywords = "construct, declarative, data structure, binary, parser, builder, pack, unpack",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
    ],
)
