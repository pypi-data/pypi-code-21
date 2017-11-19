from datetime import datetime
import json


class operation(object):


	def __init__(self, id=None, account=None, name=None,
	                        local_amount=None, local_currency=None,
				             date=None, active=True,
				             category=None, last_edited=None):
		self.id = id
		self.account = account
		self.name = name
		self.local_amount = local_amount
		self.local_currency = local_currency
		self.date = date
		self.active = active
		self.category = category
		self.last_edited = last_edited

	def json_data(self):
		_tmp = self.__dict__
		_tmp.pop('id', None)
		_tmp['date'] = str(self.date.date())
		return _tmp


	@staticmethod
	def json_serial(obj):
		"""JSON serializer for objects not serializable by default json code"""

		if isinstance(obj, (datetime)):
			return obj.isoformat()
		raise TypeError("Type %s not serializable" % type(obj))
