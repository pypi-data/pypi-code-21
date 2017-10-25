class TinyIntError(Exception):
	def __init__(self):
		self.message = "El numero no cuenta con la mierda esa"

	def __str__(self):
		return self.message
