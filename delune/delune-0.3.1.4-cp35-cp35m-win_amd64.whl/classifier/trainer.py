import os
import sys
import types
from delune import _delune, memory
from delune.searcher import indexer, document
from ..util import util
from .segment import composedsegmentwriter
from delune.searcher.segment import segment as document_segment
import math
import delune
import pickle

class ExitNow (Exception): 
	pass


class PoolInfo:
	def __init__ (self, name, df):
		self.name = name
		self.df = df
		self.tf = 0

	def __lt__ (a, b):
		return a.name < b.name

	def __repr__ (self):
		return self.name


class Corpus:
	def __init__ (self):
		self.N = 0
		self.pools = []
		self.numpools = 0
		self.poolno = {}
		self.terms = {}
		self.scores = []
		self.features = {}
		
			
class Trainer (indexer.Indexer):
	def __init__ (self, si):
		indexer.Indexer.__init__ (self, si)		
		self.indexer = None
		self.corpus = Corpus ()
		
	def init (self):
		self.si.log ("initializing trainer...", "info")
		if not self.isIndexable ():
			raise ExitNow("`%s' not Indexable" % self.si.getAlias ())
		self.writer = composedsegmentwriter.ComposedSegmentWriter (self.si)
		self.corpus.N = self.writer.getIndexedNumDoc ()
	
	def rebuildIndex (self, breader):		
		self.si.log ("rebuild index for shrinking...", "info")
		bog = self.corpus.terms
		col = delune.collection (os.path.join (self.si.fs.getmaster (), "%s.ts" % self.si.alias), delune.APPEND, logger = self.si.logger, version = self.si.version)
		old_segment = col.getLastSegment ()
		new_path, new_segment = col.clone (old_segment)
		
		mem = memory.Memory (1, 1024, 10).get ()
		modifier = document_segment.DocumentSegment (new_path, new_segment, "w")		
		t = breader.getNumDoc ()
		i = 0
				
		while i < t:
			field, summary = breader.getDocument (mem, i)
			label, terms = util.deserialize (field)
			
			fterms = []
			for term, tf in terms:
				try:
					termid = bog [term]
				except KeyError:
					pass
				else:
					fterms.append ((termid, tf))					
			
			fterms.sort ()
			lterms = []
			for fid, tf in fterms:
				lterms.extend ([fid, tf])
				
			modifier.add_content ((label, lterms), summary)
			i += 1
		
		modifier.close ()
		col.removeSegment (old_segment)
		col.addSegment (new_segment, i)
		col.flush ()
		self.si.log ("rebuild done", "info")
					
	def add_document (self, labeledDocument):
		# labeleddocument		
		if self.indexer is None:
			if "optimized" in self.si.segments.parameters:
				if not self.si.rebuild:
					raise AssertionError ("Already optimized, can't append")
			
			col = delune.collection (os.path.join (self.si.fs.getmaster (), "%s.ts" % self.si.alias), self.si.rebuild and delune.CREATE or delune.WRITE, self.si.analyzer, self.si.logger, version = self.si.version)
			self.indexer = col.get_indexer (force_merge = True)
			
		terms = self.si.analyzer.term (labeledDocument.text)
		if not terms: return
		
		doc = document.Document ()
		doc.add_field ("label", labeledDocument.label, delune.STRING)
		doc.add_field ("default", labeledDocument.text, delune.TEXT, lang = labeledDocument.lang )
		for name, (val, ftype, lang, option) in list(labeledDocument.fields.items ()):
			doc.add_field (name, val, ftype, option, lang = lang)
		doc.set_content ([labeledDocument.label, terms])
		self.indexer.add_document (doc)
		
	def close (self):
		if self.indexer:
			self.closeIndexer ()
					
		if self.writer:
			self.writer.flush ()
			self.writer.close ()
		self.si.lock.unlock ("index")
		self.si.close ()
		self.si = None
		
	def scoringFeaures (self, selector, select_way, prune_df_min, prune_df_max):
		terms = self.corpus.terms	
		sl = _delune.Selector (len (self.corpus.pools), self.corpus.N, len (terms))
		
		if select_way == delune.SUM:		method = 0
		elif select_way == delune.MAX:	method = 1
		elif select_way == delune.AVG:	method = 2
		
		selector = getattr (sl, selector)		
		self.si.log ("setting corpus")
		fi = []
		for pool in self.corpus.pools:
			fi.append ((pool.df, pool.tf))
		sl.addCorpus (fi)
		
		self.si.log ("calculating feature's score...")
		scores = []
		t = len (terms)
		c = 0
		p = 0
		for term in terms:			
			c += 1
			if c % 1000 == 0:
				self.si.log ("calculating feature %d/%d (%d pruned)" % (c, t, p))
				
			tdf, fi = self.writer.featureClassInfo (term, self.corpus)
			if not tdf: continue
			if prune_df_min > 0 and tdf < prune_df_min:
				p += 1
				continue
			if prune_df_max > 0 and tdf > prune_df_max:
				p += 1
				continue			
			sl.add (fi)			
			score = selector (method)
			scores.append ((term, score))			

		self.si.log ("sorting by score")
		scores.sort (key = lambda x: x [1], reverse = True)
		self.si.log ("feature selection, done.")
		sl.close ()
		return scores
	
	def selectFeatures (self, name, selector, select, select_way, prune_df_min = 0, prune_df_max = 0, noprint = 0):
		self.si.log ("selecting [%s] using [%s:%s] for [%s]" % (select, selector, select_way, name))
		
		scores = self.scoringFeaures (selector, select_way, prune_df_min, prune_df_max)
		if not select:
			select = 1.0
		if select <= 1.0:
			select = int (len (scores) * select)
		else:
			select = int (select)
		if len (scores) < select:
			select = len (scores)
		
		if not noprint:
			c = 0
			for term, score in scores:
				c += 1
				tdf = self.writer.featureClassInfo (term, self.corpus)[0]				
				if c <= 200 or c >= (len (scores) - 200):
					self.si.log ("FEAT %5d. %s %2.3f (DF %d)" % (c, term, score, tdf))
				elif c == 201:
					self.si.log ("=========== Top 200, Bottom 200 ===========")
					
		self.si.log ("selecting within %d th features" % (select,))
		terms = scores [:select]
		terms = [x [0] for x in terms]
		
		fmap = dict ([(term, self.corpus.terms [term]) for term in terms])
		self.si.segments.features [name] = fmap	
		return len (terms)	
	
	def getFeatureSet (self, name):
		return self.si.segments.features	[name]	
	
	def listbydf (self, dfmin = 0, dfmax = 0):
		self.build (dfmin, dfmax, False)
	
	def closeIndexer (self):
		self.indexer.commit (1)
		self.indexer.merge ()
		self.indexer.close ()
		self.indexer = None			
		
		# reset parameters
		if self.si.hasSegmentsFile ():
			self.si.segments.parameters ["build"] = (-1, -1)
			self.si.segments.parameters ["train"] = {}
			if self.si.rebuild: 
				try: del self.si.segments.parameters ["optimized"]
				except KeyError: pass	
			self.si.flush (0)
					
	def build (self, dfmin = 0, dfmax = 0, commit = True, rebuild_index = False):
		if self.indexer:
			self.closeIndexer ()

		if not self._initialized:
			self.init ()
		
		if (dfmin, dfmax) == self.si.segments.parameters ["build"]:
			self.si.log ("same with previous parameters, need not rebuild")
			commit = False
		else:		
			self.si.log ("building corpus data")
			
		breader = self.writer.getSegmentBulkReader ()
		# get self.corpus pools and DF
		tindex = 0
		pruned = 0
		total = -1
		stat = {}
		while 1:
			try:
				ti = breader.advanceTermInfo ()
				if ti.fdno == self.writer.fdnoclass:
					self.corpus.pools.append (PoolInfo (ti.term, ti.df))
				elif ti.fdno == self.writer.fdnoterm:
					total += 1
					if dfmin and ti.df < dfmin:
						pruned += 1
					elif dfmax and ti.df > dfmax:
						pruned += 1	
					else:	
						self.corpus.terms [ti.term] = tindex
						stat [ti.term] = ti.df
						tindex += 1					
			except IndexError:
				break		
		
		temp = list(stat.items ())
		temp.sort (key = lambda x: x[1], reverse = True)		
		cc = 0
		for term, df in temp:
			cc += 1
			if cc <= 200 or cc >= (len (temp) - 200):
				self.si.log ("TERM %5d. DF %d %s" % (cc, df, term))
			elif cc == 201:
				self.si.log ("=========== Top 200, Bottom 200 ===========")	
		del stat
		del temp
		self.si.log ("%d (%d%%) terms pruned term dimension was shrinked: %d->%d" % (pruned, 1.*pruned/total*100, total, total-pruned))
		
		if rebuild_index:
			self.rebuildIndex (breader)						
			self.si.segments.parameters ["optimized"] = True
			self.si.flush (0)
		breader.close ()
		
		if not commit:
			self.writer.close ()		
			self.writer = None			
			return total, pruned
		
		self.writer.dirty = 1	
		self.corpus.pools.sort ()		
		# caching related with pools
		self.corpus.numpools = len (self.corpus.pools)
		pindex = 0
		poolno = {}
		for pool in self.corpus.pools:
			poolno [pool.name] = pindex
			pindex += 1
		self.corpus.poolno = poolno
		# caching related with pools--
		
		c = 0
		t = len (self.corpus.terms)
		for term in self.corpus.terms:
			if c % 1000 == 0:				
				self.si.log ("build corpus %d/%d" % (c, t))
			tdf, fi = self.writer.featureClassInfo (term, self.corpus)
			i = 0
			for df, tf in fi:
				self.corpus.pools [i].tf += tf
				i += 1
			c +=1
		
		self.writer.commit (self.corpus)		
		# sould be exactly here
		self.si.segments.parameters ["build"] = (dfmin, dfmax)		
		self.si.segments.parameters ["train"] = {}
		self.si.segments.features = {}
		self.writer.flush ()
		self.writer.close ()
		self.writer = None
		
		return total, pruned
		
	def untrain (cl_for = None):
		if cl_for in self.si.segments.features:
			del self.si.segments.features [cl_for]
			del self.si.segments.parameters ["train"][cl_for]
			self.si.flush ()	
		
	def train (self, cl_for = "default", **options):
		self.writer = composedsegmentwriter.ComposedSegmentFeaturesetWriter (self.si)
		if not self.corpus.numpools:
			self.corpus = self.writer.get_corpus ()
			
		selector = options.get ("selector", None)
		if not selector and cl_for == "default":
			raise ValueError("No default selector, be specify")
				
		if selector:
			orderby = options.get ("orderby", delune.SUM)
			select = float (options.get ("select", 1.0))
			prune_df_min, prune_df_max = options.get ("df_range", (0, 0))
			prune_df_min = options.get ("dfmin", 0)			
			prune_df_max = options.get ("dfmax", 0)
			noprint = options.get ("noprint", 0)
			
			if prune_df_min <= 1: prune_df_min = int (prune_df_min * len (self.corpus.terms))
			if prune_df_max <= 1: prune_df_max = int (prune_df_max * len (self.corpus.terms))
			
			numterms = self.selectFeatures (cl_for, selector, select, orderby, prune_df_min, prune_df_max, noprint)
		self.si.segments.parameters ["train"][cl_for] = options
		return numterms
				
	def optimize (self):
		if "optimized" in self.si.segments.parameters:
			raise AssertionError ("Already optimized")		
		if (-1, -1) == self.si.segments.parameters ["build"]:
			raise AssertionError ("Call build (dfmin, dfmax) first")
					
		dfmin, dfmax = self.si.segments.parameters ["build"]
		self.si.log ("optimizing corpus with DFMIN %d and DFMAX %d" % (dfmin, dfmax))
		self.build (dfmin, dfmax, True, True)		
		
		for cl_for, param in list (self.si.segments.parameters ["train"].items ()):
			self.si.log ("optimizing classifiers for %s" % (cl_for,))
			param ["noprint"] = 1
			self.train (cl_for, **param)
	
	
def usage ():
	print("""
Usage:
	%s [long option list...]
	--config=configuration file path
	--force
	--index
		sub option: --[bulk | append]	
	""" % sys.argv [0])
	sys.exit ()
	
	
def main (path, index = 0, rebuild = 0, force = 0):
	util.check_config (path)
	f = Trainer (path)
	if f.indexable (force):
		f.main (index, rebuild, force)


if __name__ == "__main__":
	import sys, getopt
	import profile

	try: argopt = getopt.getopt(sys.argv[1:], "", \
		["config=", "index", "bulk", "append", "force"])
	except:
		usage ()

	_config = None
	_rebuild = None
	_force = 0
	_index = 0

	for k, v in argopt[0]:
		if k == "--config":
			_config = v
		elif k == "--index":
			_index = 1
		elif k == "--bulk":
			_rebuild = 1
		elif k == "--append":
			_rebuild = 0
		elif k == "--force":
			_force = 1

	if not _config: usage ()
	if _index and _rebuild is None: usage ()

	main (_config, _index, _rebuild, _force)	
