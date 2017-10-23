from . import similarity
import math

class Classifier (similarity.Classifier):
	def match (self, name):
		return name in ("rocchio",)
	
	def revise (self, result):
		s = {}
		for cla, sim in result:
			try: 
				s [cla] += sim
			except KeyError:
				s [cla] = sim	
		result = list (s.items ())
		result.sort (key = lambda x: x [1], reverse = True)
		return result
		
