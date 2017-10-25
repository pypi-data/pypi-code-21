import datetime
import calendar
import time
from ..const import STRING
from terminal import green, white, red, yellow, cyan
import os
import re

def sub_desc(s):
    return s[0:20]+'...' if len(s)>20 else s

def get_cluster_state(state):
    s = state.lower() if state else state
    if s=='active':
        return green(state)
    elif s=='deleting':
        return red(state)
    else:
        return white(state)

def get_job_state(state):
    s = state.lower() if state else state
    if s=='running':
        return cyan(state)
    if s=='finished':
        return green(state)
    elif s=='waiting':
        return white(state)
    elif s=='failed':
        return red(state)
    elif s=='stopped':
        return yellow(state)
    else:
        return white(state)

def get_job_state_simple(state):
    s = state.lower() if state else state
    if s=='running':
        return 'R'
    if s=='finished':
        return 'C'
    elif s=='waiting':
        return 'W'
    elif s=='failed':
        return 'F'
    elif s=='stopped':
        return 'S'
    else:
        return state

def filter_list(arr, filters):
    '''
    fitlers:
       1. {State:['Running','Waiting']}
       2. {NumRunningInstance: {'>': 1}}
       3. {JobName: {'like':'jobName1'}}
       4. {JobName: {'startswith':'qsub-'}}
       5. {JobName: {'startswith':['qsub-user1-','qsub-user2-']}}
    '''
    t = arr

    for k in filters:

        if isinstance(filters[k], STRING):
            t = [item for item in t if filters[k].lower() == item.get(k).lower()]
        if isinstance(filters[k], (list,tuple)):
            alist = [ x.lower() for x in filters[k]]
            t = [item for item in t if (item.get(k) != None and item.get(k).lower() in alist )]
        if isinstance(filters[k], dict):

            startswith = filters[k].get('startswith')

            like = filters[k].get('like')


            gt = filters[k].get('>')
            lt = filters[k].get('<')

            if startswith != None:

                startswith = [startswith] if isinstance(startswith, STRING) else startswith
                startswith = map(lambda x:x.lower(), startswith)
                t2=[]
                for item in arr:
                    for ss in startswith:
                        if item.get(k).lower().startswith(ss):
                            t2.append(item)
                t=t2

            elif like != None:
                like = like.lower()
                t = [item for item in t if like in item.get(k).lower()]
            elif (gt != None or lt != None):
                t = [item for item in t
                     if (gt == None or gt != None and item.get(k) > gt) or (lt == None or lt != None and item.get(k) < lt)]
            else:
                t = arr
        arr = t
    return t

def order_by(arr, cols, desc=None):
    arr.sort(key=lambda x:[x[c] for c in cols], reverse=desc)
    return arr

def items2arr(items):
    t=[]
    for item in items:
        m = to_dict(item)
        t.append(m)
    return t

def sub(s, l=10):
    s = s or ''
    return ('%s...' % s[:l]) if len(s)>l else s


def format_date_in_arr(arr, cols):
    t=[]

    for n in arr:
        m = {}
        for k in n:
            m[k]=n[k]
        if 'StartTime' in cols and 'EndTime' in cols:
            m['Elapsed'] = calc_elapse(m.get('StartTime'), m.get('EndTime'))

        for k in cols:
            v = m.get(k)
            if v:
                m[k] = format_datetime(v)
                m['%sFromNow' % k] = from_now(v)
            else:
                m[k] = 'null'
        t.append(m)
    return t

def format_datetime(dt):
    if dt and isinstance(dt,datetime.datetime):
        dt = datetime.datetime.fromtimestamp(time.mktime(dt.timetuple()))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(dt, STRING):
        return format_date_str(dt)
    else:
        return dt or 'null'

