#!/usr/bin/env python

from distutils.core import setup


setup(name='testypie',
      version='0.6.0',
      author='Ross Fenning',
      author_email='ross.fenning@gmail.com',
      py_modules=['testypie'],
      url='http://github.com/avengerpenguin/testypie',
      description='HTTP proxy that generates and loads from fixtures for testing.',
      license='GPLv3+',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      install_requires=[
          'Flask',
          'requests',
          'httplib2'
      ],
)
