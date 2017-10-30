#!/usr/bin/env python
from setuptools import setup
setup(
  name = 'cs.result',
  description = 'Result and friends: callable objects which will receive a value at a later point in time.',
  author = 'Cameron Simpson',
  author_email = 'cs@cskk.id.au',
  version = '20171030.1',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Topic :: Software Development :: Libraries :: Python Modules', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'],
  install_requires = ['cs.logutils', 'cs.obj', 'cs.seq', 'cs.py3'],
  keywords = ['python2', 'python3'],
  long_description = 'A Result is the base class for several callable subclasses\nwhich will receive values at a later point in time,\nand can also be used standalone without subclassing.\n\nA call to a Result will block until the value is received or the Result is cancelled,\nwhich will raise an exception in the caller.\nA Result may be called by multiple users, before or after the value has been delivered;\nif the value has been delivered the caller returns with it immediately.\nA Result\'s state may be inspected (pending, running, ready, cancelled).\nCallbacks can be registered via an Asychron\'s .notify method.\n\nAn incomplete Result can be told to call a function to compute its value;\nthe function return will be stored as the value unless the function raises an exception,\nin which case the exception information is recorded instead.\nIf an exception occurred, it will be reraised for any caller of the Result.\n\nTrite example::\n\n  R = Result(name="my demo")\n\n  Thread 1:\n    value = R()\n    # blocks...\n    print(value)\n    # prints 3 once Thread 2 (below) assigns to it\n\n  Thread 2:\n    R.result = 3\n\n  Thread 3:\n    value = R()\n    # returns immediately with 3\n\nYou can also collect multiple Results in completion order using the report() function::\n\n  Rs = [ ... list of Results or whatever type ... ]\n  ...\n  for R in report(Rs):\n    x = R()     # collect result, will return immediately\n    print(x)    # print result',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.result'],
)
