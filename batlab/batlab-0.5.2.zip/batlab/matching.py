from statistics import variance
class pack:
	def __init__(self):
		self.modules = set()
	def add(self,module):
		self.modules.add(module)
		
class module:
	def __init__(self):
		self.cells = set()
		self.capacity_score = None
		self.impedance_score = None
	def add(self,cell):
		self.cells.add(cell)
	def score(self):
		self.capacity_score = variance(self.cells.chrg_capacity) + variance(self.cells.dchrg_capacity)
		self.impedance_score = variance(self.cells.chrg_capacity) + variance(self.cells.dchrg_capacity)
			
		

class cell:
	def __init__(self):
		self.chrg_capacity = None
		self.dchrg_capacity = None
		self.chrg_impedance = None
		self.dchrg_impedance = None

	