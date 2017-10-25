from delune import indexinfo
from delune.lib import confparse, logger
from . import classifier
from delune.searcher import searcher
from delune.searcher import memory
import os

class Classifier:
	def __init__ (self, path, debug = False):	
		memory.create (1, 32768, 100, "segment")
		lg = logger.screen_logger ()
		conf = confparse.ConfParse (path)
		
		base_index = os.path.join (os.path.split (conf.getfilename ()) [0], os.path.split (conf.getopt ("common", "base_index"))[-1])		
		si = indexinfo.IndexInfo (confparse.ConfParse (base_index))
		base_schr = searcher.Searcher (si, lg)
		
		inf = indexinfo.IndexInfo (conf)
		self.f = classifier.Classifier (inf, base_schr, lg)
		self.f.initialize ()
		
	def query (self, *args, **karg):	
		return self.f.query (*args, **karg)
	
	def guess (self, *args, **karg):
		return self.f.guess (*args, **karg)
	
	def close (self):
		self.f.close ()
	
		
if __name__ == "__main__":
	import odbc
	f = Classifier (r"D:\bladepub\search\etc\col\fsc.class")
		
	dbc = odbc.odbc ("pepsi")
	c = dbc.cursor ()
	c.execute ("""
		select top 3 left (egcc, 4) unspsc, 
		isnull (title, '') + ' ' + isnull (seg, '') + ' ' + isnull (fam, '') + ' '+ isnull (cla, '') + ' ' + isnull (com, '') as description
		from iisd.dbo.trainset_unspsc
		where lang = 0 and substring (egcc, 3, 2) <> '00'		
	""")

	matched = 0
	processed = 0
	unclassified = 0
	agreed = 0
	c1 = 0
	c2 = 0
	c3 = 0

	items = c.fetchall ()
	for item in items:	
		processed += 1
		unspsc, title = item
		#res = f.query (title, engine = "id3")
		res = f.guess (title)
		res = res [4:]
		
		if res:
			print(unspsc, res [:2])
			if type (res [0]) == type (()):
				if res [0][0] == unspsc:
					matched += 1
			else:	
				if res [0] == unspsc:
					matched += 1
		else:
			unclassified += 1
	f.close ()
	
	print("_" * 79)
	print((
		"Processed: %d\n"
		"Unclassified: %d\n"
		"Matched: %d\n"
		"Agree: %d\n"
		"1 Class: %d\n"
		"2 Classes: %d\n"
		"3 Classes: %d\n"

		"Accuracy: %2.3f%%\n" % (processed, unclassified, matched, agreed, c1, c2, c3, float (matched) / (processed - unclassified) * 100)
	))

	c.close ()
	dbc.close ()
	