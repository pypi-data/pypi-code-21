"""
describes this package for distribution and installation
"""

import os
from setuptools import setup


def _read_file_for_long_description(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# pylint: disable=exec-used
# get version string variable __version__
exec(open('dploy/version.py').read())

DESCRIPTION = "Provides functionality similar to GNU Stow as a cross platform CLI tool and Python 3 module"

setup(
    name='dploy',
    # pylint: disable=undefined-variable
    version=__version__,
    download_url='https://github.com/arecarn/dploy/tarball/' + __version__,
    license='MIT',
    description=DESCRIPTION,
    long_description=_read_file_for_long_description('README.md'),
    author='Ryan Carney',
    author_email='arecarn@gmail.com',
    url='https://github.com/arecarn/dploy',
    packages=['dploy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={'console_scripts': ['dploy=dploy.__main__:main']},
)
