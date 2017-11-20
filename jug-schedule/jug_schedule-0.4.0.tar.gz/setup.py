# -*- coding: utf-8 -*-

import sys
try:
    import setuptools
except:
    sys.stdout.write("setuptools was not found.\nIf on Linux you may find it on your system's package manager\n")
    sys.exit(1)

exec(compile(open("jug_schedule/version.py").read(), "jug_schedule/version.py", "exec"))
long_description = open("README.rst").read()

classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development",
    "Topic :: System :: Distributed Computing",
    "Intended Audience :: Science/Research",
]

setuptools.setup(
    name="jug_schedule",
    version=__version__,  # noqa
    description="Automatic DRMAA scheduling with resource management for Jug",
    long_description=long_description,
    author="Renato Alves",
    author_email="alves.rjc@gmail.com",
    license="MIT",
    platforms=["Any"],
    classifiers=classifiers,
    url="https://gitlab.com/Unode/jug_schedule",
    packages=setuptools.find_packages(),
    install_requires=[
        "jug>1.4.0",
        "colorlog",
        "drmaa",
    ],
)
