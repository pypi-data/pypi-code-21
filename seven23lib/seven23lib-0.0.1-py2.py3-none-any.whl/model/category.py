
class category(object):

	def __init__(self, id=None, account=None, name=None,
	                    description=None, parent=None,
	                    selectable=True, active=True):
		self.id = id
		self.account = account
		self.name = name
		self.description = description
		self.parent = parent
		self.selectable = selectable
		self.active =  active

	def json_data(self):
		_tmp = self.__dict__
		_tmp.pop('id', None)
		return _tmp
