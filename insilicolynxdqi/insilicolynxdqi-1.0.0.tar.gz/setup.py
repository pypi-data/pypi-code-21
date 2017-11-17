#!/usr/bin/python

'''
*******************************************************************************************************************************************

Copyright (C) 2017 InSilicoLynx Limited
All Rights Reserved.

This file is part of insilicolynxdqi.

The insilicolynxdqi software is covered by a BSD 3-clause license that is included in the LICENSE.txt file distributed with this software.

*******************************************************************************************************************************************
'''

'''
*******************************************************************************************************************************************

Change log

17th November 2017: First release written by Mark Wenlock.

*******************************************************************************************************************************************
'''

from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
		
def getReadMeText():
    with open("README.txt") as fileToRead:
        return fileToRead.read()

setup(
	name="insilicolynxdqi",
	
	version="1.0.0",

	description="Medicinal Chemistry tool for calculating drug suitability parameters of compounds.",
	
	long_description=getReadMeText(),

	keywords="insilicolynxdqi",

	url="http://www.insilicolynx.com/",

    author="InSilicoLynx Limited",
     
    author_email="contact@insilicolynx.com",

	license="BSD 3-clause",
	
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		'Environment :: Console',
		'Intended Audience :: Science/Research',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3',
		"Topic :: Scientific/Engineering :: Chemistry"
		],
	
	packages=[
				"insilicolynxdqi",
				"insilicolynxdqi.calculations",
				"insilicolynxdqi.docs",
				"insilicolynxdqi.docs.examples",
				"insilicolynxdqi.docs.templates",
				"insilicolynxdqi.resources",
				"insilicolynxdqi.run",
				"insilicolynxdqi.system"	
				],
			
	package_data={
		"": ["*.txt"]
		},
	
	platforms='Linux, Win32',
	
	scripts=[
		"bin/insilicolynxdqi_analyse_calculations.py",
		"bin/insilicolynxdqi_generate_scenarios.py",
		"bin/insilicolynxdqi_perform_calculations.py",
		"bin/insilicolynxdqi_run.py"
		],
	
	python_requires='>=2.7, <4',
	
	)

