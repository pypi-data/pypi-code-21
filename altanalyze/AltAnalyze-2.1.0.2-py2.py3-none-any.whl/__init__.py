__version__ = "2.1.1"
import os
import subprocess
import shutil
import site
import sys
import zipfile
from os.path import expanduser
userdir = expanduser("~")
os.chdir(userdir)
try:
	os.mkdir("altanalyze")
except:
	pass
try:
	if(os.name == 'nt'):
		pypackpath = site.getsitepackages()[0] + '\Lib\site-packages'
	else:	
		pypackpath = site.getsitepackages()[0]
except:
	if(os.name == 'nt'):	
		pypackpath = os.path.dirname(site.__file__) + '\Lib\site-packages'
	else:		
		pypackpath = os.path.dirname(site.__file__) + '/site-packages'

def main():
    	"""Entry point for the application script"""
	os.chdir(pypackpath)	
	os.chdir("altanalyze")
	out = ""	
	if(len(sys.argv) > 1):
		out = sys.argv[1:]
		out.insert(0, "AltAnalyze.py")
		out.insert(0, "python")
	else:
		out = ["python", "AltAnalyze.py"]
	print(out)	
	pipe = subprocess.Popen(out)
	
    
