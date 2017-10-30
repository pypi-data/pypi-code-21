#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.logutils',
  description = 'Logging convenience routines.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20171030',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
  install_requires = ['cs.ansi_colour', 'cs.lex', 'cs.obj', 'cs.pfx', 'cs.py.func', 'cs.upd'],
  keywords = ['python2', 'python3'],
  long_description = 'The logging package is very useful, but a little painful to use.\nThis package provides low impact logging setup and some extremely useful if unconventional context hooks for logging.\n\nThe logging verbosity output format has different defaults based on whether an output log file is a tty and whether the environment variable $DEBUG is set, and to what.\n\nOn terminals warnings and errors get ANSI colouring.\n\nA mode is available that uses cs.upd.\n\nSome examples:\n--------------\n\nProgram initialisation::\n\n  from cs.logutils import setup_logging\n\n  def main(argv):\n    cmd = os.path.basename(argv.pop(0))\n    setup_logging(cmd)\n\nBasic logging from anywhere::\n\n  from cs.logutils import info, warning, error\n  [...]\n  def some_function(...):\n    [...]\n    error("nastiness found! bad value=%r", bad_value)',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.logutils'],
)
