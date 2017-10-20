#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import codecs
import json
import sys

import sqlite3

from .SQLiteDB import *
from .DataModelContainerFile import *
from .DataModelContainerMemory import *





class DBManager(object):

	@staticmethod
	def createSQLiteDB(dirPath, bOverwriteIfExists = False):
		assert isinstance(dirPath, str)

		if not os.path.isdir(dirPath):
			os.mkdir(dirPath)

		dataFile = os.path.join(dirPath, "data.db")
		modelFile = os.path.join(dirPath, "model.json")
		if os.path.isfile(dataFile) and os.path.isfile(modelFile):
			if not bOverwriteIfExists:
				raise Exception("Database already exists at: " + dirPath)

		if os.path.isfile(dataFile):
			os.unlink(dataFile)
		if os.path.isfile(modelFile):
			os.unlink(modelFile)

		return SQLiteDB(
			sqlite3.connect(dataFile),
			DataModelContainerFile(modelFile)
			)
	#

	@staticmethod
	def createSQLiteMemoryDB():
		return SQLiteDB(
			sqlite3.connect(":memory:"),
			DataModelContainerMemory()
			)
	#

	@staticmethod
	def openSQLiteDB(dirPath):
		assert isinstance(dirPath, str)

		if not os.path.isdir(dirPath):
			raise Exception("Directory does not exist!")

		dataFile = os.path.join(dirPath, "data.db")
		modelFile = os.path.join(dirPath, "model.json")
		if not os.path.isfile(dataFile) or not os.path.isfile(modelFile):
			raise Exception("No database exists at specified location: " + dirPath)

		return SQLiteDB(
			sqlite3.connect(dataFile),
			DataModelContainerMemory()
			)
	#

#











