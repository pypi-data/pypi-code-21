import threading
import os
from aquests.lib import siesta
import delune
import time

class Commander:
	def __init__ (self, colopt, server, segments = 1, logger = None):
		self.colopt = colopt
		self.server = server
		self.segments = segments
		self.logger = logger
		self.api = siesta.API (self.server)
		
		self.apis = [None] * self.segments
		self.name = self.colopt ["name"]
		self.lk = threading.Lock ()
		self.T = 0		
	
	def get_api (self, segment):
		return self.apis [segment [0]]
	
	def maybe_commit (self, api, message):
		with self.lk:
			self.T += 1
			if self.T % 100 == 0:			
				print (message, self.T)
				try:
					api (self.name).commit.get ()
				except:
					print ('commit error')
					
	def delete (self, segment, pk = None, query = None):
		api = self.get_api (segment)
		if query:
			r = api (self.name).delete (query)
		elif pk:
			r = api (self.name).documents (pk).delete ()
		else:
			raise ValueError ("Required pk or query")
			
		if r.data: raise SystemError (r.data)
		self.maybe_commit (api, pk and 'deleted')
	
	def	post (self, segment, doc, pk = None):
		api = self.get_api (segment)
		while 1:
			r = None
			try:
				if pk:
					r = api (self.name).documents (pk).patch (doc.as_dict ())
				else:
					r = api (self.name).documents.post (doc.as_dict ())						
			except:
				pass
			
			if not r or r.data:
				print ('error: %s, try after 1 sec...' % r)
				time.sleep (1)
			else:
				break
		
		self.maybe_commit (api, pk and 'updated' or 'inserted')
	
	def undo (self):
		r = self.api.get ()
		if self.name in r.data ["collections"]:	
			return
		
		r = self.api (self.name).get (side_effect = 'undo')
		if r.data: raise SystemError (r.data)
		while 1:
			r = self.api.get ()
			if self.name not in r.data ["collections"]:	
				time.sleep (1)
			else:
				break

	def truncate (self):
		r = self.api.get ()
		if self.name not in r.data ["collections"]:	
			return
		r = self.api (self.name).documents.delete (truncate_confirm=self.name)
		if r.data: raise SystemError (r.data)
	
	def commit (self):
		for api in self.apis:
			try:
				self.api (self.name).commit.get ()
			except:
				pass			
	
	def register (self):
		r = self.api.get ()
		if self.name not in r.data ["collections"]:	
			r = self.api (self.name).post (self.colopt)
			if r.data: raise SystemError (r)
		else:
			r = self.api (self.name).patch (self.colopt)
			if r.data: raise SystemError (r.data)
		
		while 1:
			r = self.api.get ()
			if self.name not in r.data ["collections"]:	
				time.sleep (1)
			else:
				break
				
	def unregister (self):
		r = self.api.get ()
		if self.name not in r.data ["collections"]:	
			return
			
		r = self.api (self.name).delete (side_effect='data')
		if r.data: raise SystemError (r)
		while 1:
			r = self.api.get ()
			if self.name in r.data ["collections"]:	
				time.sleep (1)
			else:
				break

	def start (self, func, update = False):	
		ts = []		
		for i in range (1, self.segments):
			self.apis [i] = siesta.API (self.server)
			t = threading.Thread (target = func, args = (self, (i, self.segments), update))
			ts.append (t)
			t.start ()
		
		self.apis [0] = siesta.API (self.server)
		func (self, (0, self.segments), update)
		for t in ts:	
			t.join ()
		
		for api in self.apis:
			try:
				api (self.name).commit.get ()
			except: 
				pass
		
			
def handle_commandline (colopt, server, segments = 1, index = None, delete = None):
	import sys
	
	commander = Commander (colopt, server, segments)	
	
	cmd = sys.argv [1]	
	if cmd == "unreg":
		commander.unregister ()	
	elif cmd == "reg":
		commander.register ()	
	elif cmd == "undo":	
		commander.undo ()	
	elif cmd == "truncate":	
		commander.truncate ()		
	elif cmd == "commit":	
		commander.commit ()	
	elif cmd == "index":	
		commander.start (index, False)	
	elif cmd == "update":	
		commander.start (index, True)		
	elif cmd == "delete":	
		commander.start (delete)	
	else:	
		print ('error: unknow command')
