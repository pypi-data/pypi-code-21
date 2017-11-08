'''
      _               _ _
   __| |_      _____ | | | __ _
  / _` \ \ /\ / / _ \| | |/ _` |
 | (_| |\ V  V / (_) | | | (_| |
  \__,_| \_/\_/ \___/|_|_|\__,_|

  An official requests based wrapper for the Dwolla API.

  This file contains custom exception classes for dwolla-python
'''

class DwollaAPIException(Exception):
	def __init__(self, message, response):
		self.response = response
		super(DwollaAPIException, self).__init__(message)