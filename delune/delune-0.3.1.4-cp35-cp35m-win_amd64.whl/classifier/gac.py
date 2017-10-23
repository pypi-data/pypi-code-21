import delune
from pprint import pprint
import json
import codecs
import os
import requests

class Collection:
	def __init__ (self, ratio = 0.9, front = 1):		
		self.ratio = ratio
		self.front = front
		if ratio == 1.0 and not front:
			self.ratio = 0.9			
		self.skipped = 0
		self.skipping = 1
		self.__totaldoc = 0
		self.__numdoc = 0
		self.setup ()
	
	def __skip (self):	
		self.skipping = 1	
		if self.offset:
			if self.offset > self.__totaldoc:				
				raise IndexError ("offset is larger than total documents")
			while self.__numdoc < self.offset:
				self.get ()
				self.__numdoc += 1
		self.skipping = 0
		
	def __iter__ (self):
		return self
	
	def __next__ (self):
		if not self.skipped:
			self.__skip ()
			self.skipped = 1
			
		doc = self.get ()
		self.__numdoc += 1
			
		if doc is None or self.__numdoc >= self.__totaldoc or self.__numdoc >= (self.offset + self.limit):
			self.teardown ()
			raise StopIteration			
		return doc
	
	def reget (self):
		self.__numdoc += 1
		return self.get ()
		
	def get_total (self):
		return self.__totaldoc
	
	@property
	def index (self):
		return self.__numdoc
		
	def set_total (self, num):
		self.__totaldoc = num
		if self.front:
			self.offset = 0
			self.limit = int (self.__totaldoc * self.ratio)
		else:
			self.offset = int (self.__totaldoc * self.ratio)
			self.limit = self.__totaldoc - self.offset		
	
	def setup (self):
		pass
			
	def teardown (self):
		pass
	
	def get (self):
		raise NotImplementedError	
		
		
class GuessAndCheck:
	def __init__ (self, colopt, col_class, trainset_ratio, trialset, resource_dir = ""):
		self.colopt = colopt	
		self.col_class = col_class
		self.trainset_ratio = trainset_ratio		
		self.params = trialset
		self.resource_dir = resource_dir
		self.logger = None
	
	def set_logger (self, logger):
		self.logger = logger		
		
	def get_model (self, mode):	
		mdl = delune.model (
			[os.path.join (self.resource_dir, d) for d in self.colopt ['data_dir']], 
			mode, 
			delune.standard_analyzer (max_term = 10000, **self.colopt ['analyzer'])
		)
		return mdl
		
	def get_learner (self, mode = delune.MODIFY):			
		return self.get_model (mode).get_learner ()
	
	def get_classifier (self):			
		return self.get_model(delune.READ).get_classifier ()
	
	def add_document (self, learner, docs):
		if type (docs) is not list:
			docs = [docs]
		for doc in docs:				
			learner.add_document (doc)
				
	def index (self):
		try: os.remove (self.get_file ())
		except OSError: pass
		learner = self.get_learner (delune.CREATE)
		for docs in self.col_class (self.trainset_ratio, 1):			
			self.add_document (learner, docs)
		learner.close ()
	
	def append (self):
		learner = self.get_learner (delune.APPEND)
		for docs in self.col_class (self.trainset_ratio, 0):
			self.add_document (learner, docs)
		learner.close ()
		
	def optimize (self):
		learner = self.get_learner ()
		learner.optimize ()
		learner.close ()
			
	def listbydf (self, dfmin = 0, dfmax = 0):
		learner = self.get_learner ()			
		learner.listbydf (dfmin, dfmax)
		learner.close ()
	
	def guess (self, document, lang = "en"):
		classifier = self.get_classifier ()
		classifier.setopt (delune.ROCCHINO, topdoc = 200)
		rs = []
		for cl in (delune.META, delune.NAIVEBAYES, delune.FEATUREVOTE, delune.ROCCHINO, delune.MULTIPATH, delune.TFIDF, delune.SIMILARITY):
			rs.append (classifier.guess (document, lang = "en", cl = cl))
		pprint (rs)		
		classifier.close ()
	
	def build (self, dfmin = 0, dfmax = 0):
		learner = self.get_learner ()	
		r = learner.build (dfmin, dfmax)
		learner.close ()
		return r
	
	def train (self, selector = delune.IG, select = 2000):
		learner = self.get_learner ()	
		r = learner.train (selector = selector, select = select, orderby = delune.MAX, dfmin = 0, dfmax = 0)
		learner.close ()			
		return r
		
	def check (self, cl = delune.NAIVEBAYES):
		classifier = self.get_classifier ()
		classifier.setopt (delune.ROCCHINO, topdoc = 200)
				
		total = 0
		matched = 0		
		unclaissified = 0
		
		for docs in self.col_class (self.trainset_ratio, 0):
			if type (docs) is not list:
				docs = [docs]
			
			for doc in docs:	
				total += 1
				rs = classifier.guess (doc.text, cl = cl, lang = doc.lang)
				if not rs ["result"]:
					unclaissified += 1				
					continue
				
				if len (rs ["result"]) and rs ["result"][0][0] == doc.label:	
					matched += 1	
					if self.logger and matched % 100 == 0:
						self.logger ("%2.1f%% (%d droped / %d documents)" % (matched / (total - unclaissified) * 100, unclaissified, total), 'info')
			
		classifier.close ()
		return (matched / (total - unclaissified), unclaissified, total)		
	
	def test (self, cl = delune.NAIVEBAYES):
		result = self.check (cl)
		print ("accuracy: %1.4f, unclassified: %d, total documents: %d" % tuple (result))
		
	def get_file (self):
		data_dir = self.colopt ['data_dir']
		if type (data_dir) is list:
			data_dir = data_dir [0]
		return os.path.join (self.resource_dir, data_dir, 'prof.gac')
			
	def save (self, obj):
		with codecs.open (self.get_file (), "w")	as f:
			f.write (json.dumps (obj))
	
	def load (self):		
		fn = self.get_file ()
		if not os.path.isfile (fn):
			return {}
		with codecs.open (fn)	as f:
			return json.loads (f.read ())
	
	def commit (self, index):
		prev = self.load ()
		params = prev.get ('params')
		if not params:
			raise SystemError ('You should run trials first')
		if 'optimal' in prev:
			raise SystemError ('Already committed')
		try:
			dfmin, dfmax, selector, select, cl = params [index]
		except IndexError:
			raise SystemError ('Invalid parameter index')
				
		self.build (dfmin, dfmax)
		self.train (selector, select)
		self.optimize ()
		prev ['optimal'] = params [index]
		self.save (prev)
		
	def runset (self):
		current_dfs = (-1, -1)
		prev = self.load ()
		if prev.get ('current_dfs'):
			current_dfs = tuple (prev.get ('current_dfs'))
			
		results = []
		trial = 0
		total, pruned = 0, 0		
		for dfmin, dfmax, selector, select, cl in self.params:			
			if current_dfs != (dfmin, dfmax):
				total, pruned = self.build (dfmin, dfmax)
				current_dfs = (dfmin, dfmax)				
			features = self.train (selector, select)
			results.append ((trial, self.check (cl), (features, total, total - pruned, dfmin, dfmax, cl, selector, select)))
			trial += 1
			
		self.save ({
			'results': results,
			'current_dfs': list (current_dfs),
			'params': self.params
		})
		self.status ()
	
	def status (self):
		res = self.load ()		
		print ('------------------')
		print ('testing result')
		print ('------------------')
		for trial, result, options in res ["results"]:			
			print ("#%2d" % trial, end = " ")
			print ("accuracy: %1.4f, unclassified: %d, total documents: %d" % tuple (result))			
			print (
				"    - features: %d, terms: %d -> %d, dfmin: %d, dfmax: %d\n" 
				"    - classifier: %s, selector: %s, select: %s"
				% tuple (options)
			)
			print ()

