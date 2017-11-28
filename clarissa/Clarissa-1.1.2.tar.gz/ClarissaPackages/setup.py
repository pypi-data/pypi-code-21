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
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
def setClarissaSetting(key, value):
	if not(os.path.isdir(os.environ['CLARISSA_PATH']+"/Settings")):
		os.mkdir(os.environ['CLARISSA_PATH']+"/Settings")
	setting_path = os.environ['CLARISSA_PATH']+"/Settings/Clarissa.settings"
	try:
		existing = open(setting_path, 'r')
		for line in existing.readlines():
			if key in line:
				val = line.replace(key+"=", "")
				replace(setting_path, key+"="+val, key+"="+value+"\n")
				return None
	except IOError:
		print ""
	file = open(setting_path, 'a') #open with append privileges
	file.write("\n"+key+"="+value)
	file.flush()
	file.close()
def setupClarissa(install_path):
	if(os.path.isfile(".setup_ext")):
		os.system("rm .setup_ext")
		del_settings = raw_input("This will delete your current settings. Do you wish to continue? (Y/N)")
		if "y" in del_settings.lower():
			os.system("rm -R Settings")
		else:
			print ""
	print "Setting up Clarissa. This should not take long."
	try:
		setup = open(os.environ['USERPROFILE']+"/._clarissa.py", 'w')
	except KeyError:
		setup = open(os.environ['HOME']+"/._clarissa.py", 'w')
	setup.write("import os\n")
	setup.write("os.environ['CLARISSA_PATH']=\""+install_path+"\"")
	setup.flush()
	setup.close()
	os.environ['CLARISSA_PATH'] = install_path
	out = open('.setup_ext','a')
	out.write("install="+os.environ['CLARISSA_PATH'])
	out.flush()
	out.close()
	name_q = raw_input("Do you wish to add a user name? (Y/N)")
	if name_q.lower() is "y" or "yes":
		setClarissaSetting("user.name", raw_input("User name: "))
	else:
		return None


try:
	setupClarissa(sys.argv[1])
except IndexError:
	print "Run python setup.py [CLARISSA_INSTALL_PATH]"