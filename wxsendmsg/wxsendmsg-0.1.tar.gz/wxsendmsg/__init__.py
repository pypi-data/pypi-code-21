#!/usr/bin/python
#-*- encoding: utf-8 -*-
import requests
import json
import sys
import os
import requests
import time
import traceback
import logging


from .querytoken import query_token,get_token



logging.basicConfig(filename='/var/log/wxsendmsg.log',level=logging.DEBUG,format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a,%d,%Y %H:%M:%S')



def send_msg(url,gettoken,msg):
	try:
		url=url+gettoken

		post_param_data="""{
				"touser" : "dingyinggui",
				"msgtype" : "text",
				"agentid" : 1000002,
				"text" : {
					"content" : "%s"
					},
				"safe":0
				}"""%(msg)

		req=requests.post(url,json=json.loads(post_param_data),verify=False)
		print req.status_code
		print req.headers
		k=req.headers
		print 'sendmsg'
		return int(k['Error-Code'])
	except Exception as e:
		exc_var=traceback.format_exec()
		logging.debug(exc_var)
		return -1




