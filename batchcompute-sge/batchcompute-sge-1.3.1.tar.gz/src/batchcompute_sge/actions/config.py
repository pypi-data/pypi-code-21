# -*- coding:utf-8 -*-

from terminal import  green,bold
from batchcompute_sge.lib import bccluster_json
from ..util.debugger import *

FALSE_ARR = ['', 'null', 'None', 'false', 'False']

def config(bcs_port=None, god=None):
    if not bcs_port and not god:
       show_config()
    else:
        if bcs_port:
            update_bcs_port(bcs_port)
        if god:
            update_god(god)

def update_god(god):
    obj = bccluster_json.get()
    god = god.strip()
    if god not in FALSE_ARR:
        obj['god'] = 'true'
        bccluster_json.save(obj)
    else:
        if obj.get('god'):
            del obj['god']
            bccluster_json.save(obj)


def update_bcs_port(port):
    obj = bccluster_json.get()

    if port not in FALSE_ARR:
        obj['bcs_port'] = port
        bccluster_json.save(obj)
    else:
        if obj.get('bcs_port'):
           del obj['bcs_port']
           bccluster_json.save(obj)


def show_config():
    obj = bccluster_json.get_required_login()

    arr = ['region','access_key_id', 'access_key_secret','master_security_group_id','master_vpc_id','cluster_id',
           'oxs_region', 'oxs_access_key_id', 'oxs_access_key_secret', 'bcs_port','god']
    try:
        for k in arr:
            if obj.get(k):
                v = hide_key(obj[k]) if ('access_key_secret' in k) else obj[k]
                print('%s: %s' %(bold(k), green(v)))
    except Exception as e:
        dstack()
        raise Exception('You need to login first')


def hide_key(s):
    if len(s) > 6:
        return "%s******%s" % (s[:3],s[-3:])
    elif len(s) > 1:
        return "%s*****" % s[:1]
    else:
        return "******"