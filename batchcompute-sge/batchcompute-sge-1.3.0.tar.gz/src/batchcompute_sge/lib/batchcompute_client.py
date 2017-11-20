from batchcompute import Client
import bccluster_json

from ..util.debugger import *
from . import it_config

def _get_endpoint(region, port=None):
    domain = 'batchcompute.%s.aliyuncs.com' % region
    if port:
        Client.register_region(region, domain, int(port))
    else:
        Client.register_region(region, domain)
    return domain


def _get_client(opt=None):
    opt = opt or bccluster_json.get()

    if not opt or not opt.get('access_key_id'):
        raise Exception('You need to login first')

    endpoint = _get_endpoint(opt.get('region'), opt.get('bcs_port'))

    dprint('batchcompute.Client(%s,%s,%s)' % (endpoint, opt.get('access_key_id'), opt.get('access_key_secret')))

    c = Client(endpoint, opt.get('access_key_id'), opt.get('access_key_secret'))

    return c


def check_client(opt):
    client = _get_client(opt)
    client.list_images('',1)



def list_images():
    client = _get_client()

    sysArr = __list_images(client,'',100,type_='System')
    arr = __list_images(client)
    return {'Items': sysArr + arr,'Marker':''}



def list_instance_types():
    quotas = get_quotas()
    arr = quotas.AvailableClusterInstanceType

    itmap = it_config.get()

    t=[]
    for n in arr:
        t.append( itmap[n] if itmap.get(n) else {'name':str(n),'cpu': '','memory':''} )
    t = order_by(t, ['cpu','memory'],False)
    return t


def list_cluster_instances(cluster_id, group_name):
    client = _get_client()

    arr = __list_cluster_instances(client, cluster_id, group_name, '', 100)
    return {'Items': arr, 'Marker': ''}


def get_cluster(cluster_id):
    client = _get_client()
    return client.get_cluster(cluster_id)


def update_cluster_vm_count(cluster_id, groupName, vmCount):
    client = _get_client()
    return client.change_cluster_desired_vm_count(cluster_id, **{groupName:vmCount})

def create_cluster(clusterDesc):
    client = _get_client()
    return client.create_cluster(clusterDesc)


def delete_cluster(id):
    client = _get_client()
    return client.delete_cluster(id)


#############################################################

def order_by(arr, cols, desc=None):
    arr.sort(key=lambda x:[x[c] for c in cols], reverse=desc)
    return arr


def get_quotas():
    client = _get_client()
    return client.get_quotas()


def __list_images(client, marker='', maxItemCount=100, type_=''):
    t = []
    result = client.list_images(marker, maxItemCount, type_)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_images(client,result.NextMarker,maxItemCount,type_)
        t = t + arr
    return t



def __list_cluster_instances(client, cluster_id, group_name, marker='', maxItemCount=100):
    t = []
    result = client.list_cluster_instances(cluster_id, group_name, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_cluster_instances(client, cluster_id, group_name, result.NextMarker, maxItemCount)
        t = t + arr
    return t

def __items2list(items):
    t=[]
    for item in items:
        m = {}
        for k in item.keys():
            m[k] = item.get(k)
        t.append(m)
    return t
