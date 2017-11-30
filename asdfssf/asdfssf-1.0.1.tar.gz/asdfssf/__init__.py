#!/usr/bin/env python3
import os

def readfile(filepath):
	try:
		with open(filepath) as fileread:
			return fileread.readlines()
	except Exception as e:
		print(str(e))