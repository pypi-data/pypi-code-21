

class currency(object):

	def __init__(self, id=None, name=None, sign=None, space=True, after_amount=True):
		self.id = id
		self.name = name
		self.sign = sign
		self.space = space
		self.after_amount = after_amount
