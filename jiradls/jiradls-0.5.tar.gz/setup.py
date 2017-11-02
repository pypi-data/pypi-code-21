from __future__ import absolute_import, division

import io
import os
import re
import sys

from setuptools import find_packages, setup

# cf.
# https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
def read(*names, **kwargs):
  with io.open(
    os.path.join(os.path.dirname(__file__), *names),
    encoding=kwargs.get("encoding", "utf8")
  ) as fp:
    return fp.read()

def find_version(*file_paths):
  version_file = read(*file_paths)
  version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                            version_file, re.M)
  if version_match:
    return version_match.group(1)
  raise RuntimeError("Unable to find version string.")

setup(
  name='jiradls',
  description='JIRA without a GUI is less bad than JIRA with a GUI, but still JIRA',
  license='BSD',
  url='https://github.com/Anthchirp/python-jira',
  author='Markus Gerstel',
  author_email='markus.gerstel@diamond.ac.uk',
  download_url="https://github.com/Anthchirp/python-jira/releases",
  version=find_version("jiradls", "__init__.py"),
  install_requires=[
    'colorama',
    'cryptography',
    'ipython',
    'jira',
    'pyjwt',
  ],
  entry_points = {
    'console_scripts': ['jira=jiradls.command_line:main'],
  },
  packages=find_packages(),
  setup_requires=[
    'pytest-runner',
  ],
  tests_require=[
    'mock',
    'pytest'
  ],
  classifiers = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Bug Tracking',
  ]
)
