#!/usr/bin/env python

# setup script for nmrglue

from distutils.core import setup
from codecs import open
from os import path
from kmdvalg import __version__

# Determine install position
package_name = 'kmdvalg'
import sys
from site import USER_SITE, USER_BASE
rela_path = USER_SITE.split(USER_BASE)[-1][1:]
install_to = path.join(rela_path, package_name)
print(rela_path)
print(install_to)

# get long description from README
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=package_name,
    version=__version__,
    description='A module for displaying danish Voting poll in Bokeh maps.',
    long_description=long_description,
    url='https://github.com/tlinnet/kmdvalg',
    download_url='https://github.com/tlinnet/kmdvalg/archive/%s.tar.gz'%__version__,
    author='Troels Schwarz-Linnet',
    author_email='tlinnet@gmail.com',
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'],
    requires=['bokeh', 'numpy', 'pandas', 'pickle', 'pyshp', 'beautifulsoup4', 'requests'],
    packages=['kmdvalg'],
    data_files=[(install_to, ['README.rst', 'LICENSE'])],
)