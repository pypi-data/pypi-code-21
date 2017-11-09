#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

import json
import httplib2
from xml.dom.minidom import parse
import xml.dom.minidom

#author: guojial@cn.ibm.com
#version: v1.00
#Date:   2017-11-09
#Last Modified by: guojial@cn.ibm.com
#Last Modified time: 2017-11-09

class ibmBluepages:
    
    def getPersonInfoByIntranetID(self, intranetID):
        
        http = httplib2.Http() 
        content = http.request("https://bluepages.ibm.com/BpHttpApisv3/slaphapi?ibmperson/mail="+intranetID+".list/byxml", "GET")
        #print(content)
        
        DOMTree = xml.dom.minidom.parseString(content[1])
        collection = DOMTree.documentElement
        
        attrs = collection.getElementsByTagName("attr")
        
        attrData = {}
        for attr in attrs:
            #print (attr.getAttribute('name') + "  :  " + attr.getElementsByTagName('value')[0].childNodes[0].data)
            attrData[attr.getAttribute('name')] = attr.getElementsByTagName('value')[0].childNodes[0].data
        
        #print(attrData)
        personInfo = json.dumps(attrData)
        #print(personInfo)
        return personInfo