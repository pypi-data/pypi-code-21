import skitai
import sys, os
from .package import mirror, indexer

def bootstrap (pref):	
	config = pref.config
	
	script = None
	logpath = config.get ("logpath")
	logopt = logpath and "--log=%s" % logpath or ""
	if config.get ("enable_mirror", False):
		script = "%s %s %s" % (mirror.__file__, logopt, config.remote)
	elif config.get ("enable_index", False):
		script = "%s %s %s" % (indexer.__file__, logopt, config.resource_dir)
	
	if script:		
		skitai.cron (config.sched, r"%s %s%s" % (sys.executable, script, ''))
