import re
import urllib.request, urllib.parse, urllib.error

class QuerySet:
	rx_col = re.compile ("\[info:(.+?)\]")
	def __init__ (self, log, loop = 1, max = 0):
		self.loop = loop
		self.f = open (log)
		self.max = max
		self.c = 0
	
	def close (self):
		self.f.close ()
	
	def get_uri (self):
		args = self.get ()
		return "/rpc2/bladese?col=%s&qs=%s&offset=%s&fetch=%s&sort=%s&summary=%s&analyze=%s&delete=%s&field%s" % args
		
	def get (self):
		while 1:
			line = self.f.readline ()
			if not line:
				if self.loop:
					self.f.seek (0)
					self.f.readline ()
				else:
					return None	
			
			s = line.find ("QUERY ")
			if s == -1: continue
			
			match = self.rx_col.search (line)
			if match:
				col = match.group (1)
			else: 
				continue
			
			line = line [s + 6:].strip ()
			k = line.split ("/")		
			qs = urllib.parse.quote ("/".join (k [:-7]))
			args = (col, qs) + tuple (k [-7:])
			if len (args) != 9: continue
			
			self.c += 1
			if self.max and self.c > self.max: return None	
				
			return args


class QueryResultSet:
	rx_col = re.compile ("\[info:(.+?)\]")
	def __init__ (self, log):
		self.f = open (log)
		self.rset = {}
	
	def close (self):
		self.f.close ()
			
	def build (self):
		while 1:
			line = self.f.readline ()
			if not line:
				return None	
			
			s = line.find ("RESULT ")
			if s == -1: continue
			
			match = self.rx_col.search (line)
			if match:
				col = match.group (1)
			else: 
				continue
			
			line = line [s + 6:].strip ()			
			q, r = line.split ("=>", 1)
			r = r.split ("/", 4)			
			self.rset [col + "/" + q] = int (r [2])
			
