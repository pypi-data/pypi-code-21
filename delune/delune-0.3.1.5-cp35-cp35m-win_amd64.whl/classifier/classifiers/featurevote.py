from . import naivebayes
from delune import _delune

class Classifier (naivebayes.Classifier):
	def match (self, name):
		return name in ("fv", "featurevote")
	
	def guess (self, mem, qs, lang = "un", cond = ""):
		if type (qs) is type ([]):
			terms = qs
		else:	
			terms = self.getFeatures (mem, qs, lang)
		if not terms: return []
		
		classifier = _delune.Classifier (mem, self.reader.corpus, self.numfeat, self.reader.getN ())
		for term, tf  in terms:			
			if self.reader.readTermInfo (mem, term):
				classifier.load ()
				classifier.featurevote (tf)

		result = classifier.get (0, self.reader.numpools)
		classifier.close ()
		return self.reader.translate (result)
