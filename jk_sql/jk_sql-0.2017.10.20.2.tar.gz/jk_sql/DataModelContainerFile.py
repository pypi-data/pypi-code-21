#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import codecs
import json
import sys

from .AbstractDataModelContainer import AbstractDataModelContainer



class DataModelContainerFile(AbstractDataModelContainer):

	def __init__(self, modelFilePath):
		self.__modelFilePath = modelFilePath
	#

	# ----------------------------------------------------------------

	def loadDataModel(self):
		if os.path.isfile(self.__modelFilePath):
			with codecs.open(self.__modelFilePath, "r") as f:
				jsonRawModel = json.load(f)
				assert jsonRawModel["version"] == 1
				return jsonRawModel
		else:
			return None
	#

	def storeDataModel(self, tables):
		jsonRawModel = {
			"version": 1,
			"tables": []
		}

		for t in tables:
			jsonRawModel["tables"].append(t.toJSON())

		with codecs.open(self.__modelFilePath, "w") as f:
			json.dump(jsonRawModel, f, indent="\t")
	#

#











