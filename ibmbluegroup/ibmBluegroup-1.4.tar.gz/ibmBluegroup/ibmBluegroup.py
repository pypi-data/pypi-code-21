 #!/usr/bin/env python3
 # -*- coding: utf-8 -*- 

import httplib2
from xml.dom.minidom import parse
import xml.dom.minidom

#author: guojial@cn.ibm.com
#version: v1.0
#Date:   2017-10-27
#Last Modified by: guojial@cn.ibm.com
#Last Modified time: 2017-10-30

class ibmBluegroup:

	def __init__(self):

	#check the user exsit in group
	def userInGroup(self, intranetID, groupname):

		http = httplib2.Http() 
		content = http.request("https://bluepages.ibm.com/tools/groups/groupsxml.wss?task=listMembers&group="+groupname, "GET")
		#print(content)

		DOMTree = xml.dom.minidom.parseString(content[1])
		collection = DOMTree.documentElement
		
		#print(collection.getElementsByTagName("member")[0].childNodes[0].data)
		flag = False
		for member in collection.getElementsByTagName("member"):
			if (intranetID == member.childNodes[0].data):
				flag = True
				break
			else:
				flag = False
		#print(flag)
		return flag

	def listMembers(self, groupname):

		http = httplib2.Http() 
		content = http.request("https://bluepages.ibm.com/tools/groups/groupsxml.wss?task=listMembers&group="+groupname, "GET")
		#print(content)

		DOMTree = xml.dom.minidom.parseString(content[1])
		collection = DOMTree.documentElement
		
		#print(collection.getElementsByTagName("member")[0].childNodes[0].data)
		members = [];
		for member in collection.getElementsByTagName("member"):
			members.append(member.childNodes[0].data)
		#print(members)
		return members