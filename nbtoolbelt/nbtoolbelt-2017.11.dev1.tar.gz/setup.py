"""
Setup file for nbtoolset

Copyright (c) 2017 - Eindhoven University of Technology, The Netherlands

This software is made available under the terms of the MIT License.
"""

from setuptools import setup, find_packages
import sys
from pathlib import Path

here = Path(__file__).parent  # location of this file in the file system

version_ns = {}  # name space for version
with (here / 'src' / 'nbtoolbelt' / '_version.py').open(encoding="utf8") as f:
    exec(f.read(), {}, version_ns)

#-----------------------------------------------------------------------------
# Minimal Python version sanity check
#-----------------------------------------------------------------------------

v = sys.version_info
if v[0] < 3 or (v[0] >= 3 and v[:2] < (3, 5)):
    error = "ERROR: %s requires Python version 3.5 or above." % name
    print(error, file=sys.stderr)
    sys.exit(1)

#-----------------------------------------------------------------------------
# get on with it
#-----------------------------------------------------------------------------

# I really prefer Markdown to reStructuredText.  PyPi does not.  This allows me
# to have things how I'd like, but not throw complaints when people are trying
# to install the package and they don't have pypandoc or the README in the
# right place.
try:
   import pypandoc
   long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
   long_description = ''

setup(
    name = version_ns['package_name'],
    version = version_ns['__version__'],
    author = 'Tom Verhoeff',
    author_email = 't.verhoeff@tue.nl',
    description = "Tools to work with Jupyter notebooks",
    long_description=long_description,
    url = 'https://gitlab.tue.nl/jupyter-projects/nbtoolbelt',
    license = 'MIT License',
    platforms = 'Linux, Mac OS X, Windows',
    keywords = ['Interactive', 'Interpreter', 'Shell', ],
    packages = find_packages('src'),
    install_requires = [
        'nbformat',
        'nbconvert',
        'numpy',
        'pandas',
    ],
    python_requires = '>=3.5',
    tests_require = {
        'test': ['pytest', 'pytest-mock'],
    },
    package_dir = {'': 'src'},
    package_data = {'': [
        'data/nbtoolbelt.json'
    ]},
    entry_points = {
        'console_scripts' : [
            'nbtb = nbtoolbelt.__main__:main_dispatch',
        ]
    },
    # zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Framework :: Jupyter',
    ],
)
