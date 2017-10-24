#!/usr/bin/python3

import os
import delune
import skitai	

if __name__ == "__main__":
	pref = skitai.pref ()
	pref.use_reloader = 1
	pref.debug = 1
	
	config = pref.config
	config.sched = "0/5 * * * *"	
	config.local = "http://127.0.0.1:5000/v1"
	
	config.remote = os.environ.get ("DELUNE_MIRROR")
	config.enable_mirror = config.remote
	
	config.resource_dir = skitai.joinpath ('resources')
	config.enable_index = True
	
	config.logpath = None
	skitai.trackers ('delune:collection')
	skitai.mount ("/v1", delune, "app", pref)
	skitai.run (	
		workers = 2,
		port = 5000,
		logpath = config.logpath
	)
