# 2017. 3. 13 by Hans Roh (hansroh@gmail.com)

from skitai.saddle import Saddle
import skitai
import delune
from delune.lib import pathtool
import os
import json
import codecs
import time
import shutil

app = Saddle (__name__)
app.config.numthreads = 1
app.last_maintern = time.time ()

def getdir (*d):
	return os.path.join (app.config.resource_dir, *d)

def is_json (request):
	return request.command == "post" and not request.get_header ('content-type', '').startswith ('application/x-www-form-urlencoded')

def normpath (path):
	if os.name == "nt":
		return path.replace ("/", "\\")
	return path.replace ("\\", "/")
			
def load_data (alias, numthreads, plock):
	with codecs.open (getdir ("models", ".config", alias), "r", "utf8") as f:
		colopt = json.loads (f.read ())			
		colopt ['data_dir'] = [getdir (normpath(d)) for d in colopt ['data_dir']]
	
	if 'classifier' in colopt:
		analyzer = delune.standard_analyzer (10000, numthreads, **colopt ["analyzer"])
		col = delune.model (colopt ["data_dir"], delune.READ, analyzer, plock = plock, version = colopt.get ("version", 1))
		actor = col.get_classifier (**colopt.get ('classifier', {}))
	else:
		analyzer = delune.standard_analyzer (8, numthreads, **colopt ["analyzer"])
		col = delune.collection	(colopt ["data_dir"], delune.READ, analyzer, plock = plock, version = colopt.get ("version", 1))	
		actor = col.get_searcher (**colopt.get ('searcher', {}))
		actor.create_queue ()
	delune.assign (alias, actor)

def error (response, status, errcode, errmsg = "", errstack = None):
	err = response.eapi (errmsg, errcode, exc_info = errstack)
	return response (status, err)
		
#-----------------------------------------------------------------

@app.startup
def startup (wasc):
	app.config.numthreads = len (wasc.threads)
	delune.configure (app.config.numthreads, wasc.logger.get ("app"), 16384, 128)
	pathtool.mkdir (getdir ("models", ".config"))
	for alias in os.listdir (getdir ("models", ".config")):
		if alias.startswith ("-"):
			with codecs.open (getdir ("models", ".config", alias), "r", "utf8") as f:
				colopt = json.loads (f.read ())
			for d in [getdir (normpath(d)) for d in colopt ['data_dir']]:
				if os.path.isdir (d):
					shutil.rmtree (d)
			os.remove (getdir ("models", ".config", alias))
		elif alias.startswith ("#"):
			continue
		else:
			load_data (alias, app.config.numthreads, wasc.plock)
  
@app.shutdown
def shutdown (wasc):
	delune.shutdown ()

#-----------------------------------------------------------------

@app.before_request
def before_request (was):
	with app.lock:
		last_maintern = was.getlu ("delune:collection") > app.last_maintern and app.last_maintern or 0
		if last_maintern:
			app.last_maintern = time.time ()
	
	if last_maintern:
		was.log ('collection changed, maintern...')
		for alias in os.listdir (getdir ("models", ".config")):			
			if alias [0] in "#-":
				if delune.get (alias [1:]):
					delune.close (alias [1:])
			elif not delune.get (alias):						
				load_data (alias, app.config.numthreads, was.plock)			
			elif os.path.getmtime (getdir ("models", ".config", alias)) > last_maintern:
				delune.close (alias)
				load_data (alias, app.config.numthreads, was.plock)

	if was.request.args.get ('alias') and was.request.routed.__name__ != "config":
		alias = was.request.args.get ('alias')
		if not delune.get (alias):
			return error (was.response, "404 Not Found", 40401, "resource %s not exist" % alias)
		
@app.failed_request
def failed_request (was, exc_info):
  return error (
  	was.response, 
  	"500 Internal Server Error", 
  	50000, 
  	errstack = app.debug and exc_info or None
  )

#-----------------------------------------------------------------

