# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from setuptools import setup

with open("README") as f:
   description= f.read()

setup(name= 'abus',
   version= '4',
   description= 'Abingdon Backup Script',
   long_description= description,
   author= 'Cornelius Grotjahn',
   author_email= 's1@tempaddr.uk',
   license= 'MIT',
   packages= ['abus'],
   install_requires= ['cryptography'],
   zip_safe= False,
   entry_points = { 'console_scripts': ['abus=abus:entry_point'], }, # script=package:function
   classifiers= [
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3 :: Only',
      'Development Status :: 3 - Alpha',
      'License :: OSI Approved :: MIT License',
      'Topic :: System :: Archiving :: Backup',
      ],
   )
