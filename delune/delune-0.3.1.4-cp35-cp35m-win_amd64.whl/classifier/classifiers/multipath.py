"""
Experimental Classifier
2016.4.6
"""

from . import metaclassifier, termcluster
import delune

class Classifier (metaclassifier.Classifier):
	def __init__ (self, reader, analyzer, featset, use_top_features, logger = None):
		self.subcl = delune.NAIVEBAYES
		self.cluster = None
		metaclassifier.Classifier.__init__ (self, reader, analyzer, featset, use_top_features, logger)
		
	def setopt (self, **opts):	
		self.subcl = opts.get ("subcl", self.subcl)
		self.cluster = opts.get ("cluster", self.cluster)
		metaclassifier.Classifier.setopt (self, **opts)
		if self.cluster:
			self.cluster.setopt (**opts)

	def match (self, name):
		return name == "multipath"
		
	def guess (self, mem, qs, lang = "un", cond = ""):
		terms = self.cluster.getFeatures (mem, qs, lang)
		clusters = self.cluster.cluster (mem, qs, lang, terms)
		
		results = []
		for cluster in clusters:
			if self.verbose: self.logger ("cluster contains %d of %d terms" % (len (cluster), len (terms)))
			result = self.clfs [self.subcl].guess (mem, terms, lang, cond)			
			results.append (result)
			
		return metaclassifier.Classifier.merge_and_choice (self, results)
		

