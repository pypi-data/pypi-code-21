# -*- coding: utf-8 -*-
from terminal import green
import re
import os
from ..util import client, config, formater, list2table, qsub_config
import json
import uuid
import base64
import tarfile
from ..const import  STRING, NUMBER
import socket


def qstat(for_job_id=None, all=False, waiting=False, running=False,
          user_list=None,


          job_id=None, nodes=None, ss=False,RR=False, QQ=False, qq=False, PBS=False,
          xx=None, ll=None, tt=None, mm=None,gg=None, one=None, ee=None):


    if for_job_id or job_id:
        get_job_info(for_job_id or job_id)
    else:
        state = []
        if waiting:
            state.append('Waiting')
        if running:
            state.append('Running')
        if all:
            state = []
        if not waiting and not running and not all:
            state = ['Waiting','Running']

        list(','.join(state), user_list)


def get_job_info(jobId):
    try:

       jobId = formater.get_job_id(jobId)
    except:
        raise Exception('Invalid jobId')

    result= client.get_job(jobId)
    #desc = client.get_job_description(jobId)

    print('Job Id: %s' % result.Id)

    for k,v in result.items():
        if k=='Id' or k=='Message':
            continue

        if isinstance(v, STRING):
           print('%s=%s' % (k,v))
        elif isinstance(v, NUMBER):
            print('%s=%s' % (k, v))




def list(state='Waiting,Running', user_list=None):
    result = client.list_jobs()
    arr = formater.items2arr(result.get('Items'))

    filter = {'Name': {'startswith':"qsub-"}}

    if user_list:
        users = user_list.split(',')
        filter['Name']['startswith'] = []
        for u in users:
          filter['Name']['startswith'].append('qsub-%s-' % u)

    # state filter
    if state:
        filter['State'] = state.split(',')

    #print(filter)
    arr = formater.filter_list(arr, filter)

    _print(arr)


def _print(arr):
    arr = formater.format_date_in_arr(arr, ['CreationTime', 'StartTime', 'EndTime'])
    list2table.print_table(arr, [('Id','job-Id',formater.hex_job_id), ('Name','name', get_job_name), ('State', 'state', formater.get_job_state_simple),
                                 ('Name', 'owner', get_user_id), ('CreationTime', 'submit at'), ('StartTime','start at'), ('EndTime', 'end at')],
                           show_no=False,show_border=False)

def get_job_name(name):
    if name and name.startswith('qsub-'):
        name = name[5:]
        return name[name.find('-')+1:]
    return name

def get_user_id(name):
    if name and name.startswith('qsub-'):
        name = name[5:]
        return name[:name.find('-')]
    return 'root'