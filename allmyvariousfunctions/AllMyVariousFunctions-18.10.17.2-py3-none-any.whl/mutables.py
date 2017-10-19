class mutables_class:
	variables = {}
	def add(self, key, value):
		self.variables[key] = value
		return True
	def sub(self, key):
		try:
			self.variables.pop(key, None)
			return True
		except:
			return False			
	def get(self, key):
		try:
			return self.variables[key]
		except:
			return False
	def set(self, key, value):
		try:
			self.variables[key]
			self.variables[key] = value
			return True
		except:
			return False
	def itr(self):
		sets = ''
		for i in self.variables:
			sets += i + ' = ' + self.variables[i] + '\n'
		return sets
	def itr_var(self):
		sets = ''
		for i in self.variables:
			sets += i + '\n'
		return sets
	def itr_val(self):
		sets = ''
		for i in self.variables:
			sets += self.variables[i] + '\n'
		return sets
mutables = mutables_class()