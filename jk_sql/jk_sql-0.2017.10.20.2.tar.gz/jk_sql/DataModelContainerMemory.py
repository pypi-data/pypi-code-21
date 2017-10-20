#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import codecs
import json
import sys

from .AbstractDataModelContainer import AbstractDataModelContainer



class DataModelContainerMemory(AbstractDataModelContainer):

	def __init__(self):
		self.__model = None
	#

	# ----------------------------------------------------------------

	def loadDataModel(self):
		return self.__model
	#

	def storeDataModel(self, tables):
		self.__model = {
			"version": 1,
			"tables": tables
		}
	#

#











