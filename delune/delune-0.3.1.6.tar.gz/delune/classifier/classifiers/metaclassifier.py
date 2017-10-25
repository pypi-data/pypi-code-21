import math
import delune
from delune import _delune
from . import naivebayes

class Classifier (naivebayes.Classifier):
	def __init__ (self, reader, analyzer, featset, use_top_features, logger = None):
		self.clfs = {}
		naivebayes.Classifier.__init__ (self, None, None, {}, 0, logger)
				
	def setopt (self, **opts):
		self.clfs = opts.get ("clfs", self.clfs)
		naivebayes.Classifier.setopt (self, **opts)
			
	def match (self, name):
		return name == "meta"
	
	def merge_and_choice (self, res):
		nres = []
		for r in res:
			if not r: continue
			current_score = None
			for label, score in r:	
				if current_score is not None and score < current_score:
					break
				nres.append (label)
				current_score = score
		#print (nres)
		if not nres: return []
		score = 1 / len (nres)
		d = {}		
		for label in nres:
			try: d [label] += score
			except KeyError: d [label] = score

		k = list(d.items ())
		k.sort (key = lambda x: x [1], reverse = True)
		return k			
	
	def guess (self, mem, qs, lang = "un", cond = ""):
		result = []
		for name, classifier in list(self.clfs.items ()):
			try:
				subresult = classifier.guess (mem, qs, lang, cond)
				if not subresult:
					continue					
				
				#print (name, subresult)
				if type (subresult [0]) == type ([]):
					result.extend (subresult)
				else:	
					result.append (subresult)
			except:
				self.logger.trace ("engine")	
		
		return self.merge_and_choice (result)
		