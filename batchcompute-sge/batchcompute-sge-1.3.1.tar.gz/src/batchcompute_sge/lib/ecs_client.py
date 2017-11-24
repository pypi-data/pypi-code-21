
import bccluster_json
from aliyunsdkcore import client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest,DescribeInstanceTypesRequest
import json
from ..util.debugger import *

def _get_client(opt=None):
    opt = opt or bccluster_json.get()

    if not opt or not opt.get('access_key_id'):
        dprint('Not found access_key_id')
        raise Exception('You need to login first')

    dprint('client.AcsClient(%s,%s,%s)' % (opt.get('oxs_access_key_id') or opt.get('access_key_id'),
        opt.get('oxs_access_key_secret') or opt.get('access_key_secret'),
        opt.get('oxs_region') or opt.get('region')))

    c = client.AcsClient(
        opt.get('oxs_access_key_id') or opt.get('access_key_id'),
        opt.get('oxs_access_key_secret') or opt.get('access_key_secret'),
        opt.get('oxs_region') or opt.get('region'))
    return c


def get_sg_id_by_instance_id(id, opt):

    clt = _get_client(opt)

    #https://help.aliyun.com/document_detail/25506.html

    request = DescribeInstancesRequest.DescribeInstancesRequest()
    request.set_accept_format('json')
    request.set_InstanceIds(json.dumps([id]))

    try:
        raw_result = clt.do_action_with_exception(request)
    except Exception as e:
        dstack()
        raise e

    #{"PageNumber":1,"TotalCount":0,"PageSize":10,"RequestId":"D7E81F82-5794-4E2C-A7ED-43BFB0DB98D9","Instances":{"Instance":[]}}

    result = json.loads(raw_result)

    if 'Code' in result and 'Message' in result:
        raise Exception('%s: %s' % (result.get('Code'), result.get('Message')) )
    return result


def get_all_instance_types(opt):

    clt = _get_client(opt)

    #https://help.aliyun.com/document_detail/25506.html

    request = DescribeInstanceTypesRequest.DescribeInstanceTypesRequest()
    request.set_accept_format('json')

    try:
        raw_result = clt.do_action_with_exception(request)
    except Exception as e:
        dstack()
        raise e

    #{"PageNumber":1,"TotalCount":0,"PageSize":10,"RequestId":"D7E81F82-5794-4E2C-A7ED-43BFB0DB98D9","Instances":{"Instance":[]}}

    result = json.loads(raw_result)

    if 'Code' in result and 'Message' in result:
        raise Exception('%s: %s' % (result.get('Code'), result.get('Message')) )
    return result
