import os
import sys
import types
from delune import _delune
from delune.searcher.segment import segmentreader
from delune.searcher import collection
from delune.util import util
from . import segment
import pickle as pk


class FeatureClassInfos:
	def __init__ (self, path):
		self.path = path
		self.infos = {}
	
	def __getitem__ (self, k):
		return self.infos [k]
	
	def __setitem__ (self, k, v):
		self.infos [k] = v
	
	def truncate (self):		
		self.infos = {}	
		self.path = None	
	
	def load (self):		
		if not self.path: 
			return
		if not os.path.isfile (self.path):
			return
		f = open (self.path, "rb")
		self.infos = pk.load (f)
		f.close ()
		
	def save (self, path = None):
		if path: self.path = path
		f = open (self.path, "wb")
		pk.dump (self.infos, f, 1)
		f.close ()
		
	def close (self):
		del self.infos
		self.infos = {}


class ComposedSegmentWriter:
	def __init__ (self, si):
		self.si = si		
		self.logger = self.si.logger
		
		self.featureClassInfoCache = FeatureClassInfos (self.getSegmentBasePath () + "cfi")
		self.DFCache = {}
		self.mpool = _delune.MemoryPool (1, 32768, 50)
		self.mem = self.mpool.get (0)
		
		self.ts_si = collection.Collection (os.path.join (self.si.fs.getmaster (), "%s.ts" % self.si.alias), 'w', self.si.logger, version = self.si.version)
		self.ts_reader = segmentreader.SegmentReader (self.ts_si, self.ts_si.getSegmentList ()[0])
		
		self.fdnoclass = self.ts_si.getFdnoByName ("label")
		self.fdnoterm = self.ts_si.getFdnoByName ("default")
		
		self.basesegmentpath = None	
		self.dirty = 0
	
	def getSegmentBasePath (self):
		try:
			seg = self.si.fs.segments ()[-1]
		except IndexError:
			return os.path.join (self.si.fs.getmaster (), "0.")
		return os.path.join (self.si.fs.getmaster (), str (seg) + ".")
				
	def close (self):
		if self.mpool:
			self.mpool.close ()
			self.mpool = None
		if self.ts_reader:
			self.ts_reader.close ()
			
	def getIndexedNumDoc (self):
		return self.ts_reader.si.getN ()
			
	def getSegmentBulkReader (self):
		return segmentreader.SegmentBulkReader (self.ts_si, self.ts_reader.si.getSegmentList ()[0])
		
	def getDocument (self, docid):
		fd, summary = self.ts_reader.getDocument (self.mem, docid)
		return pk.loads (fd) [:2]
	
	def getDF (self, term, fdno):
		return self.getTermInfo (term, fdno) [0]
		
	def getTermInfo (self, term, fdno):
		try:
			return self.DFCache ["%s:%s" % (fdno, term)]
		except KeyError:
			value = self.ts_reader.getTermInfo (self.mem, term, fdno)
			self.DFCache ["%s:%s" % (fdno, term)] = value
			return value
		
	def getTermClassInfo (self, term, pools):
		hits = _delune.Compute (self.mem)
		hits.newscan ()
		hits.setfreq (1)
		
		df, doff, poff, skip, plen = self.ts_reader.getTermInfo (self.mem, term, self.fdnoterm)		
		self.ts_reader.readPosting (self.mem, df, doff, poff, skip, plen, -1, -1, 0)
		hits.set ()
		
		cfi = {}
		tdf = 0
		numpool = 0
		for pool in pools:
			df, doff, poff, skip, plen = self.ts_reader.getTermInfo (self.mem, pool.name, self.fdnoclass)			
			self.ts_reader.readPosting (self.mem, df, doff, poff, skip, plen, -1, -1, 0)
			df = hits.intersect ()
			tf = 0
			if df:
				tdf += df
				r = hits.hitdoc (0)
				for seg, docid, freq, score in r:
					tf += freq	
				cfi [numpool] = (df, tf)
			hits.reuse ()
			numpool += 1						
		hits.close ()
		return tdf, cfi
	
	def getSegmentPath (self):
		return self.basesegmentpath		
	
	def featureClassInfo  (self, term, corpus): 
		try:
			cfi = self.featureClassInfoCache [term]
			fi = [(0,0)] * corpus.numpools
			tdf = 0
			for index, info in list(cfi.items ()):
				tdf += info [0]
				fi [index] = info
			return tdf, fi			
		except KeyError:
			pass
		tdf, cfi = self.getTermClassInfo (term, corpus.pools)
		self.featureClassInfoCache [term] = cfi
		return self.featureClassInfo (term, corpus)
	
	def flush (self):			
		if self.dirty:
			self.si.log ("flushing train data...")
			self.si.flush (new = 1)			
		else:
			self.si.flush (new = 0)
	
	def writeTermTermInfo (self, trainsegment, terms):
		numterm = len (terms)
		self.si.log ("saving %d terms co-occurences..." % (numterm,))
		hits = _delune.Compute (self.mem)
		cnt = 0
		poslist = []
		for term in terms:
			pos = trainsegment.co.tell ()
			if cnt % 100 == 0:
				self.si.log ("writing %d/%d terms co-occurences..." % (cnt, numterm))
			cnt += 1
			hits.newscan ()
			colist = []
			df, doff, poff, skip, plen = self.ts_reader.getTermInfo (self.mem, term, self.fdnoterm)		
			self.ts_reader.readPosting (self.mem, df, doff, poff, skip, plen, -1, -1, 0)
			hits.set ()
			rindex = cnt
			for term2 in terms [cnt:]:
				df, doff, poff, skip, plen = self.ts_reader.getTermInfo (self.mem, term2, self.fdnoterm)			
				self.ts_reader.readPosting (self.mem, df, doff, poff, skip, plen, -1, -1, 0)
				df = hits.intersect ()
				if df:
					colist.append ((rindex, df))
				rindex += 1
				hits.reuse ()
			df, endpos = trainsegment.co.write (colist, 1)
			poslist.extend ([pos, df])
		hits.close ()		
		trainsegment.ci.writelist (poslist, 4)
			
	def commit (self, corpus):
		if not self.dirty:
			return
		
		self.si.createSegments ()	# always rebuild
		self.si.segments.pools = [ pool.name for pool in corpus.pools ]
		self.si.segments.numpool = corpus.numpools
		self.si.segments.features = {}
		self.si.segments.numvoca = len (corpus.terms)
		self.si.segments.N = corpus.N

		self.si.log ("creating new segment...")
		newseg = self.si.getNewSegment  ()
		
		trainsegment = segment.Segment (self.si.fs.new (newseg), newseg, "w", version = self.si.version)
		trainsegment.open ()
		
		frqposition = trainsegment.tf.tell ()
		df, skip = trainsegment.tf.write ([(pool.df, pool.tf) for pool in corpus.pools], 0, 1)
		trainsegment.ti.add ("corpus", 0, df, frqposition, 0, skip - frqposition, 0)

		self.si.log ("writing terms...")
		c = 0
		t = len (corpus.terms)
		terms = list(corpus.terms.keys ())
		terms.sort ()
		for term in terms:
			if c % 1000 == 0:
				self.si.log ("writing terms %d / %d" % (c, t))
			frqposition = trainsegment.tf.tell ()
			tdf, fi = self.featureClassInfo (term, corpus)
			if not tdf: continue
			df, skip = trainsegment.tf.write (fi)
			if df:
				trainsegment.ti.add (term, 1, df, frqposition, 0, skip - frqposition, 0)
			c += 1
		
		self.basesegmentpath = trainsegment.get_base_path ()
		self.si.log ("writing feature-class information...")
		self.featureClassInfoCache.save (self.basesegmentpath + "cfi")
		self.writeTermTermInfo (trainsegment, terms)
		trainsegment.close ()
		
		self.si.addSegment (newseg, corpus.N)
		self.si.write ("segments.new")
		
		self.si.log ("saving temporary corpus")
		f = open (self.basesegmentpath + "cps", "wb")
		pk.dump (corpus, f, 1)
		f.close ()		
		self.si.log ("writing, done.")


class ComposedSegmentFeaturesetWriter (ComposedSegmentWriter):
	def __init__ (self, si):
		self.si = si		
		self.logger = self.si.logger
		
		self.featureClassInfoCache = FeatureClassInfos (self.getSegmentBasePath () + "cfi")
		self.featureClassInfoCache.load ()
		self.dirty = 1
	
	def get_corpus (self):
		path = os.path.join (self.getSegmentBasePath () + "cps")
		with open (path, "rb") as f:
			corpus = pk.load (f)
		return corpus	
		
	def close (self):
		pass

	