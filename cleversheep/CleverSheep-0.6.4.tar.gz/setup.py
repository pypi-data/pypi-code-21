#!/usr/bin/env python
"""Setup script for the CleverSheep."""

from distutils.core import setup

import CleverSheep

packages = ['CleverSheep',
            'CleverSheep.App',
            'CleverSheep.Extras',
            'CleverSheep.Log',
            'CleverSheep.Prog',
            'CleverSheep.Sys',
            'CleverSheep.TTY_Utils',
            'CleverSheep.Test',
            'CleverSheep.Test.Tester',
            'CleverSheep.Test.Mock',
            'CleverSheep.TextTools',
            'CleverSheep.VisTools',
            ]

setup(name='CleverSheep',
      version=CleverSheep.version_string,
      description='A collection of packages for high level asynchronous testing.',
      author='Paul Ollis, Laurence Caraccio',
      author_email='cleversheepframework@gmail.com',
      url='https://lcaraccio.gitlab.io/clever-sheep/api/index.html',
      packages=packages,
      py_modules=[],
      scripts=[],
      long_description=CleverSheep.__doc__,
      license="MIT License",

      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2',
          'Natural Language :: English'
      ]
      )
