import sys
from setuptools import setup

version = '0.0.2'

if sys.argv[-1] == 'check-version':
    import os
    tag = os.environ.get('TRAVIS_TAG', '')
    if tag != '' and version != tag:
        sys.stderr.write("mismatch between version=%s and git tag=%s\n" % (version, tag))
        sys.exit(1)
    else:
        sys.exit(0)

setup(
    name='frc3223-azurite',
    version=version,
    author='Ellery Newcomer',
    author_email='ellery-newcomer@utulsa.edu',
    url='https://github.com/Retro3223/azurite',
    packages=[
        'frc3223_azurite',
    ],
    description='miscellaneous utilities for jupyter notebooks',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)

