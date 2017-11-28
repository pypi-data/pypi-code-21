print "Updating Clarissa"
import urllib2
import json
import os as os
import sys as sys
import logger as log
url = ""
try:
	if ( sys.argv[1] == "--from-url"):
		url = sys.argv[2]
	else:
		url = "http://softy.xyz/apps/sites/clarissa/get.php"
except IndexError:
	url = "http://softy.xyz/apps/sites/clarissa/get.php"
req = urllib2.Request(url)
opener = urllib2.build_opener()
f = opener.open(req)
json = json.loads(f.read())
for line in range(len(json)):
	file = open("bot_response.py",'a')
	existing_file = open("bot_response.py", 'r')
	if not os.path.isfile('bot_response.py'):
		file.write("import logger as log\n")
		file.write("def getResponse(messageToBot):\n")
	if not json[line]['command'] in existing_file.read() or not json[line]['reply']:
		file.write("\n\telif(\""+json[line]['command']+"\" in messageToBot):")
		file.write("\n\t\t\tprint \"Clarissa: "+json[line]['reply']+"\"")
		file.write("\n\t\t\tlog.log(\"chat.log\",\""+json[line]['reply']+"\")")
	commandList = open("commands.list", "a")
	commandList.write(json[line]['command']+"\n")
	commandList.flush()
	commandList.close()
	file.flush()
	file.close()
print "Update was successful"