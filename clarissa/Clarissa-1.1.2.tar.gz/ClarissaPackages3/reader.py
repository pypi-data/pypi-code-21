import os
import sys

#Get Clarissa setting
def getClarissaSetting(key):
	file = open('.setup_ext', 'r')
	for line in file.readlines():
		if "install=" in line:
			os.environ["CLARISSA_PATH"] = line.replace("install=", "")

	install_loc = os.environ['CLARISSA_PATH']+"/Settings/Clarissa.settings"
	file = open(install_loc, 'r')
	for line in file.readlines():
		if key in line:
			return line.replace(key+"=", "")

def getClarissaSettingWithPath(path, key):
	if(os.path.isfile(path)):
		file = open(path, 'r')
		for line in file.readlines():
			if key in line:
				return line.replace(key+"=", "")
	else:
		return ""