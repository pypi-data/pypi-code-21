import os
import sys
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Remove original file
    #remove(file_path)
    #Move new file
    move(abs_path, file_path)
def setClarissaSettingWithPath(path, key, value):
	file = open(path, 'a')
	file.write("\n"+key+"="+value)
	file.flush()
	file.close()
def setClarissaSetting(key, value):
	file = open('.setup_ext', 'r')
	for line in file.readlines():
		if "install=" in line:
			os.environ['CLARISSA_PATH'] = line.replace('install=', '')
	if not(os.path.isdir(os.environ['CLARISSA_PATH']+"/Settings")):
		os.mkdir(os.environ['CLARISSA_PATH']+"/Settings")
	setting_path = os.environ['CLARISSA_PATH']+"/Settings/Clarissa.settings"
	try:
		existing = open(setting_path, 'r')
		for line in existing.readlines():
			if key in line:
				val = line.replace(key+"=", "")
				replace(setting_path, key+"="+val, "\n"+key+"="+value)
				return None
	except IOError:
		print ""
	file = open(setting_path, 'a') #open with append privileges
	file.write("\n"+key+"="+value)
	file.flush()
	file.close()