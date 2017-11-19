from datetime import datetime

class account (object):


	def __init__(self, id=None, name='', create=None, currency_id=None, archived=False, public=False):
		self.id = id
		self.name = name
		self.create = create
		self.currency = currency_id
		self.archived = archived
		self.public = public
