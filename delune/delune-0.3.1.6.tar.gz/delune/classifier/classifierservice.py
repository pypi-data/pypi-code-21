#-----------------------------------------------------------------
# Services
#-----------------------------------------------------------------			
def classify (self, col, query, offset = 0, fetch = 3):
	try:
		classifier = self.searchers [col].classifier
	except:
		return  [404, 0, 0, '']
	
	query = query.strip ()
	if len (query) < 2:
		return  [403, 0, 0, query]
		
	try: tid = threading.currentThread ().getId ()
	except AttributeError: tid = 0
		
	try:	
		result = classifier.guess (self.mpool.get (tid), query, offset, fetch)
	except MemoryError:			
		return self.recover (tid)
		
	self.maintern (tid)
	return result
		
		
		
		
