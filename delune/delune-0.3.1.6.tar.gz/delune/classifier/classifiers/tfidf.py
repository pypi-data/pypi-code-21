from . import naivebayes
import math

class Classifier (naivebayes.Classifier):
	
	def setopt (self, **opts):		
		self.fetchcount = int (opts.get ("topdoc", 100))
		naivebayes.Classifier.setopt (self, **opts)
	
	def getopt (self, name):
		if name == "fetch":
			return self.fetchcount
		
	def match (self, name):
		return name in ("tfidf",)
	
	def query (self, terms, surfix, fetch = 10, lang = "un"):
		qs = "%s (%s)" % (surfix and "(%s)" % surfix or "", " or ".join ([x [0] for x in terms]))
		res = self.reader.searcher.do_query (
			qs, 0, self.fetchcount == 0 and 100000000 or self.fetchcount, 
			sort = self.fetchcount > 0 and "tfidf" or "", # self.fetchcount == -1, then fetch all
			lang = lang,
			analyze = False, limit = False
		)
		return res
		
	def guess (self, mem, qs, lang = "un", cond = ""):
		terms = self.getFeatures (mem, qs, lang)
		if not terms: return []
					
		res = self.query (terms, cond, self.fetchcount, lang)
		if res ["total"] == 0:
			return []
				
		result = []
		for row  in res ["result"]:
			cla, score = row [0][0], row [-1]
			result.append ((cla, score))		
		return result
