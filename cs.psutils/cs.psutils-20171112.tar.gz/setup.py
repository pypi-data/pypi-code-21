#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.psutils',
  description = 'Assorted process management functions.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20171112',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
  install_requires = [],
  keywords = ['python2', 'python3'],
  long_description = '* stop: stop a process with a signal (SIGTERM), await its demise.\n* write_pidfile: save a process pid to a file\n* remove_pidfile: truncate and remove a pid file\n* PidFileManager: context manager for a pid file\n* run: run a command and optionally trace its dispatch.\n* pipefrom: dispatch a command with standard output connected to a pipe\n* pipeto: dispatch a command with standard input connected to a pipe\n* groupargv: break up argv lists to fit within the maximum argument limit',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.psutils'],
)
