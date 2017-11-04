#! /usr/bin/env python

"""Setup file to build and install arandomness PyPI package

Copyright:

    setup.py build and install arandomness PyPI package
    Copyright (C) 2017  Alex Hyer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup

__author__ = 'Alex Hyer'
__email__ = 'theonehyer@gmail.com'
__license__ = 'GPLv3'
__maintainer__ = 'Alex Hyer'
__status__ = 'Alpha'
__version__ = '0.1.0rc3'

setup(name='arandomness',
      version=__version__,
      description='An arandom assortment of random modules',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      keywords='arandomness TheOneHyer',
      url='https://github.com/TheOneHyer/arandomness',
      download_url='https://github.com/TheOneHyer/arandomness/tarball/'
                   '{0}'.format(__version__),
      author='Alex Hyer',
      author_email='theonehyer@gmail.com',
      license='GPLv3',
      packages=[
          'arandomness',
          'arandomness.argparse',
          'arandomness.string',
          'arandomness.trees'
      ],
      requires=[
          'prettytable'
      ],
      include_package_data=True,
      zip_safe=False
      )
