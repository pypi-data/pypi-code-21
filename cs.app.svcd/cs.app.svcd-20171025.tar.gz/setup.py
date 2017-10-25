#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.app.svcd',
  description = 'SvcD class and "svcd" command to run persistent service programmes.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20171025',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
  entry_points = {'console_scripts': ['svcd = cs.app.svcd:main']},
  install_requires = ['cs.app.flag', 'cs.env', 'cs.logutils', 'cs.pfx', 'cs.psutils', 'cs.sh'],
  keywords = ['python2', 'python3'],
  long_description = 'This provides the features one wants from a daemon\nfor arbitrary commands providing a service:\n\n* process id (pid) files for both svcd and the service command\n* filesystem visible status (command running, service enabled)\n  via `cs.app.flag <https://pypi.org/project/cs.app.flag/>`_\n* command restart if the command exits\n* command control (stop, restart, disable)\n  via `cs.app.flag <https://pypi.org/project/cs.app.flag/>`_\n* test function to monitor for service viability;\n  if the test function fails, do not run the service.\n  This typically monitors something like\n  network routing (suspend service while laptop offline)\n  or a ping (suspend ssh tunnel while target does not answer pings).\n* signature function to monitor for service restart;\n  if the signature changes, restart the service.\n  This typically monitors something like\n  file contents (restart service on configuration change)\n  or network routing (restart ssh tunnel on network change)\n* callbacks for service command start and end,\n  for example to display desktop notifications\n\nI use this to run persistent ssh port forwards\nand a small collection of other personal services.\nI have convenient shell commands to look up service status\nand to start/stop/restart services.\n\nSee `cs.app.portfwd <https://pypi.org/project/cs.app.portfwd/>`_\nwhich I use to manage my ssh tunnels;\nit is a single Python programme\nrunning multiple ssh commands, each via its own SvcD instance.',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.app.svcd'],
)
