#!/usr/bin/env python

from distutils.core import setup

setup(name='pyslackup',
      version='0.6',
      license='ISC',
      description='Wrapper for SlackClient',
      long_description=open('README.rst', 'r').read(),
      author='Christian Bryn',
      author_email='chr.bryn@gmail.com',
      url='https://github.com/epleterte/slackup',
      download_url='https://github.com/epleterte/slackup/archive/0.6.tar.gz',
      platform='Linux',
      packages=['slackup'],
      py_modules=['slackup'],
      keywords=['slack']
     )