def usage ():
	import sys
	
	print ("""
Usage
-----

	%s command [parameters]	


Commands and Required Parameters
--------------------------------
	
	status
	index
	runset
	append
	commit trial_index    ex. commit 9
	
	test [classifier=naivebayes]: test accuracy by current options
	  - classifiers: naivebayes, featurevote, tfidf, similarity, rocchino, multipath, metaclassifier
	list min_df max_df    ex. list 5 0
	guess text_to_classify    ex. guess "computer service"
	register alias


Formal Sequence
---------------

	1. Make class for poducing documents
	2. Run index
	3. Run list 0 0
	4. Make trials parameters
	5. Run runset
	6. Run append
	7. Run commit [optimal parameter index]
	8. Run register alias
	
	""" % sys.argv [0])
	
	sys.exit ()
	
	
def handle_command (gac, log = None):
	import getopt, sys
	from delune.lib import logger
	
	argopt = getopt.getopt(sys.argv[1:], "", [])
	log = log or logger.screen_logger ()	
	delune.configure (1, log)	
	gac.set_logger (log)	
	
	params, cmd = argopt
	if not cmd:
		usage ()
				
	params, cmd = tuple (cmd [1:]), cmd [0]	
	
	if cmd == "index":
		gac.index ()
	
	elif cmd == "guess":
		gac.guess (" ".join (params))
		
	elif cmd == "status":
		gac.status ()
	
	elif cmd == "runset":
		gac.runset ()
	
	elif cmd == "list":
		try:
			gac.listbydf (int (params [0]), int (params [1]))
		except IndexError:
			usage ()	
	
	elif cmd == "append":	
		gac.append ()		
	
	elif cmd == "test":	
		if params:
			cl = params [0]
		else:
			cl = delune.NAIVEBAYES
		gac.test (cl)
		
	elif cmd == "commit":	
		try:
			gac.commit (int (params [0]))
		except IndexError:
			usage ()		
	
	elif cmd == "register":
		try:
			url = params [0]
			r = requests.post (url, data = json.dumps (gac.colopt))
			print ("register: %s" % url)
			print ("------------------------------")
			if r.text:
				print ("error: ", r.text)
			else:	
				print ("success: move/copy model into app resource dir")			
		except IndexError:
			usage ()
			
	delune.shutdown ()

