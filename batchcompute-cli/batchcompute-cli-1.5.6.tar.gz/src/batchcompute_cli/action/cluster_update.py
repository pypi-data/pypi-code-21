
# -*- coding:utf-8 -*-

from ..util import client, result_cache,util
from terminal import confirm,green
import json

def update(clusterId, nodes=None, groupName='group', mount=None, image=None, user_data=None, env=None, yes=False,
           spot_price_limit=None,
           show_json=False):

    clusterId = result_cache.get(clusterId, 'clusters', True)

    desc = {}
    desc['Groups'] = {}
    groupName = result_cache.get(groupName, 'groups')
    desc['Groups'][groupName] = { }

    if nodes!=None and nodes>=0:
        v = int(nodes)
        desc['Groups'][groupName]["DesiredVMCount"]=v

    if spot_price_limit is not None:
        spot_price_limit = float(spot_price_limit)
        # if not resource_type == 'Spot':
        #     raise Exception('spot_price_limit works only if resource_type is Spot')

        if spot_price_limit > 0:
            desc['Groups'][groupName]['SpotPriceLimit'] = spot_price_limit
            desc['Groups'][groupName]['SpotStrategy'] = 'SpotWithPriceLimit'
        else:
            desc['Groups'][groupName]['SpotStrategy'] = 'SpotAsPriceGo'

    if image:
        desc['ImageId'] = image

    if user_data:
        desc['UserData'] = {}
        for item in user_data:
            desc['UserData'][item.get('key')] = item.get('value')

    if env:
        desc['EnvVars'] = {}
        for item in env:
            desc['EnvVars'][item.get('key')] = item.get('value')

    if mount:
        extend_mount(desc, mount)

    if show_json:
        print(json.dumps(desc, indent=4))
    else:

        if yes:
            client.update_cluster(clusterId, desc)
            print(green('done'))

        else:
            if confirm('Update cluster %s' % (clusterId), default=False):
                client.update_cluster(clusterId, desc)
                print(green('done'))


def extend_mount(desc, mount_m):
    for k, v in mount_m.items():
        if k.startswith('oss://') or k.startswith('nas://'):
            if not desc.get('Configs'):
                desc['Configs']={'Mounts':{"Entries":[]}}
            desc['Configs']['Mounts']['Entries'].append({
                "Destination": v,
                "Source": k,
                "WriteSupport": k.endswith('/')
            })

def trans_image(image):

    if not image.startswith('m-') and not image.startswith('img-'):
        raise Exception('Invalid imageId: %s' % image)
    return image

def trans_nodes(nodes):
    try:
        n = int(nodes)
        if n>=0:
            return n
        else:
            raise Exception('Invalid nodes: %s' % nodes)
    except:
        raise Exception('Invalid nodes: %s' % nodes)

def trans_mount(s):
    return util.trans_mount(s)


def trans_user_data(user_data):
    items = user_data.split(',')
    t = []
    for item in items:
        arr = item.split(':',1)
        t.append( {'key': arr[0], 'value': arr[1] if len(arr)==2 else ''} )
    return t

def trans_env(env):
    items = env.split(',')
    t = []
    for item in items:
        arr = item.split(':',1)
        t.append( {'key': arr[0], 'value': arr[1] if len(arr)==2 else ''} )
    return t

