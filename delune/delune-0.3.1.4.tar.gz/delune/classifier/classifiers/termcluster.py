from . import naivebayes
from delune import _delune
import delune
import threading


class Cluster:
	def __init__ (self, f1, threshold, choiceby, verbose = False):		
		self.name = f1
		self.threshold, self.choiceby = threshold, choiceby
		self.terms = {f1: None}
		self.ordered_terms = []
		self.current_socre = 0.0
		self.verbose = verbose
	
	def __contains__ (self, x):
		return (x in self.terms)
		
	def __len__ (self):
		return len (self.terms)
	
	def __str__ (self):
		return "cluster <%s> %s" % (self.name, " ".join (self.get_terms ()))

	def choice_max (self, mis):
		f2s = {}
		for f1 in self.terms:
			for f2, R in mis [f1].items ():				
				if f2 not in self.terms:
					f2s [f2] = None

		cand = None
		for f2 in f2s:
			t = []
			for f1 in self.terms:
				R = mis [f1][f2]
				t.append (R)			
			summi = sum (t)
			if self.choiceby == delune.AVG:
				score = summi / len (t)
			elif self.choiceby == delune.MIN:
				score = min (t)				
			else:
				raise AssertionError ("Unknown choice method: %s" % self.choiceby)
			if cand is None or score > cand [1]:
				cand = (f2, score)
		
		if cand is None:
			return 1
			
		f2, score = cand		
		
		if score <= self.threshold:			
			if self.verbose: self.ordered_terms.append ("%s>>" % f2)
			return f2
		
		self.terms [f2] = None
		self.current_socre = score
		if self.verbose: self.ordered_terms.append (f2)
	
	def get_terms (self):
		if self.ordered_terms:
			return self.ordered_terms
		else:
			return list (self.terms.keys ())			
	
	
class Classifier (naivebayes.Classifier):
	def __init__ (self, reader, analyzer, featset, use_top_features, logger = None):
		self.threshold = 1.0
		self.choiceby = delune.AVG
		self.scoreby = delune.IG
		self.scorer = None
		self.mis_cache = {}
		self.cached = 0		
		self.lock = threading.RLock ()
		naivebayes.Classifier.__init__ (self, reader, analyzer, featset, use_top_features, logger)		
	
	def match (self, name):
		return name == "termcluster"
		
	def setopt (self, **opts):	
		self.threshold = opts.get ("threshold", self.threshold)
		self.choiceby = opts.get ("choiceby", self.choiceby) 
		self.scoreby = opts.get ("scoreby", self.scoreby)
		self.scorer = getattr (_delune, "%smn" % self.scoreby.upper ())
		naivebayes.Classifier.setopt (self, **opts)
		
	def createCluster (self, term):
		return Cluster (term, self.threshold, self.choiceby, self.verbose)
		
	def createTermClusters (self, mem, terms):
		terms = [term for term in terms if term [0] in self.featset]
		if len (terms) <= 1:
			return [terms]
		
		featset = []
		for term, tf  in terms:
			findex = self.featset [term]
			df = self.reader.getDF (mem, term)
			featset.append ((term, findex, df))		
		featset.sort ()
		
		kd = 0
		mis = {}
		min_mi = None
		for term1, x, m in featset [:-1]:
			kd += 1
			if term1 not in mis: 
				mis [term1] = {}
			
			self.lock.acquire ()
			if term1 not in self.mis_cache:
				self.mis_cache [term1] = {}
			self.lock.release ()	
							
			for term2, y, n in featset [kd:]:
				#print (term1, term2)
				if term2 not in mis:
					mis [term2] = {}
				
				try:					
					self.lock.acquire ()
					R = self.mis_cache [term1][term2]					
				except KeyError:						
					self.lock.release ()
					co = self.getCoWord (mem, x, y)					
					if not co:
						R = -15.0
					else:
						R = self.scorer (self.reader.si.getN (), m, n, co)						
					self.lock.acquire ()
					self.mis_cache [term1][term2] = R
					self.cached += 1
					self.lock.release ()
				else:	
					self.lock.release ()
					
				mis [term1][term2] = R
				mis [term2][term1] = R
				
				if min_mi is None or R < min_mi [-1]:
					min_mi = (term1, term2, R)
		
		if self.verbose: self.logger ("co-word %d cached" % len (self.mis_cache))			
		if not mis: return [terms]

		f1, f2, R = min_mi
		if R > self.threshold:
			# single clusters
			if self.verbose: self.logger ("single cluster contains %s and %s with %2.3f" % min_mi)
			return [terms]
		if self.verbose: self.logger ("initial clusters are %s and %s with %2.3f" % min_mi)		

		clusters = {f1: self.createCluster (f1), f2: self.createCluster (f2)}
		dones = []
		while len (dones) < len (clusters):
			for term, cluster in list (clusters.items ()):
				if term in dones: continue					
				unchoiced = cluster.choice_max (mis)
				if unchoiced:
					dones.append (term)
					if unchoiced != 1 and not [x for x in clusters if unchoiced in x]:						
						clusters [unchoiced] = self.createCluster (unchoiced)
					
		terms = dict (terms)		
		term_clusters = []
		olen = len (clusters)
		clusters = self.diminish (clusters)		
		if self.verbose: self.logger ("clusters diminished from %d to %d" % (olen, len (clusters)))
			
		for cluster in clusters:
			if self.verbose: self.logger ("%s\n" % cluster)
			if len (cluster.terms) == 1: continue
			term_clusters.append ([(term, terms [term]) for term in cluster.terms])
		return term_clusters
	
	def diminish (self, clusters):
		cl = list (clusters.values ())
		cl.sort (key = lambda x: len (x.terms))		
			
		deletables = []	
		for i in range (len (cl) - 1):
			for j in range (i+1, len (cl)):				
				has_unique = {}
				for term in cl [i].terms:									
					if term not in cl [j].terms:
						has_unique [term] = None
				
				if not has_unique or (
					i + 1 == j 
					and len (cl [j]) - len (cl [i]) <  len (cl [j]) * 0.1
					and len (has_unique) <= max (1, len (cl [j]) * 0.1)
				):
					# merge cluster
					for newtrem in has_unique:
						cl [j].terms [newtrem] = None
					deletables.append (i)
					break
		
		new_clusters = []
		for i in range (len (cl)):
			if i not in deletables:
				new_clusters.append (cl [i])
		
		return new_clusters	
		
	def cluster (self, mem, qs, lang = "un", terms = None):
		if not terms:
			terms = self.getFeatures (mem, qs, lang)
		return self.createTermClusters (mem, terms)
				
	def guess (self, *args, **kargs):
		raise AttributeError
