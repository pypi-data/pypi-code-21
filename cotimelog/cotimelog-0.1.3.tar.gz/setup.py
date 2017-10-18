import os
from setuptools import setup
from cotimelog import __author__, __version__


requires = []
try:
    import portalocker
except:
    requires.append('portalocker')

setup(
    name="cotimelog",
    version=__version__,
    author=__author__,
    author_email="yaleidu93@gmail.com",
    description="mixins for tornado",
    license="Apache License, Version 2",
    keywords=["log", 'concurrent'],
    url="https://github.com/badbye/timelog.git",
    packages=['cotimelog'],
    install_requires=requires,
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)


