import math
from delune import _delune

class Classifier:
	def __init__ (self, reader, analyzer, featset, use_top_features, logger = None):
		self.reader = reader
		self.analyzer = analyzer
		self.featset = featset
		self.logger = logger
		self.numfeat = len (self.featset)
		self.use_top_features = use_top_features		
		self.verbose = False
		self.setopt ()
			
	def setopt (self, **opts):
		self.verbose = opts.get ("verbose", self.verbose)
	
	def getopt (self, name):
		pass
				
	def match (self, name):
		return name in ("nb", "bayes", "naivebayes")
	
	def close (self):
		pass
	
	def getCoWord (self, mem, t1, t2):
		#(findex, co-freq)
		k = self.reader.getCoOccurrence (mem, t1, t2)
		if k is None:
			return 0
		return k [1]	
				
	def getFeatures (self, mem, qs, lang):
		if type (qs) is list:
			return qs
		terms = self.analyzer.term (qs, lang)		
		#print ([term for term in terms if term [0] in self.featset])
		if not terms: return []
		return self.reader.getFeatures (
			mem, 
			[term for term in terms if term [0] in self.featset], 
			self.numfeat, 
			self.use_top_features
			)
			
	def guess (self, mem, qs, lang = "un", cond = ""):
		terms = self.getFeatures (mem, qs, lang)
		if not terms: return []
		
		classifier = _delune.Classifier (mem, self.reader.corpus, self.numfeat, self.reader.getN ())
		for term, tf in terms:
			if self.reader.readTermInfo (mem, term):
				classifier.load ()
				has_prob = classifier.bayes (tf)
				if has_prob == 0:
					# all zero probability, abort
					return []

		result = classifier.get (0, self.reader.numpools)
		classifier.close ()
		return self.reader.translate (result)
	
	