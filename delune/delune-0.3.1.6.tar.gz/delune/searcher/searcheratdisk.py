from delune import indexinfo
from delune.lib import confparse, logger
import memory
from . import searcher
from . import query

class Searcher:
	def __init__ (self, path, debug = 0):
		self.path = path
		query.Query.DEBUG = debug
		memory.create (1, 32768, 128, "segment", logger.screen_logger ())
		inf = indexinfo.IndexInfo (confparse.ConfParse (path))
		self.s = searcher.Searcher (inf)
		self.s.initialize ()

	def query (self, q, offset = 0, fetch = 0, *args, **karg):
		return self.s.query (q, offset, fetch, *args, **karg)


if __name__ == "__main__":
	f = Searcher (r"D:\bladepub\proto\etc\col\unifiedbid")
	d = f.query ("service", 0, 10, summary = 30)
	
	print(d [2], d [4])
	
	
	
	