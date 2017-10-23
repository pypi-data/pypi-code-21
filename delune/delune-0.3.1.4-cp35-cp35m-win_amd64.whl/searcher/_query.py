from delune import _delune
from delune import util
from datetime import datetime
from . import queryparser
import types
import copy
import re
import time
import fieldreader
import typeinfo
import memory

class Query:
	DEBUG = 0
	CACHEPAGE = 3
	def __init__ (self, segments, qs, offset, fetch, sort, analyze):
		self.segments = segments
		self.qs = qs
		self.offset = offset
		self.fetch = fetch
		self.sort = sort		
		self.analyze = analyze
		
		self.cachedfetch = self.offset + self.fetch
		if self.offset == 0 and len (self.segments) < self.CACHEPAGE:
			if len (self.segments):
				self.cachedfetch = self.cachedfetch + int ((float (self.fetch) / len (self.segments)))
			else:
				self.cachedfetch = 0
				
		self.sorted = 0		
		# postential sort options
		self.sortorder = 0
				
		if self.sort:
			if self.sort [0] == "-":
				self.sortorder = 1
				self.sort = self.sort [1:]
			else:
				self.sortorder = -1
		
		self.hits = _delune.Compute (memory.get ())
		
		self.sortindex = None
		self.totalcount = 0		
		self.duration = 0
		self.esegments = []
		self.bucket = []
		self.highlights = {}
	
	def getBufferSize (self, segment, size):		
		hits = self.hits.count ()
		if hits == 0: return 0
		bsize = int ((self.segments.si.getSegmentNumDoc (segment.seg) / float (hits)) * size)
		if bsize > memory.get_buffer_size (): bufsize = 1024
		else: bufsize = 0		
		return bufsize

	def close (self):
		self.hits.close ()		
	
	def setResult (self, cached):
		self.totalcount, highlights, self.bucket = cached
		for each in highlights:
			self.highlights [each] = None
		
	def newSegmentScan (self, segment):
		self.randomscan = 0
		self.numoperate = 0
		self.numnorm = 0
		self.mem = memory.get (segment)
		self.fi = fieldreader.FieldReader (self.mem, segment, self.analyze and self.segments.inf.analyzer or None, self.sort == "tfidf")
		self.hits.setN (self.sort == "tfidf" and self.segments.si.getSegmentNumDoc (segment.seg) or 0)		
		
	def addHighlight (self, term):
		self.highlights [term] = None
		if len (term) < 4: return
		
		# plural
		if term [-1] != 's':
			if term [-1] in "xz":
				self.highlights [term + 'es'] = None
			elif term [-1] == 'y':
				if term [-2] in "aeiou":
					self.highlights [term + "s"] = None
				else:	
					self.highlights [term [:-1] + "ies"] = None			
			elif term [-1] == 'f':
				self.highlights [term [:-1] + "ves"] = None
				self.highlights [term + "s"] = None
			elif term [-2:] == 'fe':
				self.highlights [term [:-2] + "ves"] = None	
				self.highlights [term + "s"] = None	
			else:
				self.highlights [term + 's'] = None
				
		elif len (term) >= 5 and term [-3:] == 'ies':
			self.highlights [term [:-3] + "y"] = None
		
		elif len (term) >= 5 and term [-3:] == 'ves':
			self.highlights [term [:-3] + "f"] = None
			self.highlights [term [:-3] + "fe"] = None
				
		elif len (term) >= 5 and term [-2:] == 'es' and (term [-3] in "sxz" or term [-4:-2] in ("sh", "ch")):
			self.highlights [term [:-2]] = None
			self.highlights [term [:-1]] = None
		
		elif term [-1] == 's':
			self.highlights [term [:-1]] = None
		
	def setTi (self, term):
		try: 
			name, value = term.split (":")
		except ValueError:
			name, value = "default", term
			
		type, num = self.segments.si.getFieldInfo (name)		
		return self.fi (type, term, name, value, num)		
		
	def optimize (self, segment, expression):
		#swaping operands
		# it reduces push-pop operation
		if type (expression [1]) is bytes:
			expression [1] = self.setTi (expression [1])			
								
		if type (expression [2]) is bytes:
			expression [2] = self.setTi (expression [2])			
		
		#swap between operands
		if expression [0] in "*+":
			if expression [2] is None and self.hits.count ():
				expression  = [expression [0], None, expression [1]]
				if self.DEBUG: print("SWAP:", expression)				
			
			# swap phrase		
			if expression [1] and expression [2]:
				if not expression [1].methology == "Phrase" and expression [2].methology == "Phrase":
					expression  = [expression [0], expression [2], expression [1]]
					if self.DEBUG: print("SWAP:", expression)				
			
				#swap with df	
				if expression [1].ti and expression [2].ti:
					if expression [1].ti [0] > expression [2].ti [0]:
						expression = [expression [0], expression [2], expression [1]]
						if self.DEBUG: print("SWAP:", expression)				
			
				#swap range						
				if typeinfo.typemap.getsize (expression [1].type) and not typeinfo.typemap.getsize (expression [2].type):
					expression = [expression [0], expression [2], expression [1]]
					if self.DEBUG: print("SWAP:", expression)
					
		return expression
	
	rx_proxdelta = re.compile ("\s*(?P<delta>\^[0-9]+)\s*")
	def computePhrase (self, segment, term, operator):
		if not term.type: return 0
		if not term.value: return 0
		dc = 0
		self.randomscan = 0
		
		if len (term.value) == 1: # not phrase
			term.value [0].readprox = 0
			return self.computeTerm (segment, term.value [0], operator)
						
		pushed = 0
		if self.hits.count ():
			self.hits.push ()
			pushed = 1
			if self.DEBUG: print("P-PUSH:", self.hits.saved ())
			
		for termTi in term.value:
			if not termTi.df: break			
			self.computeTerm (segment, termTi, operator)
			dc = self.hits.intersect (termTi.near, termTi.loose)
			if not dc: break
		
		if pushed:
			self.hits.pop ()
			if self.DEBUG: print("P-POP:", self.hits.saved ())
			
		return dc
		
	def computeWildCard (self, segment, term, operator):
		if not term.ti: return 0
		
		self.randomscan = 0
		pushed = 0
		if self.hits.count ():
			self.hits.push ()
			pushed = 1
			if self.DEBUG: print("P-PUSH:", self.hits.saved ())
		
		for termTi in term.value:
			if not self.computeTerm (segment, termTi, operator): continue
			dc = self.hits.union ()
		
		if pushed:
			self.hits.pop ()
			if self.DEBUG: print("P-POP:", self.hits.saved ())			
		
		return dc
				
	def computeTerm (self, segment, term, operator):
		if not term.type: return 0
		if term.stopword: return 0
		if not term.df: return 0
		
		if segment.rd: self.randomscan = 0
		
		if self.randomscan and len (self.bucket) >= self.cachedfetch:
			if self.DEBUG: print("SKIP: randomscan")
			self.hits.setcount (term.df)
			return term.df
			
		df, doff, poff, skip, plen = term.ti
		if (term.sp): segment.sm.read (self.mem, self.getBufferSize (segment, term.sp [1]), *term.sp) # needn't for f type
		
		if self.randomscan:
			if self.DEBUG: print("RANDOM SCAN")
			segment.readPosting (self.mem, df, doff, poff, skip, plen, 0, self.cachedfetch, term.readprox)
			self.hits.setcount (term.df)
			
		else:
			if self.DEBUG: print("FULL SCAN")
			segment.readPosting (self.mem, df, doff, poff, skip, plen, -1, -1, term.readprox)			
			
		if operator != "-" and typeinfo.typemap.hasnorm (term.type):
			self.numnorm += 1 # need sort?
			if term.query:		
				for hk in term.query.split ():
					self.addHighlight (hk)
		
		t =  self.hits.set (self.segments.si.getWeight (term.name))
		return t
		
	def computeCoord (self, segment, term, operator):
		if not term.value: return 0
		latitude, longitude, distance = term.value
		set = 0
		if self.sort == term.name: set = 1
		
		segment.sm.read (self.mem, self.getBufferSize (segment, term.sp [1]), *term.sp)
		return self.hits.distance (latitude, longitude, distance, set)
	
	def computeDigit (self, segment, term, operator):
		if not term.value: return 0
		
		a, b = term.value
		if b in ("all", "any", "none"):
			smfunc = self.hits.bit			
		else:
			smfunc = self.hits.between
		
		segment.sm.read (self.mem, self.getBufferSize (segment, term.sp [1]), *term.sp)
		
		if not (a == -1 and (b == -1 or b in ("all", "any", "none"))):
			self.randomscan = 0
				
		if self.randomscan:
			wholes = segment.getNumDoc ()  - segment.getDeletedCount ()
			self.hits.setcount (wholes)			
			
			if len (self.bucket) >= self.cachedfetch:
				return wholes
				
			dc = smfunc (a, b, operator, self.cachedfetch + segment.getDeletedCount ())
			return wholes
			
		else:
			return smfunc (a, b, operator, -1)
				
	def compute (self, segment, expression):
		if self.DEBUG: print("EXPRESSION", expression)
		
		record_count = 0
		operate = 1
		
		#---------------------------------------------------------------------------------
		# Initial Optimazation
		#---------------------------------------------------------------------------------	
		if type (expression) is bytes: # only 1 term
			expression = ["*", expression, None]
			operate = 0
			
		elif expression [0] != "-" and type (expression [1]) == bytes and type (expression [2]) == list:
			expression = [expression [0], expression [2], expression [1]]		
		
		#---------------------------------------------------------------------------------
		# Recursive Compute
		#---------------------------------------------------------------------------------	
		if type (expression [1])  is list:
			expression [1] = self.compute (segment, expression [1])
	
			if self.numoperate and expression [1] is None and self.hits.count () == 0 and expression [0] in "*-":
				if self.DEBUG: print("SKIP:", expression [2])
				self.hits.abort () # need not proceed
				expression [2] = None
				return None
		
		if type (expression [2])  is list:
			expression [2] = self.compute (segment, expression [2])

			if self.numoperate and expression [2] is None and self.hits.count () == 0 and expression [0] in "*":
				if self.DEBUG: print("SKIP:", expression [1])				
				self.hits.abort () # need not proceed
				expression [1] = None
				return None
	
		#---------------------------------------------------------------------------------
		# Optimize
		#---------------------------------------------------------------------------------		
		expression = self.optimize (segment, expression)
		
		#---------------------------------------------------------------------------------
		# Stack Mangement
		#---------------------------------------------------------------------------------	
		# done one session, pop
		if (expression [1] is None and expression [2] is None):
			self.hits.pop ()
			if self.DEBUG: print("POP:", self.hits.saved ())
		
		# new operand, if count() save prev results
		elif expression [1] and self.hits.count ():
			self.hits.push ()			
			if self.DEBUG: print("PUSH:", self.hits.saved ())
			
		#---------------------------------------------------------------------------------
		# Left Operand
		#---------------------------------------------------------------------------------		
		# operation count			
		if  expression [1] and not expression [1].stopword:			
			self.numoperate += 1
			if type (expression [1]) is not list:
				expression = self.optimize (segment, expression)								
			# left operand is always "*"
			record_count = getattr (self, "compute" + expression [1].methology) (segment, expression [1], "*")
			if self.DEBUG: print("QUERY:", expression [1], record_count)
			if not record_count	and expression [0] in "-*":
				self.hits.abort () # need not proceed
				return None
		
		#---------------------------------------------------------------------------------
		# Right Operand
		#---------------------------------------------------------------------------------		
		if  expression [2] and not expression [2].stopword:
			self.numoperate += 1
			expression = self.optimize (segment, expression)
			record_count = getattr (self, "compute" + expression [2].methology) (segment, expression [2], expression [0])			
			if self.DEBUG: print("QUERY:", expression [2], record_count)			
			if not record_count:
				if expression [0] in "*":
					self.hits.abort () # + or - is keep hits
					return None		
		
		#---------------------------------------------------------------------------------
		# Operate
		#---------------------------------------------------------------------------------		
		if self.DEBUG: 
			print("START OPERATE:", expression, record_count)
		
		if operate:
			if expression [0] == "*":
				record_count = self.hits.intersect ()
			elif expression [0] == "+":	
				record_count = self.hits.union ()				
			elif expression [0] == "-":	
				record_count = self.hits.trim ()
			
			if self.DEBUG: print("OPERATE:", expression, record_count)
		
		if self.DEBUG: print("CURSAVED:", self.hits.saved ())		
		return None
			
	def merge (self):
		if self.sortindex:
			if self.sorted == 1:
				self.bucket.sort (lambda x, y: cmp (x [self.sortindex], y [self.sortindex]))
			elif self.sorted == -1:
				self.bucket.sort (lambda x, y: cmp (y [self.sortindex], x [self.sortindex]))
		
		highlights = list(self.highlights.keys ())
		highlights.sort (lambda x, y: cmp (len (y), len (x)))
		#rx_highlights  = re.compile ("(^| )(?P<match>" + "|".join (highlights) + ")($| )", re.I)
			
	def query (self):
		s = time.time ()
		
		tokens = queryparser.Tokenizer (self.qs).tokenize ()			
		try:
			expression = queryparser.ArithmeticParser(tokens).parse_expression()
		except IndexError:
			self.close ()
			return [501, 0, 0, ""]	
		
		for segment in self.segments:	
			try:
				self.newSegmentScan (segment)			
				# 1 term and no sort and has freq data
				if  not self.sort and type (expression) is bytes:
					self.randomscan = 1
					
				clone = copy.deepcopy (expression)			
				self.query_segment (segment, clone)
			
			except IOError:
				self.esegments.append (segment.seg)
				self.segments.si.trace ()				
			
		if self.DEBUG: print("Total Result:", self.totalcount)		
		
		self.duration = int ((time.time () - s) * 1000) #ms	
		self.merge ()
		
	def query_segment (self, segment, expression):
		#-------------------------------------------------------------------------------
		# operate
		#-------------------------------------------------------------------------------
		self.compute (segment, expression)
		
		#-------------------------------------------------------------------------------
		# skip extra fetching when no sort
		#-------------------------------------------------------------------------------
		if not self.sort and len (self.bucket) > self.cachedfetch:
			count = self.hits.count ()
			self.totalcount += count
			return
			
		#-------------------------------------------------------------------------------
		# sort setting
		#-------------------------------------------------------------------------------		
		bysortkey = 0
		byextra = 0		
		if self.sort == "tfidf" and self.numnorm:
			self.sorted = -1
			self.sortindex = -1
		
		elif self.sort:
			type, num = self.segments.si.getFieldInfo (self.sort)
			if typeinfo.typemap.isint (type):
				sp = segment.getSortMapPointer (num)					
				if sp:
					pointer, vsize = sp
					segment.sm.read (self.mem, self.getBufferSize (segment, vsize), pointer, vsize)
					bysortkey = 1
					self.sorted = self.sortorder
					self.sortindex = -1					
			
			elif typeinfo.typemap.isextra (type):
				byextra = 1
				self.sorted = self.sortorder
				self.sortindex = -2
				
		else:
			self.sorted = 0
			self.sortindex = None
			
		want = self.cachedfetch
		self.hits.sort (want, self.sorted, bysortkey, byextra)
		
		#-------------------------------------------------------------------------------
		# select from hit docs
		#-------------------------------------------------------------------------------
		bucket = self.hits.hitdoc (segment.seg, want, segment.getBits ())		
		self.bucket =  bucket + self.bucket
		
		#-------------------------------------------------------------------------------
		# counting hitdoc
		#-------------------------------------------------------------------------------
		count = self.hits.count ()
		self.totalcount += count
				
		if self.DEBUG: print("Segment Result:", count)
		
	