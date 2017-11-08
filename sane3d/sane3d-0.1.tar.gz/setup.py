#!/usr/bin/env python

from distutils.core import setup

setup(name='sane3d',
      version='0.1',
      description='A sane interface to mplot3d',
      author='Johannes Kulick',
      author_email='johannes@mailless.org',
      url='http://github.com/hildensia/sane3d',
      install_requires=['matplotlib'],
      packages=['sane3d']
)
