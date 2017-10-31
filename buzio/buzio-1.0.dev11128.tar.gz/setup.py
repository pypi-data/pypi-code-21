"""Setup.py."""
import datetime
from codecs import open
from os import path
from setuptools import setup, find_packages
from buzio import __version__


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

install_requires = [
    'unidecode',
    'colorama'
]

if 'dev' in __version__:
    now = datetime.datetime.now()
    release_number = (now - datetime.datetime(2017, 10, 24)
                      ).total_seconds() / 60
    version = "{}{}".format(__version__, int(release_number))
else:
    version = __version__

setup(
    name='buzio',
    version=version,
    description='Helpers for command line interaces (CLI) in terminal',
    long_description=long_description,
    author='Chris Maillefaud',
    include_package_data=True,
    # Choose your license
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='terminal input print colorama',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=install_requires
)
