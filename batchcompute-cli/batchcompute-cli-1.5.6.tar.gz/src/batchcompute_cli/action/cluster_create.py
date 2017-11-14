
# -*- coding:utf-8 -*-
from ..const import EVENTS
from ..util import client,util,config,formater
from terminal import green
import json


def create_cluster(clusterName, image=None, type=None, nodes=1, description='', user_data=None, env=None, disk=None,
                   notification_endpoint=None, notification_topic=None, notification_events=None,
                   mount=None, nas_access_group=None, nas_file_system=None, resource_type='OnDemand',
                    vpc_cidr_block=None, vpc_id=None, filePath=None,
                   no_cache_support=False,
                   spot_price_limit=None,
                   show_json=False):
    cluster_desc = {}

    if filePath:
        cluster_desc = getClusterJSON(filePath)

    else:

        image = config.get_default_image() if not image else image
        type = config.get_default_instance_type() if not type else type


        cluster_desc['Name'] = clusterName
        cluster_desc['ImageId'] = image
        cluster_desc['InstanceType'] = type
        cluster_desc['Description'] = description

        cluster_desc['Groups']={
            'group': {
                'InstanceType': type,
                'DesiredVMCount': nodes,
                'ResourceType': resource_type
            }
        }
        cluster_desc['Configs'] = {
            'Mounts': {
                'NAS':{}
            },
            'Disks': {}
            # 'Networks': {
            #     #"VPC": {}
            # }
        }
        if spot_price_limit is not None:
            spot_price_limit = float(spot_price_limit)
            if not resource_type == 'Spot':
                raise Exception('spot_price_limit works only if resource_type is Spot')

            if spot_price_limit > 0:
                cluster_desc['Groups']['group']['SpotPriceLimit'] = spot_price_limit
                cluster_desc['Groups']['group']['SpotStrategy'] = 'SpotWithPriceLimit'
            else:
                cluster_desc['Groups']['group']['SpotStrategy'] = 'SpotAsPriceGo'

        if user_data:
            cluster_desc['UserData'] = {}
            for item in user_data:
               cluster_desc['UserData'][item.get('key')]=item.get('value')
        if env:
            cluster_desc['EnvVars'] = {}
            for item in env:
                cluster_desc['EnvVars'][item.get('key')] = item.get('value')

        if disk:
            cluster_desc['Configs']['Disks']=disk


        if mount:
            extend_mount(cluster_desc, mount)

        if nas_access_group:
            cluster_desc['Configs']['Mounts']['NAS']['AccessGroup'] = nas_access_group.split(',')
        if nas_file_system:
            cluster_desc['Configs']['Mounts']['NAS']['FileSystem'] = nas_file_system.split(',')

        if no_cache_support:
            cluster_desc['Configs']['Mounts']['CacheSupport'] = not no_cache_support


         # notification
        cluster_desc['Notification']={'Topic':{}}

        if notification_endpoint:
            cluster_desc['Notification']['Topic']['Endpoint'] = notification_endpoint
        if notification_topic:
            cluster_desc['Notification']['Topic']['Name'] = notification_topic
        if notification_events:
            cluster_desc['Notification']['Topic']['Events'] = notification_events

        # vpc
        vpc_cidr_block = vpc_cidr_block if vpc_cidr_block else config.getConfigs(config.COMMON, ['vpc_cidr_block']).get('vpc_cidr_block')

        if vpc_cidr_block:
            if not cluster_desc['Configs'].get('Networks'):
                cluster_desc['Configs']['Networks']={}
            if not cluster_desc['Configs']['Networks'].get('VPC'):
                cluster_desc['Configs']['Networks']['VPC']={}
            cluster_desc['Configs']['Networks']['VPC']['CidrBlock']=vpc_cidr_block


        if vpc_id:
            if not vpc_cidr_block:
                raise Exception('vpc_id must works with vpc_cidr_block')

            if not cluster_desc['Configs'].get('Networks'):
                cluster_desc['Configs']['Networks']={}
            if not cluster_desc['Configs']['Networks'].get('VPC'):
                cluster_desc['Configs']['Networks']['VPC']={}
            cluster_desc['Configs']['Networks']['VPC']['VpcId']=vpc_id

    if show_json:
        print(json.dumps(cluster_desc, indent=4))
    else:
        result = client.create_cluster(cluster_desc)

        if result.StatusCode==201:
            print(green('Cluster created: %s' % result.Id))

def getClusterJSON(filePath):
    filePath= formater.get_abs_path(filePath)
    s = ''
    with open(filePath) as f:
        s = json.loads(f.read())
    return s
def trans_mount(s):
    return util.trans_mount(s)


def extend_mount(desc, mount_m):
    desc['Configs']['Mounts']['Entries'] = []
    for k, v in mount_m.items():
        if k.startswith('oss://') or k.startswith('nas://'):
            desc['Configs']['Mounts']['Entries'].append({
                "Destination": v,
                "Source": k,
                "WriteSupport": k.endswith('/')
            })

def trans_image(image):

    if not image.startswith('m-') and not image.startswith('img-'):
        raise Exception('Invalid imageId: %s' % image)
    return image

def trans_notification_events(events):

    arr = events.split(',')
    for n in arr:
        if n not in EVENTS.get('CLUSTER'):
            raise Exception('Invalid cluster event: %s\n  Type "bcs e" for more' % n)

    return arr

def trans_nodes(n):
    try:
        n = int(n)
        return n if n >= 0 else 0
    except:
        return 0


def trans_user_data(user_data):
    items = user_data.split(',')
    t = []
    for item in items:
        if item.strip() == '':
            continue
        arr = item.split(':',1)
        t.append({'key': arr[0].strip(), 'value': arr[1].strip() if len(arr) == 2 else ''})
    return t

def trans_env(env):
    items = env.split(',')
    t = []
    for item in items:
        if item.strip() == '':
            continue
        arr = item.split(':',1)
        t.append( {'key': arr[0].strip(), 'value': arr[1].strip() if len(arr)==2 else ''} )
    return t

def trans_disk(disk):
    return util.trans_disk(disk)

