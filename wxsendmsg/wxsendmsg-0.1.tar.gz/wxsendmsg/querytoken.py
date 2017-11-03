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



logging.basicConfig(filename='/var/log/wxsendmsg.log',level=logging.DEBUG,format='%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s',datefmt='%a,%d,%Y %H:%M:%S')

CACHE={}
CACHE_MAX_AGE=60*60*2

try:
        import json
except:
        import simplejson as json



def cache_load(cf):
        if not os.path.isfile(cf): return
        global CACHE
        f=open(cf,'r')
        try: CACHE=json.load(f)
        except:
		exc_var=traceback.format_exc()
		logging.debug(exc_var)
	finally:
        	f.close()


def cache_save(cf):
        global CACHE
	try:
        	f=open(cf,'w')
        	json.dump(CACHE,f)
	except:
		exc_var=traceback.format_exec()
		logging.debug(exc_var)
	finally:
		f.close()

def get_token(url,corpid,secret):
        try:
                get_param_data={'corpid':corpid,'corpsecret':secret}
                req=requests.get(url,params=get_param_data,verify=False)
                print req.status_code
                print req.raise_for_status()
                t=(json.loads(req.text))
                return t['access_token']
        except Exception,e:
                exc_var=traceback.format_exec()
		logging.debug(exc_var)
                return e

def query_token(url,corpid,secret,cache_file=None,force=0):
        if cache_file: cache_load(cache_file)
	print 'cache_file'
	print 'force=',force
	print 'CACHE=',CACHE
        if force or secret not in CACHE or CACHE[secret][0]<time.time()-CACHE_MAX_AGE:
                CACHE[secret]=(
                        int(time.time()),get_token(url,corpid,secret),
                )
                if cache_file: cache_save(cache_file)
        return CACHE[secret][1]


