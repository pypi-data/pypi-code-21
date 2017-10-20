#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import codecs
import json
import sys




class AbstractDataModelContainer(object):

	def loadDataModel(self):
		raise NotImplementedError()
	#

	def storeDataModel(self, tables):
		raise NotImplementedError()
	#

#











