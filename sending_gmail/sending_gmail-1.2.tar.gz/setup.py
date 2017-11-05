#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 23:06:03 2017

@author: Pera
"""
from distutils.core import setup

setup(
  name = 'sending_gmail',
  packages = ['sending_gmail'], # this must be the same as the name above
  version = '1.2',
  description = 'Send simple text e-mails on behave of your gmail account',
  author = 'Petar',
  author_email = 'petronije2002@gmail.com',
  url = 'https://github.com/petronije2002/sending_gmail', # use the URL to the github repo
  download_url = '', # I'll explain this in a second
  keywords = ['send gmail', 'google gmail API', 'example send e-mail'], # arbitrary keywords
  install_requires=[
          'google-api-python-client',
      ], 
 classifiers = [],
)















#from setuptools import setup

#setup(name='sending_gmail',                   # This is the name of your PyPI-package.
#      version='0.8',                          # Update the version number for new releases
#      scripts=['send_gmail.py'])                 # The name of your scipt, and also the command you'll be using for calling it)
