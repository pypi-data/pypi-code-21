# -*- coding: UTF-8 -*-
# Copyright © 2017 Cornelius Grotjahn - This file is covered by the LICENCE file in the project root directory.
from setuptools import setup

with open("README") as f:
   readme= f.read()

setup(name= 'abus',
   version= '6',
   description= 'Abingdon Backup Script',
   long_description= readme,
   author= 'Cornelius Grotjahn',
   author_email= 's1@tempaddr.uk',
   license= 'MIT',
   packages= ['abus','abus/cornelib'],
   package_data={'abus': ["schema-3.sql", "upgrade-2.sql", "upgrade-1.sql"]},
   install_requires= ['cryptography'],
   zip_safe= False,
   entry_points = { 'console_scripts': ['abus=abus:entry_point'], }, # script=package:function
   classifiers= [
      'Programming Language :: Python :: 3.6',
      'Programming Language :: Python :: 3 :: Only',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: MIT License',
      'Topic :: System :: Archiving :: Backup',
      ],
   url="https://pypi.python.org/pypi/abus",
   )
