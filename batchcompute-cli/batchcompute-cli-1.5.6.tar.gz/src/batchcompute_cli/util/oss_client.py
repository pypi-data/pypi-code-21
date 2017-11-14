# -*- coding: utf-8 -*-

import oss2
from oss2 import determine_part_size,SizedFileAdapter
from oss2.models import PartInfo
from oss2.exceptions import NoSuchBucket, NoSuchKey
from requests.exceptions import StreamConsumedError

from ..util import config
import re
from ..const import WIN,PY2
from os.path import getsize

REG = r'^([\w\-]+)#oss:\/\/'

def __get_cfg():
    c = config.getConfigs(config.COMMON,['region','accesskeyid','accesskeysecret',
                                            'oss_region', 'oss_id', 'oss_key'])
    return {
        'region': c.get('oss_region') or c.get('region'),
        'accesskeyid':  c.get('oss_id') or c.get('accesskeyid') ,
        'accesskeysecret': c.get('oss_key') or c.get('accesskeysecret')
    }

def get_endpoint(region):
    return 'http://oss-%s.aliyuncs.com' % region


def check_client(cfg=None):

    cfg = cfg or __get_cfg()
    services = _get_service( cfg.get('oss_region') or cfg.get('region'),
                                  cfg.get('oss_id') or cfg.get('accesskeyid'),
                                  cfg.get('oss_key') or cfg.get('accesskeysecret'),
                             connect_timeout=3)

    try:
        services.list_buckets()
    except Exception as e:
        raise Exception(e.message)
    return 'ok'


def delete_file(oss_path):

    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())

    return bucket_tool.delete_object(key)

def download_file(oss_path, filename, progress_callback=None):

    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        filename = filename.encode('utf-8')
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())

    bucket_tool.get_object_to_file(key, filename, progress_callback=progress_callback)

def upload_file(filename, oss_path, progress_callback=None, use_put_object=False):

    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        filename = filename.encode('utf-8')
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, region or  config.get_oss_region())


    total_size = getsize(filename)

    # < 4GB
    if use_put_object or total_size < 4 * 1024 * 1024 * 1042:
        bucket_tool.put_object_from_file(key,filename,progress_callback=progress_callback)
    else:
        multi_upload_object_from_file(bucket_tool, key, filename,progress_callback)


def multi_upload_object_from_file(bucket_tool, key,filename, progress_callback):

    total_size = getsize(filename)

    part_size = determine_part_size(total_size, preferred_size = 100 * 1024)

    total_parts = round(total_size/part_size)

    print('multi_uploading, parts:%d'%total_parts)

    # 初始化分片
    upload_id = bucket_tool.init_multipart_upload(key).upload_id
    parts = []


    # 逐个上传分片
    with open(filename, 'rb') as fileobj:
        part_number = 1
        offset = 0
        while offset < total_size:

            num_to_upload = min(part_size, total_size - offset)

            result = bucket_tool.upload_part(key, upload_id, part_number,
                                        SizedFileAdapter(fileobj, num_to_upload),
                                 progress_callback= lambda a,b: progress_callback(offset, total_size))

            parts.append(PartInfo(part_number, result.etag))
            offset += num_to_upload
            part_number += 1

    # 完成分片上传
    bucket_tool.complete_multipart_upload(key, upload_id, parts)


def put_data(data, oss_path):

    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, config.get_oss_region())

    bucket_tool.put_object(key, data)


def get_data(oss_path, byte_range=None):
    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())
    try:
        a = bucket_tool.get_object(key, byte_range=byte_range).read()

        if isinstance(a, bytes):
            return a.decode(encoding='utf-8')
        else:
            return a
    except StreamConsumedError:
        return ''
    except Exception as e:
        raise e


def head_data(oss_path):
    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())
    try:
        return bucket_tool.head_object(key)
    except Exception as e:
        raise e


def list(oss_path, delimiter=""):

    (bucket, key, region) = parse_oss_path(oss_path)

    if WIN and PY2:
        key = key.encode('utf-8')

    bucket_tool = get_bucket_tool(bucket, region or config.get_oss_region())

    (obj_arr, pre_arr) = _list(bucket_tool, key, delimiter=delimiter)

    return (obj_arr, pre_arr, bucket_tool, region, bucket, key)

def _list(bucket_tool, key, marker='', delimiter=""):
    obj_arr = []
    pre_arr = []
    obj = bucket_tool.list_objects(key, delimiter=delimiter, marker=marker)

    obj_arr += obj.object_list
    pre_arr += obj.prefix_list

    if obj.next_marker:
        (v,v2) = _list(bucket_tool, key, obj.next_marker, delimiter=delimiter)
        obj_arr += v
        pre_arr += v2

    return (obj_arr, pre_arr)

def get_bucket_tool(bucket, region=None, connect_timeout=None):
    cfg = __get_cfg()

    return _get_bucket_tool(region or cfg['region'],
                             cfg['accesskeyid'],
                             cfg['accesskeysecret'],
                            bucket, connect_timeout=connect_timeout)

def _get_bucket_tool(region, id, key, bucket, connect_timeout=None):
    auth = oss2.Auth(id,key)
    endpoint = get_endpoint(region)
    bucket_tool = oss2.Bucket(auth, endpoint, bucket, connect_timeout=connect_timeout)
    return bucket_tool

def _get_service(region, id, key, connect_timeout=None):
    auth = oss2.Auth(id,key)
    endpoint = get_endpoint(region)
    service = oss2.Service(auth, endpoint, connect_timeout=connect_timeout)
    return service

def parse_oss_path(oss_path):
    '''
       parse oss path
       1. cn-qingdao#oss://bucket/key1    =>  (bucket, key1, cn-qingdao)
       2. oss://bucket/key1    =>  (bucket, key1, None)
    '''

    if not oss_path:
        raise NoSuchBucket('NoSuchBucket',{},'',{})

    matches = re.match(REG, oss_path)

    if matches:
        region = matches.groups()[0]
        s = oss_path[len(region)+len('#oss://'):]
    else:
        if not oss_path.startswith('oss://'):
            def_oss_path = config.get_oss_path()
            oss_path = def_oss_path + oss_path

        s = oss_path[len('oss://'):]
        region = None

    [bucket, key] = s.split('/',1)
    return (bucket, key, region)