@app.route ("/")
def index (was):
	return was.response.api ({'collections': list (delune.status ().keys ())})	

@app.route ("/<alias>", methods = ["GET", "POST", "PATCH", "DELETE", "OPTIONS"])
def config (was, alias, side_effect = ""):
	fn = getdir ("models", ".config", alias)
	if was.request.command == "get":
		if side_effect == "undo":
			for mark in "#-":
				if os.path.isfile (getdir ("models", ".config", mark + alias)):
					os.rename (
						getdir ("models", ".config", mark + alias),
						getdir ("models", ".config", alias)
					)
					was.setlu ("delune:collection")					
					return was.response ("201 Accept", was.response.api ())
			return error (was.response, "404 Not Found", 20100, "resource already commited")
		
		if not delune.get (alias):
			return error (was.response, "404 Not Found", 40401, "resource %s not exist" % alias)
			
		status = delune.status (alias)
		conf = getdir ("models", ".config", alias)
		with codecs.open (conf, "r", "utf8") as f:
			colopt = json.loads (f.read ())		
			status ['colopt'] = {
				'data': colopt,
				'mtime': 	os.path.getmtime (conf),
				'size': 	os.path.getsize (conf),
				'path': conf
			}
		return was.response.api (status)
			
	if was.request.command == "delete":
		if not os.path.isfile (fn):
			return error (was.response, "404 Not Found", 40401, "resource not exist")
		
		a, b = os.path.split (fn)
		if side_effect == "data":
			newfn = os.path.join (a, "-" + b)
		else:
			newfn = os.path.join (a, "#" + b)		
		os.rename (fn, newfn)
		was.setlu ("delune:collection")
		return was.response.api ()
	
	for mark in "#-":
		if os.path.isfile (getdir ("models", ".config", mark + alias)):			
			return error (was.response, "406 Conflict", 40601, "removed resource is already exists, use UNDO")
			
	if was.request.command == "post" and delune.get (alias):
		return error (was.response, "406 Conflict", 40601, "resource already exists")		
	elif was.request.command == "patch" and not delune.get (alias):
		return error (was.response, "404 Not Found", 40401, "resource not exist")
			
	with codecs.open (fn, "w", "utf8") as f:
		f.write (was.request.body.decode ("utf8"))
	
	was.setlu ("delune:collection")		
	return was.response.api ()

#-----------------------------------------------------------------

@app.route ("/<alias>/locks", methods = ["GET", "OPTIONS"])
def locks (was, alias):	
	return was.response.api ({"locks": delune.get (alias).si.lock.locks ()})

@app.route ("/<alias>/locks/<name>", methods = ["POST", "DELETE", "OPTIONS"])
def handle_lock (was, alias, name):	
	if was.request.command == "post":
		delune.get (alias).si.lock.lock (name)		
		return was.response.api ()
	delune.get (alias).si.lock.unlock (name)
	return was.response.api ()

#-----------------------------------------------------------------

@app.route ("/<alias>/commit", methods = ["GET", "OPTIONS"])
def commit (was, alias):
	delune.get (alias).queue.commit ()
	return was.response.api ()

@app.route ("/<alias>/rollback", methods = ["GET", "OPTIONS"])
def rollback (was, alias):
	delune.get (alias).queue.rollback ()
	return was.response.api ()

#-----------------------------------------------------------------

@app.route ("/<alias>/collection/<group>/<fn>", methods = ["GET", "OPTIONS"])
def getfile (was, alias, group, fn):
	s = delune.status (alias)
	if group == "primary":
		path = os.path.join (s ["indexdirs"][0], fn)
	else:
		path = os.path.join (s ["indexdirs"][0], group, fn)
	return was.response.file (path)

