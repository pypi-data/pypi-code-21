#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

__version__ = '0.1.0'

setup(
    name='number2letters',
    version=__version__,
    description='Convertir les nombres en lettres.',
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/number2letters/number2letters',
    scripts=['scripts/number2letters'],
)
