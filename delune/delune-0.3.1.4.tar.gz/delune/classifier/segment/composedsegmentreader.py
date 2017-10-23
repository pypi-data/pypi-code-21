import os
import sys
import types
import delune
from delune import _delune
from delune.searcher import searcher
from delune.searcher.segment import segmentreader
from . import segment
import math
from delune import memory

class ComposedSegmentReader:
	def __init__ (self, si):
		self.si = si
		self.logger = self.si.logger
		
		self.reader = None
		self.searcher = None
		self.reader = None
		self.corpus = None
		
		self.IDFCache = {}
		self.DFCache = {}
		self.termScoreCache = {}		
		self.numpools = len (self.si.segments.pools)
	
	def getSegmentNum (self):
		return self.reader.seg
	
	def translate (self, res):
		res = [(self.si.segments.pools [x [0]], x [1]) for x in res]
		res.sort (key = lambda x: x [1], reverse = True)
		return res
	
	def get_memory (self):
		return memory.get (self.reader)
					
	def load (self):
		if self.reader:
			self.close ()
		
		self.si.read ()
		seg = self.si.getSegmentList ()[0]
		
		self.reader = segment.Segment (self.si.fs.get (seg), seg, "r", version = self.si.version)
		self.reader.open ()
		self.reader.mutex_id = memory.set (self.reader)
		
		df, doff, poff, skip, plen = self.reader.ti.get (memory.get (self.reader), "corpus", 0)
		self.corpus = [x [1:] for x in self.reader.tf.get (memory.get (self.reader), df, doff, 3)]
		col = delune.collection (os.path.join (self.si.fs.getmaster (), "%s.ts" % self.si.alias), delune.READ, self.si.analyzer, self.si.logger, version = self.si.version)		
		self.searcher = col.get_searcher ()
		self.fdnoterm = self.searcher.si.getFdnoByName ("default")
	
	def delete (self, qs):
		self.searcher.do_delete (qs)
		
	def close (self):
		if self.reader:
			memory.remove (self.reader)
			self.reader.close ()
			self.reader = None
		if self.searcher:
			self.searcher.close ()
	
	def getN (self):
		return self.si.segments.N
				
	def getDF (self, mem, term):
		try: 
			return self.DFCache [term]
		except KeyError:
			value = self.searcher.segments.last ().getTermInfo (mem, term, self.fdnoterm)
			if value:
				df = value [0]
				self.DFCache [term] = df
				return df
		return 0		
	
	def getIDF (self, df):
		if not self.IDFCache:
			for i in range (1, 128):
				self.IDFCache [i] = math.log (float (self.getN()) / i)
		try:
			return self.IDFCache [df]
		except KeyError:
			return math.log (float (self.getN()) / df)
	
	def getCoOccurrence (self, mem, x, y):
		if x > y:
			t = x; x = y; y = t			
		if x == y:
			raise ValueError("Should x != y")
		seekp = x * 8
		pos, df = self.reader.ci.listgetat (mem, seekp, 4, 2)
		conoccur = self.reader.co.getbyid (mem, y, df, pos, 2)
		return conoccur 
		
	def readTermInfo (self, mem, term):
		ti = self.reader.ti.get (mem, term, 1)
		if ti:
			df, doff, poff, skip, plen = ti
			self.reader.tf.read (mem, df, doff, skip)
			return 1
		return 0	
		
	def getFeatures (self, mem, terms, numvoca, top = 0):
		termsfv = []
		if top:
			classifier = _delune.Classifier (mem, self.corpus, numvoca, self.getN())
			for term, tf in terms:
				try: 
					score = self.termScoreCache [term]
					termsfv.append ((term, tf, score))
				except KeyError:
					if self.readTermInfo (mem, term):
						classifier.load ()
						score = classifier.scorefeature ()
						termsfv.append ((term, tf, score))
						self.termScoreCache [term] = score
			classifier.close ()
			termsfv.sort (key = lambda x: x [2], reverse = True)
			termsfv = [(x [0], x [1]) for x in termsfv [:top]]
			
		else:
			for term, tf in terms:
				if self.getDF (mem, term):
					termsfv.append ((term, tf))
		return termsfv
	