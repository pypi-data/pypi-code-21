#!/usr/bin/env python

import re
from setuptools import setup
import fastentrypoints

with open('prochestra/__init__.py') as source_file:
    source_text = source_file.read()
version = re.compile(r'^__version__\s*=\s*"(.*)"', re.M).search(source_text).group(1)

setup(name='Prochestra',
      packages=['prochestra'],
      entry_points={'console_scripts': ['prochestra=prochestra:command_line']},
      version=version,
      description='Run multiple processes with dependencies with one call.',
      author='Tobias Kiertscher',
      author_email='dev@mastersign.de',
      url='https://github.com/mastersign/prochestra',
      install_requires=['pyyaml >= 3.0.0'],
      )
