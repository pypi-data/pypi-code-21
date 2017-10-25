import delune
from delune import binfile
from delune.searcher.indexer import ExitNow
from delune.searcher.segment import typeinfo
from delune.lib import logger as loggerlib
import os, codecs, glob, json

resource_dir = None

def add_document (indexer, doc):
	document = delune.document ()	
	document.documents (doc ['documents'])
	if 'snippet' in doc and doc ['snippet']:		
		document.snippet (*tuple (doc ['snippet']))

	for name, opt in doc ['fields'].items ():
		if name == "_id":			
			data = str (opt)
			lang = 'un'
			ftype = delune.STRING
			option = []
			
		else:	
			data = opt.get ('data')
			if type (data) is str and data.startswith ("$document"):
				tree = data.split (".")
				if tree [0][9:] == "":
					index = 0
				else:	
					try: index = int (tree [0][9:])
					except ValueError: 
						raise TypeError ("document index is wrong")
						
				val = doc ['documents'][index]
				for dep in tree [1:]:
					if type (val) is dict:
						val = val.get (dep)
					else:
						try: val = val [int (dep)]
						except IndexError: val = None															
					if not val:
						break
				data = val
									
			ftype = opt.get ('type')
			if not ftype:
				raise TypeError ('Type of field is required')
			option = opt.get ('option', [])				
			lang = opt.get ('lang', 'un')
			
		document.field (name, data, ftype, lang, option = option)
	indexer.add_document (document)

def getdir (*d):
	global resource_dir	
	return os.path.join (resource_dir, *d)

def delete (col, opt, deletables):
	global log
	
	opt ['searcher']['remove_segment'] = 0
	searcher = col.get_searcher (**opt ['searcher'])
	if searcher.si.getN () == 0:
		searcher.close ()
		return 0
	
	deleted = 0
	for qs in deletables:
		qs ["commit"] = False
		deleted += searcher.delete (**qs)["total"]
		
	searcher.commit ()	
	searcher.close ()	
	log ('%d documents is deleted' % deleted)	
	return deleted
		
def index (path):	
	global log
	
	alias = os.path.split (path) [-1]
	if alias [0] in "#-":
		return
		
	with codecs.open (path, "r", "utf8") as f:
		colopt = json.loads (f.read ())
	
	colopt ['data_dir'] = [getdir (os.path.normpath(d)) for d in colopt ['data_dir']]
	
	analyzer = delune.standard_analyzer (3000, 1, **colopt ['analyzer'])
	col = delune.collection (
	  indexdir = colopt ['data_dir'],
	  mode = delune.APPEND,
	  analyzer = analyzer,
	  version = colopt.get ("version", 1)
	)		
	queue_dir = colopt ['data_dir']
	if type (queue_dir) is list:
		queue_dir = queue_dir [0]
	
	queue_dir = os.path.join (queue_dir, ".que")
	queues = [(os.path.basename (q), os.path.getmtime (q)) for q in glob.glob (os.path.join (queue_dir, 'que.*')) if not q.endswith (".lock")]
	if not queues:
		log ("nothing to for %s in %s" % (os.path.split (path) [-1], os.path.dirname (path)))
		col.removeDeletables ()
		return
	
	# reverse sort for trucate
	queues.sort (key = lambda x: x [-1], reverse = True)
	index = 0
	for gfile, mtime in queues:
		if gfile == "que.truncate":
			break
		index += 1
	
	if index < len (queues):
		log ("%s found trcuate request" % alias)
		for qfile, mtime in queues [index:]:
			os.remove (os.path.join (queue_dir, qfile))
		queues = queues [:index]
		indexer = col.get_indexer (**colopt ['indexer'])
		indexer.truncate ()	
		indexer.close ()
	
	deleted = 0
	deletables = []
	# resort from old one
	queues.reverse ()	
	for qfile, mtime in queues:
		bf = binfile.BinFile (os.path.join (queue_dir, qfile), "r")
		while 1:
			try: cmd = bf.readVInt ()
			except OSError:
				bf.close ()
				break
			
			try:
				doc = json.loads (bf.readZBytes ().decode ("utf8"))
			except (OSError, MemoryError):
				bf.close ()
				break
			
			if cmd == 1:
				qs = doc.get ("query")				
				deletables.append (qs)
				if len (deletables)	== 10000:
					# too many, commit forcely
					deleted += delete (col, colopt, deletables)
					deletables = []
	
	if deletables:
		deleted += delete (col, colopt, deletables)
	log ('%d documents deleted in this session' % deleted)
			
	indexer = col.get_indexer (**colopt ['indexer'])	
	# mannual commit mode, ignore memory usage
	indexer.set_autocommit (False)
	
	indexed_docs = 0
	indexed_ques = []
	
	for qfile, mtime in queues:
		bf = binfile.BinFile (os.path.join (queue_dir, qfile), "r")
		while 1:
			try: cmd = bf.readVInt ()				
			except OSError:
				bf.close ()
				break
			
			if cmd == 1:	 # just delete
				bf.readZBytes ()
				continue
			
			try:
				doc = json.loads (bf.readZBytes ().decode ("utf8"))				
			except (OSError, MemoryError):
				bf.close ()
				break
			
			add_document (indexer, doc)
			indexed_docs += 1
			
		indexed_ques.append (os.path.join (queue_dir, qfile))		
		if maybe_commit (indexer, indexed_ques, indexed_docs):
			indexed_docs = 0
			indexed_ques = []

	maybe_commit (indexer, indexed_ques, indexed_docs, force = True)	
	indexer.close (optimize = deleted > 100)

def maybe_commit (indexer, indexed_ques, indexed_docs, force = False):	
	if force or indexer.is_memory_over ():
		# commit and delete queue for preventing duplication		
		if indexed_docs:
			indexer.commit ()
		for qpath in indexed_ques:
			log ('remove indexed que %s' % os.path.basename (qpath))
			os.remove (qpath)
		return 1
	return 0

			
if __name__ == "__main__":
	import sys, getopt
	from delune.lib import flock
	
	log = loggerlib.screen_logger ()
	argopt = getopt.getopt(sys.argv[1:], "l:", ["log="])

	for k, v in argopt [0]:
		if k == "-l" or k == "--log":
			log = loggerlib.multi_logger ([log, loggerlib.rotate_logger (v, "delune", "daily")])
	
	lock = flock.Lock (os.path.dirname (__file__))
	if lock.islocked ("index"):
		if flock.isCurrentProcess (int (lock.lockread ("index")), 'python'):
			log ("another indexer is working")
			sys.exit ()	
	lock.lock ("index", str (os.getpid ()))
			
	delune.configure (1, log)
	try:
		resource_dir = argopt [1][0]
	except IndexError:
		print ('Usage: mirror.py resource_dir')	
		print ('  ex. mirror.py /var/tmp/delune')	
		sys.exit ()
		
	conf_dir = os.path.join (resource_dir, "models", ".config")
	for alias in os.listdir (conf_dir):
		log ("starting index for %s" % alias)
		try:
			index (os.path.join (conf_dir, alias))
		except ExitNow:			
			log ("%s is indexing by another indexer" % alias)
			continue
		except:
			log.trace ()			
		log ("index done for %s" % alias)
	log ("index complete")	
	lock.unlock ("index")
	