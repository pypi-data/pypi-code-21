#!/usr/bin/env python

from distutils.core import setup

setup(name='camlib', author='Camille Huot', author_email='noemail@noemail.com',
  version = '0.0.1', url = 'http://github.com', 
  description='Python library suited to develop web apps using MVC pattern',
  packages = ['camlib'], package_dir= { 'camlib': 'camlib' }
 )
