#-*- coding: utf-8 -*-
# Copyright 2017 ibelie, Chen Jie, Joungtao. All rights reserved.
# Use of this source code is governed by The MIT License
# that can be found in the LICENSE file.

__author__ = 'Joungtao'
__version__ = '0.0.1'

try:
	import _jithon
	setPath = _jithon.setPath
except:
	_jithon = None

def p(text):
	print text

def delegate(name, args):
	globals()[name](*args)

try:
	from extension import *
except:
	pass