@app.route ("/<alias>/segments/<group>/<fn>", methods = ["GET", "OPTIONS"])
def getsegfile (was, alias, group, fn):
	s = delune.status (alias)
	seg = fn.split (".") [0]
	if group == "primary":
		if seg not in s ["segmentsizes"]:
			return error (was.response, "404 Not Found", 40401, "resource not exist")
		path = os.path.join (s ["segmentsizes"][seg][0], fn)	
	else:
		path = os.path.join (s ["indexdirs"][0], group, fn)
	return was.response.file (path)

#-----------------------------------------------------------------

@app.route ("/<alias>/documents", methods = ["POST", "DELETE", "OPTIONS"])
def add (was, alias, truncate_confirm = ""):
	if was.request.command == "delete":
		if truncate_confirm != alias:
			return error (was.response, "400 Bad Request", 40003, 'parameter truncate_confirm=(alias name) required')
		delune.get (alias).queue.truncate ()		
		return was.response.api ()
		
	delune.get (alias).queue (0, was.request.body)
	return was.response.api ()

@app.route ("/<alias>/documents/<_id>", methods = ["GET", "DELETE", "PUT", "PATCH", "OPTIONS"])
def get (was, alias, _id, **args):
	if was.request.command == "get":
		if args.get ("q"):
			return error (was.response, "406 Conflict", 40602, "remove parameter q")
		return was.response.api (query (was, alias, q = "_id:" + _id, **args))
	
	delune.get (alias).queue (1, json.dumps ({"query": {'qs': "_id:" + _id}}))
	if was.request.command in ("patch", "put"):
		delune.get (alias).queue (0, was.request.body)

	return was.response.api ()

#-----------------------------------------------------------------
	
@app.route ("/<alias>/search", methods = ["GET", "POST", "DELETE" "OPTIONS"])
def query (was, alias, **args):
	if is_json (was.request):
		args = was.request.json ()
	
	q = args.get ("q")
	if not q:
		return error (was.response, "400 Bad Request", 40003, 'parameter q required')
	
	l = args.get ("lang", "en")
	analyze = args.get ("analyze", 1)
	
	if was.request.command == "delete":
		delune.get (alias).queue (1, json.dumps ({"query": {'qs': q, 'lang': l, 'analyze': analyze}}))
		return was.response.api ()
	
	o = args.get ("offset", 0)
	f = args.get ("limit", 10)
	s = args.get ("sort", "")
	w = args.get ("snippet", 30)	
	r = args.get ("partial", "")
	d = args.get ("nthdoc", 0)	
	data = args.get ("data", 1)
	
	if type (q) is list:
		return was.response.api ([delune.query (alias, eq, o, f, s, w, r, l, d, analyze, data, limit = 1) for eq in q])
	return was.response.api (delune.query (alias, q, o, f, s, w, r, d, l, analyze, data, limit = 1))

@app.route ("/<alias>/guess", methods = ["GET", "POST", "OPTIONS"])
def guess (was, alias, **args):	
	# args: q = '', l = 'en', c = "naivebayes", top = 0, cond = ""
	if is_json (was.request):
		args = was.request.json ()
	q = args.get ("q")
	if not q:
		return error (was.response, "400 Bad Request", 40003, 'parameter q required')				
	l = args.get ("lang", 'en')
	c = args.get ("clf", 'naivebayes')
	top = args.get ("top", 0)
	cond = args.get ("cond", '')
	if type (q) is list:
		return was.response.api ([delune.guess (alias, eq, l, c, top, cond) for eq in q])
	return was.response.api (delune.guess (alias, q, l, c, top, cond))
	
@app.route ("/<alias>/cluster", methods = ["GET", "POST", "OPTIONS"])
def cluster (was, alias, **args):
	if is_json (was.request):
		args = was.request.json ()
	q = args.get ("q")
	if not q:
		return error (was.response, "400 Bad Request", 40003, 'parameter q required')
	l = args.get ("lang", 'en')	
	if type (q) is list:
		return was.response.api ([delune.cluster (alias, eq, l) for eq in q])	
	return was.response.api (delune.cluster (alias, q, l))
