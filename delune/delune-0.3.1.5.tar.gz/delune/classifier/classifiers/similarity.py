from . import tfidf
import math

class Classifier (tfidf.Classifier):
	def __init__ (self, reader, analyzer, featset, use_top_features, logger = None):
		tfidf.Classifier.__init__ (self, reader, analyzer, featset, use_top_features, logger)
		self.rfeatset = {}
		for k, v in self.featset.items ():
			self.rfeatset [v] = k
		self.fid_type = None	
		
	def match (self, name):
		return name in ("similarity", "sim")
	
	def check_type (self, ostream):
		if type (ostream [0]) is int:
			self.fid_type = True
		else:
			self.fid_type = False
						
	def guess (self, mem, qs, lang = "un", cond = ""):
		terms = self.getFeatures (mem, qs, lang)
		if not terms: return []
		
		K = 2
		A = 0.0
		d = []
		result = []
		comp = {}
		tfc = {}
		TF = 0
		
		for term, tf in terms:
			TF += math.pow (tf, 2.0)
		TF = math.sqrt (TF)

		for term, tf in terms:
			try: 
				tfv = tfc [tf]
			except KeyError:
				tfv = float (tf) / TF
				tfc [tf] = tfv
			df = self.reader.getDF (mem, term)
			fid = self.featset [term]
			comp [fid] = tfv * self.reader.getIDF (df)
			A += math.pow (comp [fid], 2.0)
		A = math.sqrt (A)

		res = self.query (terms, cond, self.fetchcount, lang)
		if res ["total"] == 0:
			return []
		
		if self.fid_type is None:			
			self.check_type (res ["result"][0][0][1])
		
		for row in res ["result"]:
			cla, ostream = row [0][:2]			
			if not ostream: continue
				
			B = C = 0.0
			TF = 0
			tfc = {}
			
			if self.fid_type:
				stream = []			
				for i in range (0, len (ostream), 2):
					if ostream [i] in self.rfeatset:
						stream.append ((ostream [i], ostream [i + 1]))
			else:
				stream = [(self.featset [term], tf) for term, tf in ostream if term in self.featset]
					
			if not stream: continue	
				
			for fid, tf in stream:
				TF += math.pow (tf, 2.0)
			if not TF:continue
			TF = math.sqrt (TF)
			
			for fid, tf in stream:
				try: 
					tfv = tfc [tf]
				except KeyError:
					tfv = float (tf) / TF
					tfc [tf] = tfv
				
				df = self.reader.getDF (mem, self.rfeatset [fid])				
				tfidf = tfv * self.reader.getIDF (df)
				B += math.pow (tfidf, 2.0)
			
				if fid in comp:
					C += comp [fid] * tfidf
			
			if B:
				result.append ((cla, C / (A * math.sqrt (B))))

		return self.revise (result)
	
	def revise (self, result):
		result.sort (key = lambda x: x [1], reverse = True)
		return result
