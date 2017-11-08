import time
import datetime
import urllib
import itertools
import tarfile
import os
from hashlib import md5

from .constants import (
    ENDPOINT_INFO, STRING, PY2, PY3, PY25, UTC_FORMAT, API_VERSION,
)
from batchcompute.utils import constants


class ConfigError(Exception):
    def __init__(self, msg):
        super(ConfigError, self).__init__()
        self._msg = msg

    def __str__(self):
        return self._msg


def import_json():
    try:
        import json
    except ImportError:
        import simplejson as json
    return json


def import_httplib():
    try:
        import httplib
    except ImportError:
        import http.client as httplib
    return httplib


def str_md5(s):
    s = md5(str(s).encode('utf-8')).hexdigest()
    return s


def utf8(s):
    if not isinstance(s, str):
        s = s.encode('utf-8')
    return s


def url_safe(s):
    if isinstance(s, STRING):
        if PY2:
            s = urllib.quote(s, '')
        else:
            s = urllib.parse.quote(s, '')
    return s


def iget(d, key):
    '''
    A function for getting value while ignoring case sensitive of the key.
    '''
    _ = lambda s: s.strip().lower()
    ret = ''
    for (k, v) in d.items():
        if _(k) == _(key):
            ret = v
    return ret

def add_region(region, url, port=80):

    ENDPOINT_INFO[region] = url
    constants.SERVICE_PORT = port

def get_region(endpoint):
    ret = ''
    if endpoint.strip():
        for region, url in ENDPOINT_INFO.items():
            if endpoint == url:
                return region
        else:
            raise ConfigError('Invalid endpoint %s' % endpoint)
    else:
        raise ConfigError('Empty endpoint string')

def get_all_region():
    global ENDPOINT_INFO

    return ENDPOINT_INFO 

def gmt_time():
    return time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())


def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt

def datetime_timestamp(dt):
     time.strptime(dt, '%Y-%m-%d %H:%M:%S')
     s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
     return int(s)

def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*(args + fargs), **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc


def add_metaclass(cls, mcls):
    body = vars(cls).copy()
    # clean out class body
    body.pop('__dict__', None)
    body.pop('__weakref__', None)
    return mcls(cls.__name__, cls.__bases__, body)

def timediff(delta):
    if delta:
        t  = datetime.timedelta(seconds=delta)
        time_day = t.days
        s_time = t.seconds
        ms_time = t.microseconds // 1000000
        usedtime = int(s_time + ms_time)
        time_hour = usedtime // 60 // 60
        time_minute = (usedtime - time_hour * 3600 ) // 60
        time_second =  usedtime - time_hour * 3600 - time_minute * 60
        time_micsecond = (t.microseconds - t.microseconds // 1000000) // 1000

        tags = ['Day', 'Hour', 'Minute', 'Second']
        time_info = {
            'Day': time_day,
            'Hour': time_hour,
            'Minute': time_minute,
            'Second': time_second
        }

        time_list = []
        for tag in tags:
            if time_info[tag] > 1:
                new_tag = tag + 's'
            elif time_info[tag] > 0:
                new_tag = tag
            else:
                new_tag = None
            if new_tag:
                time_list.append('%s %s' % (time_info[tag], new_tag))
        retstr = ' '.join(time_list)
    else:
        retstr = '0'
    return retstr

def get_local_ip():
    import socket
    host_name = socket.getfqdn(socket.gethostname())
    host_addr = socket.gethostbyname(host_name)
    return host_addr

def do_tar(worker_dir, tar_file):
    '''
    A function to tar worker package.
    '''
    tar = tarfile.open(tar_file, 'w:gz')
    cwd = os.getcwd()
    os.chdir(worker_dir)
    for root,dir,files in os.walk('.'):
        for file in files:
            tar.add(os.path.join(root, file))
    os.chdir(cwd)
    tar.close()

def str2datetime(utc_timestr):
    # `utc_time_string` is a time string like "2015-11-11T10:00:57.246162Z" 
    utc_datetime = None 
    try:
        if utc_timestr.strip() and isinstance(utc_timestr, STRING):
            if PY25:
                # Microsecond is not supported in Python 2.5
                _ = ".000000Z"
                utc_timestr = utc_timestr[:-len(_)] + 'Z'
            utc_datetime = datetime.datetime.strptime(utc_timestr, UTC_FORMAT)
    except:
        utc_datetime = None 
    return utc_datetime 


def utc2local(utc_st):
    local_st = None 
    if utc_st and isinstance(utc_st, datetime.datetime):
        now_stamp = time.time()
        local_time = datetime.datetime.fromtimestamp(now_stamp)
        utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
        offset = local_time - utc_time
        local_st = utc_st + offset
    return local_st


def local2utc(local_st):
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st

def set_api_version(version):
    global API_VERSION

    if isinstance(version, STRING):
        API_VERSION = version
    else:
        raise ConfigError("Version must be string")

def get_api_version():
    global API_VERSION

    return API_VERSION
