import sys
import os

class index_sync_handler:
	def __init__(self, wasc):
		self.wasc = wasc
		
	def match (self, request):
		if request.command.lower() == 'replicate':
			return 1
		return 0
	
	def handle_request (self, request):
		authinfo = request.get_header ('Authorization')
		#if not authinfo or not self.wasc.authorizer (authinfo):
		#	return request.error (403)		
		try:
			request.collector = collector (self, request)
		except:
			self.wasc.se.logger.trace ()	
				
	def continue_request (self, request, filename = ""):
		if not filename:
			return request.error (500)
		
		request.push ("Created %s\n" % filename)
		request.done ()
		

class collector:
	def __init__ (self, handler, request):
		self.handler = handler
		self.request = request
		
		cl = request.get_header ('content-length')
		if not cl:
			request.error (411)
						
		else:
			cl = int(cl)
			if not cl: 	self.found_terminator()
			self.request.channel.set_terminator (cl)
			
		self.fn = request.get_header ("se-filename")		
		if not self.fn: 
			request.error (500)
			return
		
		self.ft = request.get_header ("se-filetype")
		if not self.ft: 
			request.error (500)
			return
		
		self.col = request.get_header ("se-index")	
		if not self.col: 
			request.error (500)
			return
		
		if self.ft == "config":			
			self.__create_cfile ()
		elif self.ft == "segmentinfo":
			self.__create_sfile ()
		else:
			self.__create_ifile ()
	
	def collect_incoming_data (self, data):
		self.fp.write (data)

	def found_terminator (self):		
		self.fp.close ()
		self.request.channel.set_terminator ('\r\n\r\n')
		res = self.__commit_file ()
		
		if not res: self.filepath = ""
		self.handler.continue_request (self.request, self.filepath)

	def __get_searcher (self):
		searcher = self.handler.server.se.getsearcher (self.col)
		if not searcher:
			searcher = self.handler.server.se.create_searcher (os.path.join (os.environ ["INSTANCE_HOME"], "etc", "col", self.col))
		return searcher
	
	def __commit_file (self):
		if self.ft == "index":
			return 1
				
		if self.ft == "config":
			nfile = os.path.join (os.environ ["INSTANCE_HOME"], "etc", "col", self.col)
			
		else:
			nfile = self.filepath [:-4]
		
		try:
			try: os.remove (nfile)
			except OSError as why:
				if why [0] != 2:
					raise
					
			os.rename (self.filepath, nfile)
				
		except:
			self.handler.server.se.logger.trace ()
			return 0
			
		return 1
			
	def __create_cfile (self):
		self.filepath = os.path.join (os.environ ["INSTANCE_HOME"], "etc", "col", "#" + self.col + ".tmp")
		self.fp = open (self.filepath, "w")
	
	def __create_sfile (self, col, fn):		
		searcher = self.__get_searcher ()						
		path = searcher.actor.si.fs.getmaster ()
		self.filepath = os.path.join (path, fn + ".tmp")
		self.fp = open (self.filepath, "wb")		
		
	def __create_ifile (self):
		searcher = self.__get_searcher ()		
		segment = self.fn [:-4]
		path = searcher.actor.si.fs.get (segment)
		
		if not path:
			path = searcher.actor.si.fs.new ()
		
		self.filepath = os.path.join (path, fn)
		self.fp = open (self.filepath, "wb")
	
	