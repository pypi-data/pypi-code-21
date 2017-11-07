import sys

from setuptools import setup

import gpython

args = {
    'name': 'gpython',
    'version': '1.2.0',
    'description': 'Python with optimus enablement',
    'author': 'Szabolcs Dombi',
    'author_email': 'cprogrammer1994@gmail.com',
    'license': 'MIT',
    'packages': ['gpython'],
    'platforms': ['any'],
}

setup(**args)
