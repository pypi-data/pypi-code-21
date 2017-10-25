# 2014. 12. 9 by Hans Roh hansroh@gmail.com

__version__ = "0.3.1.6"
version_info = tuple (map (lambda x: not x.isdigit () and x or int (x),  __version__.split (".")))

from .analyzers import standardAnalyzer
from .searcher import collection
from .classifier import model
from . import memory
from . import analyzers
import platform
import os
from .searcher import indexer, document
from .classifier import trainer, labeld_document
import threading
import importlib

PID = None

standard_analyzer = standardAnalyzer.Analyzer

def get_analyzer (name = "standard"):
	mod = importlib.import_module ("delune.analyzers." + name + "Analyzer")
	return getattr (mod, "Analyzer")
	
collection = collection.Collection
model = model.Model

document = document.Document
labeled_document = labeld_document.LabeledDocument

# Searchable Field Types
TEXT = "Text"
TERM = "Term"
STRING = "String"
LIST = "List"
FNUM = "Fnum"
COORD = "Coord4" 
COORD4 = "Coord4" # 4 decimals, 10 M precision
COORD6 = "Coord6" # 6 decimals, 10 CM precision
COORD8 = "Coord8" # 8 decimals, 1 MM precision
BIT8  = "Bit8"
BIT16 = "Bit16"
BIT24 = "Bit24"
BIT32 = "Bit32"
BIT40 = "Bit40"
BIT48 = "Bit48"
BIT56 = "Bit56"
BIT64 = "Bit64"
INT8  = "Int8"
INT16 = "Int16"
INT24 = "Int24"
INT32 = "Int32"
INT40 = "Int40"
INT48 = "Int48"
INT56 = "Int56"
INT64 = "Int64"

# Both Classifiers & Term Clustering
ALL = "default"

# Classifiers
NAIVEBAYES = "naivebayes"
FEATUREVOTE = "featurevote"
TFIDF = "tfidf"
SIMILARITY = "similarity"
ROCCHIO = "rocchino"
ROCCHINO = "rocchino"
MULTIPATH = "multipath"
META = "metaclassifier"

# Term Clustering
TERMCLUSTER = "termcluster"

# Feature Scoring
CHI2 = "chi"
GSS = "gss"
DF = "df"
CF = "cf"
NGL = "ngl"
MI = "mi"
TFIDF = "tfidf"
IG = "ig"
OR = "or"
OR4P = "or4p"
RS = "rs"
LOR = "lor"
COS = "cos"
PPHI = "pphi"
YULE = "yule"
RMI = "rmi"

# Feature Scoring Used For Term Clustring Only
R = "r"

# Scoring Value
SUM = "sum"
MAX = "max"
AVG = "avg"
MIN = "min"

# Open Modes
WRITE = "w"
APPEND = "w"
MODIFY = "w"
READ = "r"
CREATE = "c"

osbit, __x = platform.architecture()
if osbit == "64bit":
	LIMIT_SEGMENTSIZE = 10000000000	# 2**39, 10GB but max 500GB is possible
else:
	LIMIT_SEGMENTSIZE = 1900000000 # 2**31, 2GB
LIMIT_FILESIZE = int (LIMIT_SEGMENTSIZE * 0.7)

logger = None
	
class Task:
	def __init__ (self, logger):
		self.logger = logger
		self.lock = threading.RLock ()
		self._d_ = {}
		
	def cleanup (self):
		with self.lock:
			reactors = self._d_.items ()
		for alias, reactor in reactors:
			self.logger ("...delune closing %s" % alias, "info")
			reactor.close ()
			
	def __contains__ (self, alias):
		with self.lock:
			return (alias in self._d_)
	
	def __getattr__ (self, alias):
		return self.get (alias)
	
	def __delattr__ (self, alias):		
		self.resign (alias)

	def __dir__ (self):
		with self.lock:
			return list (self._d_.keys ())
	
	def __len__ (self):
		with self.lock:
			return len (self._d_)
	
	def swap (self, a, b):
		with self.lock:
			t = self._d__ [a]
			self._d__ [a] = b
			self._d__ [b] = t
		
	def assign (self, alias, obj):
		obj.si.set_ident (alias)
		with self.lock:
			self._d_ [alias] = obj
	
	def resign (self, alias):
		with self.lock:
			del self._d_ [alias]
		
	def get (self, alias):
		with self.lock:
			return self._d_.get (alias)
	
	def status (self):
		d = {}
		with self.lock:
			for alias, reactor in self._d_.items ():
				d [alias] = reactor.status ()
		return d
		

