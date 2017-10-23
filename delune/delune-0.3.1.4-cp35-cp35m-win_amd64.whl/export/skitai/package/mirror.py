import requests
import queue
import os
import delune
from delune import filesystem
from delune.lib import pathtool, logger as loggerlib
import threading, time
import socket, json
import pickle

mirror_server = None
DUPLICATE_LOCK = "duplicate-%s" % socket.getfqdn ()
DEBUG = True

def normpath (d):
	d = d.replace ("\\", "/")
	if DEBUG:
		d = d.replace ('D:/apps/', 'd:/var/')
	return d

def remove_end_slash (url):
	while url:
		if url [-1] != "/":
			return url
		url = mirror_server [:-1]	
			
def download (session, item):
	global mirror_server
	
	col, entity, group, fn, savepath	= item
	pathtool.mkdir (os.path.split (savepath)[0])
	url = "%s/%s/%s/%s/%s" % (mirror_server, col, entity, group, fn)		
	surl = "/%s/%s/%s/%s" % (col, entity, group, fn)		
	logger ("downloading from %s" % url)
	
	response = session.get(url, stream=True)
	cl = int (response.headers ["Content-Length"])						
	rl = 0
	
	if not response.ok:
		logger ("download failed  HTTP %d: %s" % (response.status_code, url), 'fail')
		return -1
		
	with open(savepath, 'wb') as handle:
		if cl:
			for block in response.iter_content(1024):
				rl += len (block)
				if rl % 1024000 == 0:
					logger ("%d%% downloaded %s" % (rl/cl * 100, surl))
				handle.write(block)				
			logger ("downloaded %d of %d (%d%%) from %s" % (rl, cl, rl/cl * 100, surl))
			
	if rl != cl:
		logger ("incomplete download: %s" % url, 'fail')
		return -1
	return 1			

def mirror ():
	global mirror_server, q, config_dir
	
	remote_session = requests.Session ()
	while 1:
		col = q.get ()
		if not col:
			break
			
		logger ("%s mirroring started" % col)
		remote_session.post ("%s/%s/locks/%s" % (mirror_server, col, DUPLICATE_LOCK))
		r = remote_session.get ("%s/%s" % (mirror_server, col))
		status = r.json ()
		
		local_col = delune.collection (indexdir = [normpath (d) for d in status ['indexdirs']], mode = delune.MODIFY)		
		if local_col.lock.islocked ("replicate"):
			if flock.isCurrentProcess (int (local_col.lock.lockread ("replicate")), 'python'):
				logger ("already under replicate, terminated")
				continue
		local_col.lock.lock ("replicate", str (os.getpid ()))
				
		keep_going = True		
		for name, ctime in status ["locks"]:
			if name == "index":
				logger ("origin %s is under indexing, skip updating index..." % col)
				keep_going = False
				break
		
		if keep_going:
			local_segments = status ["segments"][0]
			if not os.path.isfile (local_segments):
				local_latest_segments = -1				
			else:
				with open (local_segments, "rb") as f:
					temp = pickle.load (f)
				local_latest_segments = max (list(temp.segmentInfo.keys ()))
			origin_segments = [seginfo [0] for seginfo in status ['segmentinfos']]
			
			if not origin_segments:
				logger ("origin %s is empty" % col)
				keep_going = False
			elif max (origin_segments) < local_latest_segments:
				logger ("origin %s is older version, maybe next time..." % col)
				keep_going = False
		
		que = []
		new_file = False		
		if keep_going:
			for d in status ['indexdirs']:
				pathtool.mkdir (normpath (d))
			
			for group in status ["segmentfiles"]:
				segs = status ["segmentfiles"][group]			
				if 'segments' in segs:
					sfn = segs.pop ('segments')[0]
					dfn = normpath (sfn)
					if group == "primary":
						que.append ((col, 'collection', group, "segments", dfn + ".new"))
					else:
						que.insert (0, (col, 'collection', group, "segments", dfn))
				
				for seg, files in segs.items ():
					if group == "primary" and int (seg) not in origin_segments:
						continue
					
					for sfn, ssize, smtime in files:
						dfn = normpath (sfn)
						if not os.path.isfile (dfn):
							que.insert (0, (col, 'segments', group, str(seg) + sfn [-4:], dfn))
							new_file = True
						else:	
							dmtime = os.path.getmtime (dfn)
							dsize = os.path.getsize (dfn)
							if dsize == ssize and smtime <= dmtime:
								continue
							que.insert (0, (col, 'segments', group, str (seg) + sfn [-4:], dfn))
							new_file = True
				
		if new_file:
			failed = 0
			for item in que:
				#col, entity, group, fn, savepath
				if download (remote_session, item) == -1:
					failed += 1
			
			local_segments = status ["segments"][0]
			if failed:
				logger ("%s mirror failed, maybe mext time" % col, "fail")
				os.remove (local_segments + ".new")
			else:
				if os.path.isfile (local_segments):
					os.remove (local_segments)	
				os.rename (local_segments + ".new", local_segments)
				
		remote_session.delete ("%s/%s/locks/%s" % (mirror_server, col, DUPLICATE_LOCK))
		logger ("%s mirroring complete" % col)
		
		logger ("download configuration %s" % col)	
		colopt = status ["colopt"]
		dcolopt = normpath (colopt ['path'])
		if not os.path.isfile (dcolopt) or colopt ["mtime"] > os.path.getmtime (dcolopt) or colopt ["size"] != os.path.getsize (dcolopt):
			with open (dcolopt, "w") as out:
				out.write (json.dumps (colopt ['data']))			
			logger ("%s patch collection configure" % col)
		
		logger ("%s clean up unused segments" % col)		
		local_col.removeDeletables ()
		local_col.lock.unlock ("replicate")
		
		
if __name__ == "__main__":
	import sys, getopt
	from delune.lib import flock
	
	logger = loggerlib.screen_logger ()
	argopt = getopt.getopt(sys.argv[1:], "l:", ["log="])
	for k, v in argopt [0]:
		if k == "-l" or k == "--log":
			logger = loggerlib.multi_logger ([logger, loggerlib.rotate_logger (v, "delune", "daily")])
	
	lock = flock.Lock (os.path.dirname (__file__))
	if lock.islocked ("replicate"):
		if flock.isCurrentProcess (int (lock.lockread ("replicate")), 'python'):
			log ("another indexer is working")
			sys.exit ()	
	lock.lock ("replicate", str (os.getpid ()))
	
	if len (argopt [1])	 == 1:
		origin = argopt [1][0]		
	else:	
		print ('Usage: mirror.py origin')
		print ('  ex. mirror.py  http://192.168.1.200:5000/v1')
		sys.exit ()	
	
	mirror_server = remove_end_slash (origin)		
	session = requests.Session ()
	origin_side = session.get ("%s/" % mirror_server).json () ["collections"]
	if not origin_side:
		logger ("no collection to replicate" % col)
		sys.exit ()
	
	r = session.get ("%s/%s" % (mirror_server, origin_side [0]))
	config_dir = os.path.dirname (r.json ()["colopt"]["path"])
	
	delune.configure (1, logger)
	q = queue.Queue ()
	for col in origin_side:		
		q.put (col)
	
	q.put (None)
	t = threading.Thread (target = mirror)
	t.start ()
	
	q.put (None)
	mirror ()
	t.join ()
	
	logger ("syncing collections")	
	for col in os.listdir (config_dir):
		if col not in origin_side:
			os.rename (os.path.join (config_dir, col), os.path.join (config_dir, "-" + col))
			logger ("collection %s has been removed" % col)	
	logger ("all replication process is done.")		
	lock.unlock ("replicate")
	