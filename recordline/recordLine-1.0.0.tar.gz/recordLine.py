#!/usr/bin/env python

import os

def load(location):
	'''Return a recordLine object. location is the path to the json file.'''
	return recordLine(location)

class recordLine(object):

	def __init__(self, location):
		'''Creates a database object and loads the data from the location path.
If the file does not exist it will be created on the first update.'''
		self.load(location)

	def load(self, location):
		'''Loads, reloads or changes the path to the db file.'''
		location = os.path.expanduser(location)
		self.loco = location
		return True

	def new(self, line):
		with open(self.loco, "a") as f:
			f.writelines(line + "\n")
			f.close()
		return True

	def show(self):
		with open(self.loco, 'r') as f:
			data = []
			for line in f.read().split():
				data.append(line.rstrip())
			f.close()
		return data

	# for python3
	def __repr__(self):
		filename = self.loco.split("/")[-1]
		return "<%s>" % filename

	# for python3
	def __str__(self):
		filename = self.loco.split("/")[-1]
		return filename

	# for python2
	def __unicode__(self):
		filename = self.loco.split("/")[-1]
		return filename
