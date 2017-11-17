"""Build pokrok.
"""
import os.path
import sys

from setuptools import setup, find_packages
import versioneer

if sys.version_info < (3, 4):
    sys.stdout.write("At least Python 3.4 is required.\n")
    sys.exit(1)

setup(
    name = 'pokrok',
    version = versioneer.get_version(),
    cmdclass = versioneer.get_cmdclass(),
    author = 'John Didion',
    author_email = 'johndidion@gmail.com',
    url = 'https://github.com/jdidion/pokrok',
    description = 'Simple API for progress bars using any of several supported libraries',
    license = 'MIT',
    packages = find_packages(),
    tests_require = ['pytest'], #, 'jinja2', 'pysam'],
    extras_require = {
        'progressbar' : ['progressbar2'],
        'tqdm' : ['tqdm'],
    },
    entry_points = {
        'pokrok' : [
            'tqdm=pokrok.plugins.tqdm:TqdmProgressMeterFactory'
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ]
)
