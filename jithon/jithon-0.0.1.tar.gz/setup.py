# -*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

import os
import sys
import jithon
import warnings
import setuptools
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

if os.name == 'nt' and os.getenv('VS90COMNTOOLS') is None:
	if os.getenv('VS140COMNTOOLS') is not None:
		os.environ['VS90COMNTOOLS'] = os.getenv('VS140COMNTOOLS')
	elif os.getenv('VS120COMNTOOLS') is not None:
		os.environ['VS90COMNTOOLS'] = os.getenv('VS120COMNTOOLS')
	elif os.getenv('VS110COMNTOOLS') is not None:
		os.environ['VS90COMNTOOLS'] = os.getenv('VS110COMNTOOLS')
	elif os.getenv('VS100COMNTOOLS') is not None:
		os.environ['VS90COMNTOOLS'] = os.getenv('VS100COMNTOOLS')

path = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(path, 'README.rst')) as f:
	readme = f.read()

setup(
	name = 'jithon',
	version = jithon.__version__,
	url = 'http://github.com/ibelie/jithon',
	keywords = ('JIT', 'javascript', 'v8', 'WKWebView', 'jithon'),
	description = 'JIT module for python.',
	long_description = readme,

	author = 'joungtao',
	author_email = 'joungtao@gmail.com',
	license = 'MIT License',

	ext_modules = [Extension('jithon._jithon',
		sources = [
			'c/v8/v8.cc',
			'c/_jithon.c',
			'c/jithon.c',
			'c/port.c',
		],
		include_dirs = ['c'],
	)],

	classifiers=[
		'Development Status :: 3 - Alpha',
		# 'Development Status :: 4 - Beta',
		# 'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers',
		'Intended Audience :: Science/Research',
		'Intended Audience :: Education',
		'Topic :: Software Development :: Libraries',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3.5',
	],
	packages = list(setuptools.find_packages('.')),
)