class NoTask:
	def __getattr__ (self, name):
		raise AssertionError ("delune not configured, configure first")

task = NoTask ()

def configure (numthread, logger_t, io_buf_size = 16384, mem_limit = 128, max_segment_size = 0):
	global logger, task, PID
	
	if isinstance (task, Task):
		return
	
	PID = os.getpid ()		
	logger = logger_t
	if max_segment_size:
		set_max_segment_size (max_segment_size)
		
	if not memory.isInitialized ():
		memory.initialize (numthread, io_buf_size, mem_limit, "segment", logger_t)
		analyzers.buildFactory (numthread, logger_t)
	
	task = Task (logger)
	return task
	
def shutdown ():
	global task
	
	if task is None:
		return
		
	if isinstance (task, Task):
		task.cleanup ()
		
	if memory.isInitialized ():
		analyzers.close ()
		memory.destroy ()
	
	task = None	

# For Skitai
cleanup = shutdown

def set_max_segment_size (mbytes):
	global LIMIT_SEGMENTSIZE, LIMIT_FILESIZE
	LIMIT_SEGMENTSIZE = int (mbytes * 1000000)
	LIMIT_FILESIZE = int (LIMIT_SEGMENTSIZE * 0.7)

def qualify_analyzer (analyzer):
	if memory.isInitialized ():
		return analyzers.checkIn (analyzer) 
	return analyzer	


#=========================================
# query and guess by task alias
#=========================================

#--------------------
# common jobs
#--------------------
	
def assign (alias, obj):
	global task
	task.assign (alias, obj)
	
def resign (alias):
	global task
	task.resign (alias, obj)
		
def close (alias, *args, **karg):
	global task	
	reactor = task.get (alias)
	if not reactor.closed:
		reactor.close (*args, **karg)
	task.resign (alias)

def drop (alias):
	try:
		stu = status (alias)
	except KeyError:
		return
	close (alias)	
	for data_dir in stu ['indexdirs']:
		for fn in os.listdir (data_dir):
			os.remove (os.path.join (data_dir, fn))
	
def get (alias):
	global task
	return task.get (alias)

def status (alias = "", *args, **karg):
	global task
	if alias == "":
		return task.status ()
	return task.get (alias).status (*args, **karg)

def refresh (alias, *args, **karg):
	global task
	return task.get (alias).refresh (*args, **karg)	

#--------------------
# searcher only jobs	
#--------------------
def query (alias, *args, **karg):
	global task
	return task.get (alias).query (*args, **karg)

def delete (alias, *args, **karg):
	global task
	return task.get (alias).delete (*args, **karg)		

def remove (alias, *args, **karg):
	global task
	return task.get (alias).remove (*args, **karg)
	
def fetch (alias, *args, **karg):
	global task
	return task.get (alias).fetch (*args, **karg)	

#----------------------
# classifier only jobs	
#----------------------
def guess (alias, *args, **karg):
	global task
	return task.get (alias).guess (*args, **karg)	

def cluster (alias, *args, **karg):
	global task
	return task.get (alias).cluster (*args, **karg)	

def stem (alias, *args, **karg):
	global task
	return task.get (alias).stem (*args, **karg)	

def analyze (alias, *args, **karg):
	global task
	return task.get (alias).analyze (*args, **karg)	
