from ..util import client,config as _config ,oss_client, formater, list2table, result_cache
from terminal import bold, magenta, white, blue, green,red, yellow
from ..const import CMD
import json
import uuid
import os
import re

def asub(app_name, job_name=None, description=None,
           resource_type=None, type=None, nodes=None, min_disk_size=None, disk_type=None,
           max_retry_count=None, timeout=None,
           config={},
           show_json=False, **io_opt):

    pre_oss_path = _config.get_oss_path()
    rand = gen_rand_id()

    (app_desc, app_name_p) = get_app(app_name)


    # inputs = {}
    # for k in app_desc.get('InputParameters'):
    #     inputs[k]=''
    #
    # outputs = {}
    # for k in app_desc.get('OutputParameters'):
    #     outputs[k] = ''

    desc = {
        'Name': job_name or 'app-job',
        'Description': description or '',
        'Type': 'App',
        'App': {
            'AppName': app_name_p,
            'Inputs': {},
            'Outputs':{},
            'Logging': {
                'StdoutPath': '%s%s/logs/' % (pre_oss_path,rand),
                'StderrPath': '%s%s/logs/' % (pre_oss_path,rand)
            },
            'Config': config
        }
    }


    for k,v in io_opt.items():
        if k.startswith('input_from_file_'):
            k = k[16:]
            desc['App']['Inputs'][k] = deal_with_value(v, pre_oss_path,rand, dir_name='input',
                                                       uploadable=not show_json, upload=True)
        elif k.startswith('input_'):
            k = k[6:]
            desc['App']['Inputs'][k] = deal_with_value(v, pre_oss_path, rand, dir_name='input',
                                                       uploadable=not show_json)
        elif k.startswith('i'):
            k = k[1:]
            desc['App']['Inputs'][k] = deal_with_value(v, pre_oss_path, rand, dir_name='input',
                                                       uploadable=not show_json)

        elif k.startswith('output_'):
            k = k[7:]
            desc['App']['Outputs'][k] = deal_with_value(v, pre_oss_path, rand, dir_name='output',
                                                       uploadable=not show_json)
        elif k.startswith('o'):
            k = k[1:]
            desc['App']['Outputs'][k] = deal_with_value(v, pre_oss_path, rand, dir_name='output',
                                                        uploadable=not show_json)

    ########
    if resource_type:
        desc['App']['Config']['ResourceType'] = resource_type
    if type:
        desc['App']['Config']['InstanceType'] = type
    if nodes!=None:
        desc['App']['Config']['InstanceCounts'] = int(nodes)
    if min_disk_size!=None:
        desc['App']['Config']['MinDiskSize'] = int(min_disk_size)
    if disk_type:
        desc['App']['Config']['DiskType'] = disk_type
    if max_retry_count!=None:
        desc['App']['Config']['MaxRetryCount'] = int(max_retry_count)
    if timeout!=None:
        desc['App']['Config']['Timeout'] = int(timeout)


    if show_json:
        print(json.dumps(desc, indent=4))
    else:
        result = client.create_job(desc)

        if result.StatusCode == 201:
            print(green('Job created: %s' % result.Id))

def get_app(app_name):

    if app_name.startswith(':'):
        app_name= app_name[1:]
        try:
            info = client.get_app(app_name, 'Public')
            return (info, ':%s' % app_name)
        except:
            info = client.get_app(app_name, 'Private')
            return (info, app_name)
    else:
        try:
            info = client.get_app(app_name, 'Private')
            return (info, app_name)
        except:
            info = client.get_app(app_name, 'Public')
            return (info, ':%s' % app_name)


def deal_with_value(v, pre_oss_path,rand, dir_name, uploadable=False, upload=False):

    if v.endswith('//:oss') or upload:
        # upload and gen path
        if v.endswith('//:oss'):
           v = v[:-6]

        s = _get_basename(v)
        oss_path = '%s%s/%s/%s' % (pre_oss_path, rand, dir_name,  s )

        if upload and not os.path.isfile(v):
            raise Exception('Not found locale file: %s' % v)

        if uploadable and os.path.isfile(v):
            # upload
            print('Upload: %s ==> %s' % (v, oss_path))
            oss_client.upload_file(v, oss_path)

        return oss_path
    else:
        return v

def _get_basename(v):
    if v.endswith('/'):
        return '%s/' % os.path.basename(v[:-1])
    else:
        return os.path.basename(v)

# a:1,b:2, or   a=1,b=2
def trans_config(str):

    items = str.split(',')

    m = {}
    for item in items:
        # a:1
        arr = re.split(r'=|:', item, 1)
        #arr = item.split(':', 1)
        k = arr[0]
        v = arr[1] if len(arr)==2 else ''

        m[k] = v
    return m

def gen_rand_id():
    return uuid.uuid1()