def format_date_str(s):
    if not s:
        return s
    dt = datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    dt = datetime.datetime.fromtimestamp(calendar.timegm(dt.timetuple()))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def from_now(dt, detail=False):
    if not dt:
        return ''
    now = datetime.datetime.now()
    nt = int(calendar.timegm(now.timetuple()))

    # use calendar.timegm to correct timezone
    dt = datetime.datetime.fromtimestamp(calendar.timegm(dt.timetuple()))
    sec = time.mktime(dt.timetuple())

    sec = (nt-sec)
    return from_sec(sec)+' ago'

def from_sec(sec, detail=False):
    t = []
    if sec > 24 * 3600:
        d = int(sec / (24 * 3600))
        sec = sec - d * 24 * 3600
        t.append('%sD' % d)
        if not detail:
            return ''.join(t)
    if sec > 3600:
        h = int(sec / 3600)
        sec = sec - h * 3600
        t.append('%sH' % h)
        if not detail:
            return ''.join(t)
    if sec > 60:
        m = int(sec / 60)
        sec = sec - m * 60
        t.append('%sm' % m)
        if not detail:
            return ''.join(t)
    if sec > 0:
        t.append('%ss' % int(sec))
        if not detail:
            return ''.join(t)
    return ''.join(t)

def to_dict(item):
    m = {}
    for k in item.keys():
        m[k] = item.get(k)
    return m

def get_abs_path(location):

    if not location:
        return os.getcwd()

    elif location.startswith('/') or location.startswith('~') or re.match(r'^\w\:',location):
        return location
    else:
        return os.path.join(os.getcwd(), location)

def fix_log_path(s, jobId,taskName, instanceId, logType):
    if s!='' and s.endswith('.%s' % logType):
        return '%s/%s.%s.%s.%s' % ( s[0:s.rfind('/')] , logType, jobId,taskName, instanceId )
    else:
        return s

def calc_elapse(start, end):
    if start and end:
        sec = int(time.mktime(end.timetuple()) - time.mktime(start.timetuple()))
        return from_sec(sec, detail=True)
    else:
        return ''

def format_size(s):
    if s > (1024*1024*1024*1024):
        v = int(s/(1024*1024*1024*1024))
        return '%sTB' % v
    if s > 1024*1024*1024:
        v = int(s/(1024*1024*1024))
        return '%sGB' % v
    if s > 1024*1024:
        v = int(s/1024/1024)
        return '%sMB' % v
    if s > 1024:
        v = int(s/1024)
        return '%skB' % v
    return '%sB' % s

def hex_job_id(jobId):
    return '%s.console' % int('0x%s' % jobId[4:],16)

def get_job_id(hexId):
    ind = hexId.rfind('.')
    if ind!=-1:
        v = hexId[:ind]
    else:
        v = hexId
    s = (hex(int(v))[2:-1]).upper()
    return 'job-%s%s' % ('0'*(32-len(s)), s)



def trans_app_inputs_params(params):
    items = params.split(',')
    m = {}
    for item in items:
        # {name}:{type}:{localpath}:{desc}:{defaultValue}
        arr = item.split(':',4)

        m[arr[0]] = {
            'Type': arr[1] if len(arr)>1 and arr[1] else 'String',
            'LocalPath': arr[2] if len(arr) > 2 else '',
            'Description': arr[3] if len(arr) > 3 else '',
            'Default': arr[4] if len(arr) > 4 else '',
        }
    return m


def trans_app_outputs_params(params):
    items = params.split(',')
    m = {}
    for item in items:
        # {name}:{type}:{localpath}:{desc}
        arr = item.split(':',4)

        m[arr[0]] = {
            'Type': arr[1] if len(arr)>1 and arr[1] else 'String',
            'LocalPath': arr[2] if len(arr) > 2 else '',
            'Description': arr[3] if len(arr) > 3 else ''
        }
    return m

def trans_app_config_item(item, fn=None):
    arr = item.split(':')
    m = {
        'Default': (fn(arr[0]) if fn else arr[0]) if len(arr) > 0 else '',
        'Overwritable': bool(arr[1]) if len(arr) > 1 else False,
        'Description': arr[2] if len(arr) > 2 else '',
    }
    return m